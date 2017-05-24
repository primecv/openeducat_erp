# -*- coding: utf-8 -*-

import babel.dates
import time
import re
import werkzeug.urls
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from openerp import http
from openerp import tools, SUPERUSER_ID
from openerp.addons.website.models.website import slug
from openerp.http import request
from openerp.tools.translate import _


class website_ems(http.Controller):
    @http.route(['/student', '/student/page/<int:page>', '/students', '/students/page/<int:page>'], type='http', auth="public", website=True)
    def students(self, page=1, **searches):
        cr, uid, context = request.cr, request.uid, request.context
        student_obj = request.registry['ems.student']
        university_center_obj = request.registry['ems.university.center']
        course_obj = request.registry['ems.course']

        searches.setdefault('university_center', 'all')
        searches.setdefault('course', 'all')

        domain_search = {}

        # search domains
        # TDE note: WTF ???
        current_university_center = None
        current_course = None

        if searches["course"] != 'all':
            current_course = course_obj.browse(cr, uid, int(searches['course']), context=context)
            domain_search["course"] = [("course_id", "=", int(searches["course"]))]

        if searches["university_center"] != 'all':
            current_university_center = university_center_obj.browse(cr, uid, int(searches['university_center']), context=context)
            domain_search["university_center"] = [("university_center_id", "=", int(searches["university_center"]))]


        def dom_without(without):
            domain = [('active', "=", True)]
            for key, search in domain_search.items():
                if key != without:
                    domain += search
            return domain

        # count by domains without self search

        domain = dom_without('university_center')
        university_centers = student_obj.read_group(
            request.cr, request.uid, domain, ["id", "university_center_id"], groupby="university_center_id",
            orderby="university_center_id", context=request.context)
        university_center_count = student_obj.search(request.cr, request.uid, domain,
                                      count=True, context=request.context)
        university_centers.insert(0, {
            'university_center_id_count': university_center_count,
            'university_center_id': ("all", _("All Centers"))
        })

        domain = dom_without('course')
        courses = student_obj.read_group(
            request.cr, request.uid, domain, ["id", "course_id"],
            groupby="course_id", orderby="course_id", context=request.context)
        course_id_count = student_obj.search(request.cr, request.uid, domain,
                                            count=True, context=request.context)
        courses.insert(0, {
            'course_id_count': course_id_count,
            'course_id': ("all", _("All Courses"))
        })
        print "DOMAIN::::::::::::::::::::::::::::"
        print domain

        step = 10  # Number of students per page
        student_count = student_obj.search(
            request.cr, request.uid, dom_without("none"), count=True,
            context=request.context)
        pager = request.website.pager(
            url="/student",
            url_args={'university_center': searches.get('university_center'), 'course': searches.get('course')},
            total=student_count,
            page=page,
            step=step,
            scope=5)

        order = 'website_published desc, roll_number desc'
        obj_ids = student_obj.search(
            request.cr, request.uid, dom_without("none"), limit=step,
            offset=pager['offset'], order=order, context=request.context)
        students_ids = student_obj.browse(request.cr, request.uid, obj_ids,
                                      context=request.context)

        values = {
            'current_course': current_course,
            'current_university_center': current_university_center,
            'student_ids': students_ids,
            'university_centers': university_centers,
            'courses': courses,
            'pager': pager,
            'searches': searches,
            'search_path': "?%s" % werkzeug.url_encode(searches),
        }

        return request.website.render("website_ems.index", values)

    @http.route(['/student/<model("ems.student"):student>/page/<path:page>'], type='http', auth="public", website=True)
    def student_page(self, student, page, **post):
        values = {
            'student': student,
            'main_object': student
        }

        if '.' not in page:
            page = 'website_ems.%s' % page

        print "PAGE:::::::::::::::::::::::::::::::::::::::::::::::::::"
        print page
        try:
            request.website.get_template(page)
        except ValueError:
            # page not found
            values['path'] = re.sub(r"^website_ems\.", '', page)
            values['from_template'] = 'website_ems.default_page'  # .strip('website_ems.')
            page = 'website.page_404'

        return request.website.render(page, values)

    @http.route(['/student/<model("ems.student"):student>'], type='http', auth="public", website=True)
    def student(self, student, **post):
        if student.menu_id and student.menu_id.child_id:
            target_url = student.menu_id.child_id[0].url
        else:
            target_url = '/student/%s/register' % str(student.id)
        if post.get('enable_editor') == '1':
            target_url += '?enable_editor=1'
        print "TARGET::::::::::::::::::::::::::::::::::::::"
        print target_url
        return request.redirect(target_url)

    @http.route(['/student/<model("ems.student"):student>/register'], type='http', auth="public", website=True)
    def student_register(self, student, **post):
        values = {
            'student': student,
            'main_object': student,
            'range': range,
        }
        print "VALUES::::::::::::::::::::::::::::::::::::::"
        print values
        return request.website.render("website_ems.student_description_full", values)

    @http.route(['/student/<model("ems.student"):student>/classes'], type='http', auth="public", website=True)
    def student_classes(self, student, **post):
        cr, uid, context = request.cr, request.uid, request.context
        class_obj = request.registry['ems.class.enrollment']
        order = 'class_id desc'
        obj_ids = class_obj.search(
            request.cr, request.uid, [('student_id', "=", student.id)],
            order=order, context=request.context)
        class_ids = class_obj.browse(request.cr, request.uid, obj_ids,
                                      context=request.context)

        values = {
            'class_ids': class_ids,
            'student': student,
            'main_object': student,
            'range': range,
        }
        print "VALUES2::::::::::::::::::::::::::::::::::::::"
        print values
        return request.website.render("website_ems.student_classes", values)

    @http.route(['/student/<model("ems.student"):student>/grades'], type='http', auth="public", website=True)
    def student_grades(self, student, **post):
        cr, uid, context = request.cr, request.uid, request.context
        grade_obj = request.registry['ems.enrollment.inscription.subject']
        order = 'academic_year desc,course_year,semester'
        obj_ids = grade_obj.search(
            request.cr, request.uid, [('student_id', "=", student.id)],
            order=order, context=request.context)
        grades_ids = grade_obj.browse(request.cr, request.uid, obj_ids,
                                      context=request.context)

        values = {
            'grades_ids': grades_ids,
            'student': student,
            'main_object': student,
            'range': range,
        }
        print "VALUES2::::::::::::::::::::::::::::::::::::::"
        print values
        return request.website.render("website_ems.student_grades", values)
