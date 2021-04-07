from datetime import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView
from django_tables2 import RequestConfig, SingleTableView
from django.contrib.auth.models import Group
from django.db import connection
from django.db.models import Q

from journal.views import mainView

from .forms import reportListOfJournalsForm, contactTeacherForm, contactStudentForm
from .models import teacher, material, discipline, student
from .tables import TeacherContactTable, StudentContactTable


class viewReportManager(LoginRequiredMixin, ListView):

    @login_required
    def journal_manager_main(request, *args, **kwargs):
        if request.user.is_staff or Group.objects.get(
                name='course_teacher') in request.user.groups.all() or Group.objects.get(
            name='curator') in request.user.groups.all():
            data = mainView.get_data_main(request, *args, **kwargs)
            d_left, d_right = mainView.determine_date_study(request)
            if request.method == 'POST':
                teacher_id = request.POST['teacher']
                try:
                    instance = teacher.objects.filter(pk=teacher_id)
                    form = reportListOfJournalsForm(request.POST, instance=instance.first())

                    format_d = datetime.today().strftime('%Y-%m-%d')
                    discip_qs = discipline.objects.filter(teachIdToDiscip=teacher_id).order_by('dayofWeekStartLecture',
                                                                                               'timeStartLecture')
                    discip_qs = discip_qs.extra(where=[f"dateStart>='{d_left}' and dateFinish<'{d_right}'"])
                    data['disciplines_for_manager'] = discip_qs

                except ValueError:
                    form = reportListOfJournalsForm()
            else:
                data['disciplines_for_manager'] = None
                form = reportListOfJournalsForm()

            data['d_left'] = datetime.strptime(d_left, '%Y%m%d')
            data['d_right'] = datetime.strptime(d_right, '%Y%m%d')
            data['form'] = form
            return render(request, 'journal/report_journal_manager.html', context=data)
        else:
            raise Http404

    @login_required
    def contact_teacher(request, *args, **kwargs):
        if request.user.is_staff or Group.objects.get(
                name='course_teacher') in request.user.groups.all() or Group.objects.get(
            name='curator') in request.user.groups.all():
            data = mainView.get_data_main(request, *args, **kwargs)

            form_table = TeacherContactTable(
                teacher.objects.all().filter(Q(userTechId_id__is_active=1) & (Q(dateFinishTeach__gte=datetime.today()) | Q(dateFinishTeach__isnull=True))).order_by('lastName'))

            data['form_table'] = form_table
            return render(request, 'journal/table_contacts.html', context=data)
        else:
            raise Http404

    @login_required
    def contact_student(request, *args, **kwargs):
        if request.user.is_staff or Group.objects.get(
                name='course_teacher') in request.user.groups.all() or Group.objects.get(
            name='curator') in request.user.groups.all():
            data = mainView.get_data_main(request, *args, **kwargs)
            d_left, d_right = mainView.make_semestr_dates(request)

            form_table = StudentContactTable(
                student.objects.all().filter(isOn=1).order_by('lastName', 'course', 'depStudId', 'paid'))

            data['form_table'] = form_table
            return render(request, 'journal/table_contacts.html', context=data)
        else:
            raise Http404

    @login_required
    def workload(request, *args, **kwargs):
        if request.user.is_staff or Group.objects.get(
                name='course_teacher') in request.user.groups.all() or Group.objects.get(
            name='curator') in request.user.groups.all() or Group.objects.get(
            name='teacher') in request.user.groups.all():
            data = mainView.get_data_main(request, *args, **kwargs)
            d_left, d_right = mainView.determine_date_study(request)

            def select_data(teacher_id, d_left, d_right):
                # with connection.cursor() as cursor:
                cursor = connection.cursor()
                cursor.execute(

                    # qs = material.objects.raw(
                    "SELECT "
                    # "    1 as id , "  
                    "    date_format( data_table.dateInit, '%%Y-%%m' ) as d, "
                    "    data_table.paid_discip, "
                    "    SUM( data_table.countHour ) AS 'sum_h' "
                    "FROM "
                    "    ( "
                    "    SELECT "
                    "        journal_material.id, "
                    "        journal_material.dateInit, "
                    "        journal_material.countHour, "
                    "        journal_discipline.paid_discip, "
                    "        journal_position.positionName, "
                    "        journal_teacher.lastName, "
                    "        journal_teacher.firstName"
                    "    FROM"
                    "        `u0865207_journal_amumgk`.`journal_material` "
                    "        JOIN journal_teacher ON journal_teacher.id = journal_material.teachIdToMaterial_id "
                    "        JOIN journal_discipline ON journal_discipline.id = journal_material.discipMaterialId_id "
                    "        JOIN journal_position ON journal_position.id = journal_teacher.positionId_id "
                    "    WHERE"
                    "        journal_material.teachIdToMaterial_id = %s "
                    "        AND journal_material.isCount = 1 "
                    "        AND journal_material.dateInit >= %s "
                    "        AND journal_material.dateInit < %s "
                    "    ORDER BY "
                    "        journal_material.dateInit "
                    "    ) AS data_table "
                    "GROUP BY "
                    "    d, "
                    "    data_table.paid_discip "
                    "ORDER BY "
                    "    d, "
                    "    data_table.paid_discip ",
                    [teacher_id, d_left, d_right])
                return cursor.fetchall()

            if request.method == 'POST':
                teacher_id = request.POST['teacher']
                try:
                    instance = teacher.objects.filter(pk=teacher_id)
                    form = reportListOfJournalsForm(request.POST, instance=instance.first())

                    data['table_workload'] = select_data(teacher_id, d_left, d_right)
                except ValueError:
                    form = reportListOfJournalsForm()
            else:
                data['table_workload'] = select_data(data['userData'].id, d_left, d_right)
                form = reportListOfJournalsForm()

            data['d_left'] = d_left
            data['d_right'] = d_right
            data['form'] = form
            return render(request, 'journal/report_workload.html', context=data)
        else:
            raise Http404

    @login_required
    def workload_all(request, *args, **kwargs):
        if request.user.is_staff or Group.objects.get(
                name='course_teacher') in request.user.groups.all() or Group.objects.get(
            name='curator') in request.user.groups.all():
            data = mainView.get_data_main(request, *args, **kwargs)
            d_left, d_right = mainView.determine_date_study(request)

            def select_data(d_left, d_right):
                # with connection.cursor() as cursor:
                cursor = connection.cursor()
                cursor.execute(

                    # qs = material.objects.raw(
                    "SELECT "
                    "    data_table.teach_id, "  
                    "    data_table.teach, "  
                    "    data_table.nameDep, "  
                    "    date_format( data_table.dateInit, '%%Y-%%m' ) as d, "
                    "    data_table.paid_discip, "
                    "    SUM( data_table.countHour ) AS 'sum_h', "
                    "    data_table.dep_id "
                    "FROM "
                    "    ( "
                    "    SELECT "
                    "        journal_material.id, "
                    "        journal_material.dateInit, "
                    "        journal_material.countHour, "
                    "        journal_discipline.paid_discip, "
                    "        journal_position.positionName, "
                    "        CONCAT(journal_teacher.lastName, ' ',journal_teacher.firstName, ' ',journal_teacher.partonymic ) as 'teach', "
                    "        journal_teacher.id  as 'teach_id', "
                    "        journal_departament.order_by, "
                    "        journal_departament.nameDep, "
                    "        journal_departament.id as 'dep_id'"
                    "    FROM"
                    "        journal_teacher "
                    "        LEFT JOIN journal_material ON journal_teacher.id = journal_material.teachIdToMaterial_id "
                    "        LEFT JOIN journal_discipline ON journal_discipline.id = journal_material.discipMaterialId_id "
                    "        JOIN journal_position ON journal_position.id = journal_teacher.positionId_id "
                    "        JOIN journal_departament ON journal_departament.id = journal_teacher.depTeachId_id "
                    "    WHERE"
                    "        ((journal_material.discipMaterialId_id OR journal_material.teachIdToMaterial_id is NULL) OR "
                    "        (journal_material.isCount = 1 "
                    "        AND journal_material.dateInit >= %s "
                    "        AND journal_material.dateInit < %s ) ) AND (journal_teacher.dateFinishTeach >= now()  OR journal_teacher.dateFinishTeach is NULL)"
                    "    ORDER BY "
                    "        journal_material.dateInit "
                    "    ) AS data_table "
                    "GROUP BY "
                    "    data_table.order_by, "
                    "    data_table.teach, "
                    "    d, "
                    "    data_table.paid_discip "
                    "ORDER BY "
                    "    data_table.order_by, "
                    "    data_table.teach, "
                    "    d, "
                    "    data_table.paid_discip ",
                    [d_left, d_right])
                return cursor.fetchall()


            data['table_workload'] = select_data(d_left, d_right)
            form = reportListOfJournalsForm()

            data['d_left'] = d_left
            data['d_right'] = d_right
            data['form'] = form
            return render(request, 'journal/report_workload_all.html', context=data)
        else:
            raise Http404


    @login_required
    def schedule_teacher(request, *args, **kwargs):
        if request.user.is_staff or Group.objects.get(
                name='course_teacher') in request.user.groups.all() or Group.objects.get(
            name='curator') in request.user.groups.all():
            data = mainView.get_data_main(request, *args, **kwargs)
            d_left_semestr, d_right_semestr = mainView.make_semestr_dates(request)
            d_left_year, d_right_year = mainView.determine_date_study(request)

            if request.method == 'POST':
                teacher_id = request.POST['teacher']

                if 'paid' in request.POST and request.POST['paid'] == 'on':
                    paid = 1
                else:
                    paid = 0

                try:
                    teacher_int = int(teacher_id)
                    instance = teacher.objects.filter(pk=teacher_int)
                    form = reportListOfJournalsForm(request.POST, instance=instance.first())
                    qs = student.objects.raw(
                        "SELECT "
                        "journal_teacher.id , "
                        "journal_discipline.dayofWeekStartLecture, "
                        "journal_discipline.timeStartLecture, "
                        "journal_discipline.timeFinishLecture, "
                        "journal_discipline.nameDiscipline, "
                        "journal_teacher.firstName  AS 'teacher_firstName', "
                        "journal_teacher.lastName AS 'teacher_lastName', "
                        "journal_teacher.partonymic AS 'teacher_partonymic' ,"
                        "journal_item.itemName "
                        "FROM "
                        "journal_teacher "
                        "INNER JOIN journal_discipline ON journal_discipline.teachIdToDiscip_id = journal_teacher.id "
                        "INNER JOIN journal_position ON journal_position.id = journal_teacher.positionId_id "
                        "INNER JOIN journal_item ON journal_item.id = journal_discipline.itemIdToDiscip_id  "
                        
                        "WHERE "
                        "`journal_teacher`.id = %s "
                        "AND journal_discipline.paid_discip = %s "
                        "AND journal_discipline.isOn = 1 "
                        "AND ((journal_discipline.dateStart >= %s AND journal_discipline.dateFinish <= %s) OR "
                        " (journal_discipline.dateStart >= %s AND journal_discipline.dateFinish < %s)) "
                        "ORDER BY "
                        "journal_discipline.dayofWeekStartLecture, journal_discipline.timeStartLecture ASC",
                        [teacher_id, paid, d_left_semestr, d_right_semestr, d_left_year, d_right_year])

                    data['report_schedule'] = qs
                except ValueError:
                    form = reportListOfJournalsForm()
            else:
                form = reportListOfJournalsForm()

            data['teacher_name'] = form.instance
            data['d_left'] = d_left_semestr
            data['d_right'] = d_right_semestr
            data['form'] = form
            return render(request, 'journal/report_schedule.html', context=data)
        else:
            raise Http404
