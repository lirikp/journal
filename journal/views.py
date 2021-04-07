import datetime
import time
import re

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

from datetime import timedelta

from .forms import disciplineChoiceForTeacher, materialForm, scoreForm, reportScheduleForm, reportScorecardForm, \
    reportKtpForm, reportStudentAllItemsWithYearForm
from .models import material, student, teacher, discipline, typeOfMeet, score, cronMysql


# from .tables import MaterialTable


class mainView(LoginRequiredMixin, ListView):
    LoginRequiredMixin.login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def is_member_student(user):
        return user.groups.filter(name='student').exists()

    def is_member_teacher(user):
        return user.groups.filter(name='teacher').exists()

    @login_required
    def main_list(request, *args, **kwargs):

        if request.user.groups.filter(name='student').exists():
            return HttpResponseRedirect(reverse('students:student_detail', ))
        elif request.user.groups.filter(name='teacher').exists():

            data = mainView.get_data_main(request, *args, **kwargs)

            # if 'discipline_detail_id' in data:
            #     return HttpResponseRedirect(
            #         reverse('discipline:discipline_detail', args=(data['discipline_detail_id'],)))
            # else:
            #
            return render(request, 'journal/first_page.html', context=data)
        else:
            raise Http404

    @login_required
    @user_passes_test(is_member_teacher)
    def discipline_detail(request, *args, **kwargs):
        data = mainView.get_data_discipline(request, *args, **kwargs)

        return render(request, 'journal/main.html', context=data)

    @login_required
    @user_passes_test(is_member_student)
    def student(request, *args, **kwargs):
        data = {}  # mainView.__get_data_discipline(request, *args, **kwargs)
        userData = student.objects.filter(userStudId=request.user.id).get()
        d_left, d_right = mainView.make_semestr_dates(request)

        qs = student.objects.raw(
            "SELECT "
            "journal_student.id, "
            "journal_student.lastName, "
            "journal_student.firstName, "
            "journal_student.course, "
            "journal_material.dateInit, "
            "journal_discipline.id AS 'discipline.id', "
            "journal_discipline.nameDiscipline, "
            "journal_material.id AS 'material.id', "
            "journal_material.meetId_id AS 'meetId', "
            "journal_teacher.id AS 'teacher.id', "
            "journal_teacher.firstName AS 'prep_firstName', "
            "journal_teacher.lastName AS 'prep_lastName', "
            "journal_teacher.partonymic AS 'prep_partonymic', "
            "journal_score.descriptionScore, "
            "journal_score.result "
            "FROM "
            "journal_student "
            "INNER JOIN journal_listofstudfordiscipline ON journal_listofstudfordiscipline.studId_id = journal_student.id "
            "INNER JOIN journal_discipline ON journal_discipline.id = `journal_listofstudfordiscipline`.`discipListId_id` "
            "INNER JOIN journal_material ON journal_discipline.id = `journal_material`.discipMaterialId_id "
            "INNER JOIN journal_teacher ON journal_teacher.id = journal_discipline.teachIdToDiscip_id "
            "LEFT JOIN `journal_score` ON ( journal_score.disciplineId_id = journal_discipline.id ) "
            "AND ( journal_score.materialId_id = journal_material.id ) "
            "AND ( journal_score.studentId_id = journal_student.id ) "
            "AND ( journal_score.teachIdToScore_id = journal_teacher.id ) "
            "WHERE "
            "`journal_student`.`isOn` = 1 "
            "AND `journal_student`.id = %s "
            "AND journal_score.result IS NOT NULL "
            "AND journal_score.dateIn BETWEEN %s AND %s "
            "ORDER BY "
            "journal_student.id, "
            "journal_material.dateInit ASC ",
            [userData.id, d_left, d_right])
        data['report_student_all_items_with_year'] = qs
        qs = student.objects.raw(
            "SELECT "
            "journal_student.id, "
            "journal_student.lastName, "
            "journal_student.firstName, "
            "journal_discipline.dayofWeekStartLecture, "
            "journal_discipline.timeStartLecture, "
            "journal_discipline.timeFinishLecture, "
            "journal_discipline.nameDiscipline, "
            "journal_teacher.firstName  AS 'teacher_firstName', "
            "journal_teacher.lastName AS 'teacher_lastName', "
            "journal_teacher.partonymic AS 'teacher_partonymic' "
            "FROM "
            "journal_student "
            "INNER JOIN journal_listofstudfordiscipline ON journal_listofstudfordiscipline.studId_id = journal_student.id "
            "INNER JOIN journal_discipline ON journal_discipline.id = `journal_listofstudfordiscipline`.`discipListId_id` "
            "INNER JOIN journal_teacher ON journal_teacher.id = journal_discipline.teachIdToDiscip_id "
            "INNER JOIN journal_position ON journal_position.id = journal_teacher.positionId_id "
            "WHERE "
            "`journal_student`.id = %s "
            "AND journal_position.id != 2 "
            "AND journal_discipline.dayofWeekStartLecture != 8 "
            "AND journal_discipline.dateStart >= %s "
            "AND journal_discipline.dateFinish <= %s "
            "ORDER BY "
            "journal_discipline.dayofWeekStartLecture ASC",
            [userData.id, d_left, d_right])

        data['report_schedule'] = qs

        qs_8 = student.objects.raw(
            "SELECT "
            "journal_student.id, "
            "journal_student.lastName, "
            "journal_student.firstName, "
            "journal_discipline.dayofWeekStartLecture, "
            "journal_discipline.timeStartLecture, "
            "journal_discipline.timeFinishLecture, "
            "journal_discipline.nameDiscipline, "
            "journal_teacher.firstName  AS 'teacher_firstName', "
            "journal_teacher.lastName AS 'teacher_lastName', "
            "journal_teacher.partonymic AS 'teacher_partonymic' "
            "FROM "
            "journal_student "
            "INNER JOIN journal_listofstudfordiscipline ON journal_listofstudfordiscipline.studId_id = journal_student.id "
            "INNER JOIN journal_discipline ON journal_discipline.id = `journal_listofstudfordiscipline`.`discipListId_id` "
            "INNER JOIN journal_teacher ON journal_teacher.id = journal_discipline.teachIdToDiscip_id "
            "INNER JOIN journal_position ON journal_position.id = journal_teacher.positionId_id "
            "WHERE "
            "`journal_student`.id = %s "
            "AND journal_position.id != 2 "
            "AND journal_discipline.dayofWeekStartLecture = 8 "
            "AND journal_discipline.dateStart >= %s "
            "AND journal_discipline.dateFinish <= %s "
            "ORDER BY "
            "journal_discipline.dayofWeekStartLecture ASC",
            [userData.id, d_left, d_right])

        data['report_schedule_8'] = qs_8

        data['d_left'] = d_left
        data['d_right'] = d_right
        data['student_name'] = userData
        data['userName'] = userData

        return render(request, 'journal/student.html', context=data)

    @login_required
    @user_passes_test(is_member_teacher)
    def material_detail(request, *args, **kwargs):
        pass

    @login_required
    @user_passes_test(is_member_teacher)
    def material(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)
        if request.method == 'POST':
            if 'material_pk' in kwargs:
                instance = material.objects.get(pk=kwargs['material_pk'])
                form = materialForm(request.POST, instance=instance)
            else:
                form = materialForm(request.POST)

            if form.is_valid():
                form.save()

                return HttpResponseRedirect(
                    reverse('discipline:discipline_detail', args=(form.cleaned_data['discipMaterialId'].id,)))

        else:
            if 'material_pk' in kwargs and 'discipline_pk' in kwargs:
                # instance = material.objects.filter(request, pk=kwargs['material_pk'])
                instance = material.objects.get(pk=kwargs['material_pk'])
                form = materialForm(instance=instance)

            else:
                lastMaterial = material.objects.filter(discipMaterialId=kwargs['discipline_pk'],
                                                       teachIdToMaterial=data['userData'].id).order_by('-dateInit')[:1]
                if len(lastMaterial) == 0:
                    dateNext = datetime.datetime.today()
                    cH = 0
                else:
                    lastMaterial = lastMaterial.get()
                    dateNext = lastMaterial.dateInit + timedelta(days=7)
                    cH = lastMaterial.countHour

                form = materialForm(initial={
                    'countHour': cH,
                    'dateInit': dateNext,
                    'discipMaterialId': kwargs['discipline_pk'],
                    'teachIdToMaterial': data['userData'].id},
                )
        if 'discipline_pk' in kwargs:
            data['discipline_last_pk'] = kwargs['discipline_pk']
            data['disciplineDetail'] = discipline.objects.filter(pk=kwargs['discipline_pk']).get()
        else:
            data['disciplineDetail'] = discipline.objects.filter(pk=data['discipline_detail_id']).get()

        data['form'] = form
        return render(request, 'journal/change_material.html', context=data)

    @login_required
    @user_passes_test(is_member_teacher)
    def material_delete(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)
        material.objects.filter(pk=kwargs['material_pk']).delete()

        return HttpResponseRedirect(reverse('discipline:discipline_detail', args=(kwargs['discipline_pk'],)))

    @login_required
    @user_passes_test(is_member_teacher)
    def material_checkbox_del(request, *args, **kwargs):
        material.objects.filter(discipMaterialId=kwargs['discipline_pk']).delete()

        return HttpResponseRedirect(reverse('discipline:discipline_detail', args=(kwargs['discipline_pk'],)))

    @login_required
    @user_passes_test(is_member_teacher)
    def material_checkbox_copy(request, *args, **kwargs):

        if request.method == 'POST':
            discipline_id = request.POST['disciplines']
            _ = list()
            for mat in request.POST.keys():
                x = re.findall('material_choice_(\d+)', mat)
                if x.__len__() > 0:
                    _.append(int(x[0]))

            if _.__len__() > 0:
                discipMateriallAll = material.objects.filter(discipMaterialId=kwargs['discipline_pk'], pk__in=_)

            # else:
            #     discipMateriallAll = material.objects.filter(discipMaterialId=kwargs['discipline_pk']).all()

                try:
                    discipline_int = int(discipline_id)
                    discipMateriallAddToDiscip = material.objects.filter(discipMaterialId=discipline_int)
                    discipMateriallAll = discipMateriallAll.values('dateInit', 'countHour', 'topic', 'homework',
                                                                   'discipMaterialId', 'meetId', 'teachIdToMaterial')
                    find_date = False
                    for i in discipMateriallAll:
                        for materialFromEditDiscip in discipMateriallAddToDiscip:
                            if materialFromEditDiscip.dateInit == i['dateInit']:
                                find_date = True
                                break
                        if find_date:
                            continue

                        materialId = material(dateInit=i['dateInit'],
                                              countHour=i['countHour'],
                                              topic=i['topic'],
                                              homework=i['homework'],
                                              discipMaterialId_id=discipline_int,

                                              meetId_id=i['meetId'],
                                              teachIdToMaterial_id=i['teachIdToMaterial'], )
                        materialId.save()

                    return HttpResponseRedirect(reverse('discipline:discipline_detail', args=(discipline_int,)))

                except Exception as ex:
                    from django import http
                    return http.HttpResponseServerError(str(ex))

        return HttpResponseRedirect(reverse('discipline:discipline_detail', args=(kwargs['discipline_pk'],)))

    @login_required
    @user_passes_test(is_member_teacher)
    def score_delete(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)
        score.objects.filter(pk=kwargs['score_pk']).delete()

        return HttpResponseRedirect(reverse('discipline:discipline_detail', args=(kwargs['discipline_pk'],)))

    @login_required
    def get_data_main(request, *args, **kwargs):
        userData = teacher.objects.filter(userTechId=request.user.id).get()

        arch_qs = cronMysql.objects.raw(
            "SELECT id, CAST(DATE_FORMAT( journal_cronmysql.dateIn, '%%Y')  AS UNSIGNED)  - 1 as 'd' "
            "FROM `journal_cronmysql` "
            "WHERE cronTypeId_id = 7 "
            "ORDER by `d` DESC ")

        now_day = datetime.datetime.today()
        format_d = now_day.strftime('%Y-%m-%d')

        discip_qs = discipline.objects.filter(teachIdToDiscip=userData.id).order_by('dayofWeekStartLecture',
                                                                                    'timeStartLecture')
        discip_qs = discip_qs.extra(where=[f"dateStart<='{format_d}' and dateFinish>='{format_d}'"])

        data = {
            'userData': userData,
            "userName": ' '.join([userData.lastName, userData.firstName[:1] + '.', userData.partonymic[:1] + '.']),
            'userId': request.user.id,
            'Disciplineforteacher': disciplineChoiceForTeacher(user_id=userData.id),
            # disciplineChoiceForTeacher(user_id=request.user.id)
            'disciplines': discip_qs,
            'arch_dates': arch_qs,

        }
        if len(data['disciplines']) > 0:
            data['discipline_detail_id'] = data['disciplines'].__getitem__(0).id

        return data

    @login_required
    @user_passes_test(is_member_teacher)
    def get_data_discipline(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)
        userData = data['userData']

        if 'discipline_pk' in kwargs:
            with_pk = discipline.objects.filter(teachIdToDiscip=userData.id, id=kwargs['discipline_pk'])
            data['discipline'] = with_pk.get()
            data['item_name'] = with_pk.__getitem__(0).nameDiscipline
            data['discipline_id'] = kwargs['discipline_pk']

            qsMaterial = material.objects.filter(teachIdToMaterial=userData.id,
                                                 discipMaterialId=kwargs['discipline_pk'])
            data['material_table'] = qsMaterial
            formMaterial = reportKtpForm()
            formMaterial.fields['disciplines'].queryset = data['disciplines'].exclude(id=kwargs['discipline_pk'])
            data['formMaterial'] = formMaterial

            # from django.contrib.admin import helpers
            # result_qs = list(qsMaterial.values('pk').all())
            # map(lambda r: r.update({'check_box': helpers.checkbox.render(helpers.ACTION_CHECKBOX_NAME, r['pk'])}), result_qs)
            # data['summary'] = list(result_qs)

            data['type_meet'] = typeOfMeet.objects.all()

            now_day = datetime.datetime.today()

            # data['students_from_discipline'] = listOfStudForDiscipline.objects.filter(discipListId=kwargs['discipline_pk']).select_related().order_by('studId__lastName')
            qs = student.objects.raw(
                "SELECT journal_student.id, "
                "       journal_student.lastName, "
                "       journal_student.firstName,"
                "       journal_material.dateInit, "
                "       journal_discipline.id AS 'discipline_id',"
                "       journal_material.id AS 'material_id',"
                "       journal_typeofmeet.meetName AS 'meetName',"
                "       journal_student.id AS 'student_id',"
                "       journal_teacher.id AS 'teacher_id',"
                "       journal_listofstudfordiscipline.status AS 'status_in_study', "
                "       journal_score.descriptionScore, "
                "       journal_score.result  "
                "FROM journal_student "
                "INNER JOIN journal_listofstudfordiscipline ON journal_listofstudfordiscipline.studId_id = journal_student.id "
                "INNER JOIN journal_discipline ON journal_discipline.id = `journal_listofstudfordiscipline`.`discipListId_id` "
                "INNER JOIN journal_material ON journal_material.discipMaterialId_id = journal_discipline.id "
                "INNER JOIN journal_typeofmeet ON journal_material.meetId_id = journal_typeofmeet.id "
                "INNER JOIN journal_teacher ON journal_teacher.id = journal_discipline.teachIdToDiscip_id "
                "LEFT JOIN `journal_score` ON "
                "       ( journal_score.disciplineId_id = journal_discipline.id ) "
                "       AND ( journal_score.materialId_id = journal_material.id ) "
                "       AND ( journal_score.studentId_id = journal_student.id ) "
                "       AND ( journal_score.teachIdToScore_id = journal_teacher.id ) "
                "WHERE `journal_student`.`isOn` = 1 AND `journal_listofstudfordiscipline`.`discipListId_id` = %s AND journal_material.dateInit <= %s"
                "ORDER BY journal_student.lastName, journal_student.id, journal_material.dateInit ASC",
                [kwargs['discipline_pk'], now_day.strftime('%Y-%m-%d')])
            data['students_from_discipline'] = qs
        return data

    @login_required
    @user_passes_test(is_member_teacher)
    def report_student_all_items_with_year(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)

        d_left, d_right = mainView.determine_date_study(request)

        qs = student.objects.raw(
            "SELECT "
            "journal_student.id, "
            "journal_student.lastName, "
            "journal_student.firstName, "
            "journal_student.course, "
            "journal_material.dateInit, "
            "journal_discipline.id AS 'discipline.id', "
            "journal_discipline.nameDiscipline, "
            "journal_material.id AS 'material.id', "
            "journal_material.meetId_id AS 'meetId', "
            "journal_teacher.id AS 'teacher.id', "
            "journal_teacher.firstName AS 'prep_firstName', "
            "journal_teacher.lastName AS 'prep_lastName', "
            "journal_teacher.partonymic AS 'prep_partonymic', "
            "journal_score.descriptionScore, "
            "journal_score.result "
            "FROM "
            "journal_student "
            "INNER JOIN journal_listofstudfordiscipline ON journal_listofstudfordiscipline.studId_id = journal_student.id "
            "INNER JOIN journal_discipline ON journal_discipline.id = `journal_listofstudfordiscipline`.`discipListId_id` "
            "INNER JOIN journal_material ON journal_discipline.id = `journal_material`.discipMaterialId_id "
            "INNER JOIN journal_teacher ON journal_teacher.id = journal_discipline.teachIdToDiscip_id "
            "INNER JOIN journal_item ON journal_item.id = journal_discipline.itemIdToDiscip_id "
            "LEFT JOIN `journal_score` ON ( journal_score.disciplineId_id = journal_discipline.id ) "
            "AND ( journal_score.materialId_id = journal_material.id ) "
            "AND ( journal_score.studentId_id = journal_student.id ) "
            "AND ( journal_score.teachIdToScore_id = journal_teacher.id ) "
            "WHERE "
            "`journal_student`.`isOn` = 1 "
            "AND `journal_student`.id = %s "
            "AND journal_score.result IS NOT NULL "
            "AND journal_score.dateIn BETWEEN %s AND %s "
            "ORDER BY "
            "journal_item.itemName ASC, "
            "journal_discipline.dayofWeekStartLecture ASC, "
            "journal_teacher.lastName ASC ",
            [kwargs['student_pk'], d_left, d_right])
        data['report_student_all_items_with_year'] = qs
        data['student_name'] = student.objects.filter(id=kwargs['student_pk']).get()
        if 'discipline_pk' in kwargs:
            data['discipline_id'] = kwargs['discipline_pk']
        return render(request, 'journal/report_student_all_items_with_year.html', context=data)

    @login_required
    @user_passes_test(is_member_teacher)
    def report_all_student_all_items_with_year(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)
        # d_left, d_right = mainView.determine_date_study(request)
        d_left, d_right = mainView.make_semestr_dates(request)
        if request.method == 'POST':
            student_id = request.POST['student']
            try:
                student_int = int(student_id)
                instance = student.objects.filter(pk=student_int)
                form = reportStudentAllItemsWithYearForm(request.POST, instance=instance.first())

                qs = student.objects.raw(
                    "SELECT "
                    "journal_student.id, "
                    "journal_student.lastName, "
                    "journal_student.firstName, "
                    "journal_student.course, "
                    "journal_material.dateInit, "
                    "journal_discipline.id AS 'discipline.id', "
                    "journal_discipline.nameDiscipline, "
                    "journal_material.id AS 'material.id', "
                    "journal_material.meetId_id AS 'meetId', "
                    "journal_teacher.id AS 'teacher.id', "
                    "journal_teacher.firstName AS 'prep_firstName', "
                    "journal_teacher.lastName AS 'prep_lastName', "
                    "journal_teacher.partonymic AS 'prep_partonymic', "
                    "journal_score.descriptionScore, "
                    "journal_score.result "
                    "FROM "
                    "journal_student "
                    "INNER JOIN journal_listofstudfordiscipline ON journal_listofstudfordiscipline.studId_id = journal_student.id "
                    "INNER JOIN journal_discipline ON journal_discipline.id = `journal_listofstudfordiscipline`.`discipListId_id` "
                    "INNER JOIN journal_material ON journal_discipline.id = `journal_material`.discipMaterialId_id "
                    "INNER JOIN journal_teacher ON journal_teacher.id = journal_discipline.teachIdToDiscip_id "
                    "INNER JOIN journal_position ON journal_position.id = journal_teacher.positionId_id "
                    "INNER JOIN journal_item ON journal_item.id = journal_discipline.itemIdToDiscip_id "
                    "LEFT JOIN `journal_score` ON ( journal_score.disciplineId_id = journal_discipline.id ) "
                    "AND ( journal_score.materialId_id = journal_material.id ) "
                    "AND ( journal_score.studentId_id = journal_student.id ) "
                    "AND ( journal_score.teachIdToScore_id = journal_teacher.id ) "
                    "WHERE "
                    "`journal_student`.`isOn` = 1 "
                    "AND journal_position.id != 2 "
                    "AND `journal_student`.id = %s "
                    "AND journal_score.result IS NOT NULL "
                    "AND journal_score.dateIn BETWEEN %s AND %s "
                    "ORDER BY "
                    "journal_item.itemName ASC, "
                    "journal_discipline.dayofWeekStartLecture ASC, "
                    "journal_teacher.lastName ASC",
                    [student_int, d_left, d_right])
                data['report_student_all_items_with_year'] = qs
                data['student_name'] = form.instance

            except ValueError:
                form = reportStudentAllItemsWithYearForm()
        else:
            form = reportStudentAllItemsWithYearForm()

        data['form'] = form
        data['d_left'] = d_left
        data['d_right'] = d_right

        if 'discipline_pk' in kwargs:
            data['discipline_id'] = kwargs['discipline_pk']
        return render(request, 'journal/report_all_student_all_items_with_year.html', context=data)

    @login_required
    @user_passes_test(is_member_teacher)
    def score_change(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)
        if request.method == 'POST':
            try:
                instance = score.objects.filter(disciplineId=kwargs['discipline_pk'], materialId=kwargs['material_pk'],
                                                studentId=kwargs['student_pk'],
                                                teachIdToScore=kwargs['teacher_pk']).get()
            except Exception as ex:
                form = scoreForm(request.POST)
            else:
                form = scoreForm(request.POST, instance=instance)

            if form.is_valid():
                qd = form.save(commit=False)

                if 'score_pk' in kwargs:
                    qd.pk = kwargs['score_pk']
                qd.save()

                return HttpResponseRedirect(
                    reverse('discipline:discipline_detail', args=(form.cleaned_data['disciplineId'].id,)))

        else:
            instance = score.objects.filter(disciplineId=kwargs['discipline_pk'], materialId=kwargs['material_pk'],
                                            studentId=kwargs['student_pk'], teachIdToScore=kwargs['teacher_pk'])
            count = instance.count()
            if count > 0:  # edit score
                form = scoreForm(instance=instance.get())
            else:  # not score
                form = scoreForm(initial={'teachIdToScore': data['userData'].id, 'studentId': kwargs['student_pk'],
                                          'materialId': kwargs['material_pk'], 'disciplineId': kwargs['discipline_pk']})

        data['info'] = {'student_name': student.objects.get(pk=kwargs['student_pk'], ),
                        'disciplin': discipline.objects.get(pk=kwargs['discipline_pk']),
                        'material': material.objects.get(pk=kwargs['material_pk'])}

        if 'discipline_pk' in kwargs:
            data['discipline_last_pk'] = kwargs['discipline_pk']

        data['form'] = form
        return render(request, 'journal/change_score.html', context=data)

    @login_required
    @user_passes_test(is_member_teacher)
    def score_redirect_to_discip(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)

        return render(request, 'journal/change_score.html', context=data)

    @login_required
    @user_passes_test(is_member_teacher)
    def report_schedule(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)
        d_left_semestr, d_right_semestr = mainView.make_semestr_dates(request)
        d_left_year, d_right_year = mainView.determine_date_study(request)

        if request.method == 'POST':
            student_id = request.POST['student']
            try:
                student_int = int(student_id)
                instance = student.objects.filter(pk=student_int)
                form = reportScheduleForm(request.POST, instance=instance.first())
                qs = student.objects.raw(
                    "SELECT "
                    "journal_student.id, "
                    "journal_student.lastName, "
                    "journal_student.firstName, "
                    "journal_discipline.dayofWeekStartLecture, "
                    "journal_discipline.timeStartLecture, "
                    "journal_discipline.timeFinishLecture, "
                    "journal_discipline.nameDiscipline, "
                    "journal_teacher.firstName  AS 'teacher_firstName', "
                    "journal_teacher.lastName AS 'teacher_lastName', "
                    "journal_teacher.partonymic AS 'teacher_partonymic' ,"
                    "journal_item.itemName "
                    "FROM "
                    "journal_student "
                    "INNER JOIN journal_listofstudfordiscipline ON journal_listofstudfordiscipline.studId_id = journal_student.id "
                    "INNER JOIN journal_discipline ON journal_discipline.id = `journal_listofstudfordiscipline`.`discipListId_id` "
                    "INNER JOIN journal_teacher ON journal_teacher.id = journal_discipline.teachIdToDiscip_id "
                    "INNER JOIN journal_position ON journal_position.id = journal_teacher.positionId_id "
                    "INNER JOIN journal_item ON journal_item.id = journal_discipline.itemIdToDiscip_id "
                    "WHERE "
                    "`journal_student`.id = %s "
                    "AND journal_position.id != 2 "
                    "AND journal_discipline.dayofWeekStartLecture != 8 "
                    "AND journal_discipline.isOn = 1 "
                    "AND ((journal_discipline.dateStart >= %s AND journal_discipline.dateFinish <= %s) OR "
                    " (journal_discipline.dateStart >= %s AND journal_discipline.dateFinish < %s)) "
                    "ORDER BY "
                    "journal_discipline.dayofWeekStartLecture, journal_discipline.timeStartLecture ASC",
                    [student_id, d_left_semestr, d_right_semestr, d_left_year, d_right_year])

                data['report_schedule'] = qs

                qs_8 = student.objects.raw(
                    "SELECT "
                    "journal_student.id, "
                    "journal_student.lastName, "
                    "journal_student.firstName, "
                    "journal_discipline.dayofWeekStartLecture, "
                    "journal_discipline.timeStartLecture, "
                    "journal_discipline.timeFinishLecture, "
                    "journal_discipline.nameDiscipline, "
                    "journal_teacher.firstName  AS 'teacher_firstName', "
                    "journal_teacher.lastName AS 'teacher_lastName', "
                    "journal_teacher.partonymic AS 'teacher_partonymic' ,"
                    "journal_item.itemName "
                    "FROM "
                    "journal_student "
                    "INNER JOIN journal_listofstudfordiscipline ON journal_listofstudfordiscipline.studId_id = journal_student.id "
                    "INNER JOIN journal_discipline ON journal_discipline.id = `journal_listofstudfordiscipline`.`discipListId_id` "
                    "INNER JOIN journal_teacher ON journal_teacher.id = journal_discipline.teachIdToDiscip_id "
                    "INNER JOIN journal_position ON journal_position.id = journal_teacher.positionId_id "
                    "INNER JOIN journal_item ON journal_item.id = journal_discipline.itemIdToDiscip_id "
                    "WHERE "
                    "`journal_student`.id = %s "
                    "AND journal_position.id != 2 "
                    "AND journal_discipline.dayofWeekStartLecture = 8 "
                    "AND journal_discipline.isOn = 1 "
                    "AND ((journal_discipline.dateStart >= %s AND journal_discipline.dateFinish <= %s) OR "
                    " (journal_discipline.dateStart >= %s AND journal_discipline.dateFinish < %s)) "
                    "ORDER BY "
                    "journal_discipline.dayofWeekStartLecture, journal_discipline.timeStartLecture ASC",
                    [student_id, d_left_semestr, d_right_semestr, d_left_year, d_right_year])

                data['report_schedule_8'] = qs_8

                data['student_name'] = form.instance
                data['d_left'] = d_left_semestr
                data['d_right'] = d_right_semestr
                data['form'] = form
                return render(request, 'journal/report_schedule.html', context=data)

            except ValueError:
                form = reportScheduleForm()


        else:
            form = reportScheduleForm()

        data['d_left'] = d_left_semestr
        data['d_right'] = d_right_semestr
        data['form'] = form

        return render(request, 'journal/report_schedule.html', context=data)

    @login_required
    @user_passes_test(is_member_teacher)
    def report_ktp(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)

        if request.method == 'POST':
            discipline_id = request.POST['disciplines']
            try:
                discipline_int = int(discipline_id)
                data['report_ktp'] = material.objects.filter(discipMaterialId=discipline_int,
                                                             teachIdToMaterial__id=data['userData'].id, ).exclude(
                    meetId=2)
                data['discip_ktp'] = discipline.objects.get(pk=discipline_int)
                form = reportKtpForm(request.POST)
                form.fields['disciplines'].queryset = data['disciplines']

                data['form'] = form
                return render(request, 'journal/report_ktp.html', context=data)

            except ValueError:
                pass

        form = reportKtpForm()
        form.fields['disciplines'].queryset = data['disciplines']

        data['form'] = form
        return render(request, 'journal/report_ktp.html', context=data)

    @login_required
    @user_passes_test(is_member_teacher)
    def report_scorecard(request, *args, **kwargs):
        data = mainView.get_data_main(request, *args, **kwargs)
        if request.method == 'POST':
            try:
                course = int(request.POST['course'])
                dep_id = int(request.POST['nameDep'])
                # typeofmeet = int(request.POST['meetName'])
                semestr = int(request.POST['halfYear'])
                d_left, d_right = mainView.determine_date_half_study(request, semestr)

                if 'paid' in request.POST and request.POST['paid'] == 'on':
                    paid = 1
                else:
                    paid = 0

                form = reportScorecardForm(request.POST)
                qs = student.objects.raw(
                    "SELECT "
                    "    journal_student.id, "
                    "    journal_student.lastName, "
                    "   journal_student.firstName, "
                    "   journal_item.id AS 'item_id', "
                    "   journal_item.itemName, "
                    "   journal_score.result, "
                    "	journal_typeofmeet.id AS 'meet_id', "
                    "   journal_typeofmeet.meetName, "
                    "   journal_score.dateIn,  "
                    "   journal_material.dateInit,  "
                    "   journal_listofstudfordiscipline.status,  "
                    "   journal_teacher.lastName AS 't_l', "
                    "   journal_teacher.firstName AS 't_f' "

                    "FROM "
                    "   journal_student "
                    "   INNER JOIN journal_listofstudfordiscipline ON journal_listofstudfordiscipline.studId_id = journal_student.id "
                    "   INNER JOIN journal_departament ON journal_student.depStudId_id = journal_departament.id "
                    "   INNER JOIN journal_discipline ON journal_discipline.id = `journal_listofstudfordiscipline`.`discipListId_id` "
                    "   INNER JOIN journal_item ON journal_discipline.itemIdToDiscip_id = `journal_item`.id "
                    "   INNER JOIN journal_material ON journal_discipline.id = `journal_material`.discipMaterialId_id "
                    "   INNER JOIN journal_typeofmeet ON journal_material.meetId_id = journal_typeofmeet.id "
                    "   INNER JOIN journal_teacher ON journal_teacher.id = journal_discipline.teachIdToDiscip_id "
                    "   LEFT JOIN `journal_score` ON ( journal_score.disciplineId_id = journal_discipline.id )  "
                    "   AND ( journal_score.materialId_id = journal_material.id )  "
                    "   AND ( journal_score.studentId_id = journal_student.id )  "
                    "   AND ( journal_score.teachIdToScore_id = journal_teacher.id )  "
                    "WHERE "
                    "   `journal_student`.`isOn` = %s  "
                    "   AND journal_student.course = %s  "
                    "   AND journal_student.paid = %s  "
                    "   AND journal_departament.id = %s "
                    "   AND (journal_typeofmeet.id = 2 or journal_typeofmeet.id = %s )   "
                    "   AND journal_score.result IS NOT NULL  "
                    "   AND journal_material.dateInit BETWEEN %s AND %s "
                    "ORDER BY "
                    "   journal_student.lastName, "
                    "   journal_student.id, "
                    "   journal_material.dateInit ASC ",
                    [1, course, paid, dep_id, semestr, d_left, d_right])

                data['report_scorecard'] = qs
                data['form'] = form
                data['d_left'] = datetime.date(int(d_left[:4]), int(d_left[4:6]), int(d_left[6:]))
                data['d_right'] = datetime.date(int(d_right[:4]), int(d_right[4:6]), int(d_right[6:]))
                return render(request, 'journal/report_scorecard.html', context=data)

            except ValueError:
                form = reportScorecardForm()


        else:
            form = reportScorecardForm()

        data['form'] = form
        return render(request, 'journal/report_scorecard.html', context=data)

    def determine_date_study(self):
        if time.localtime().tm_mon > typeOfMeet.HALF_YEAR_CHOICES[3][1]['finish_month']:
            year_int_l = time.localtime().tm_year
            year_int_r = time.localtime().tm_year + 1

        else:
            year_int_l = time.localtime().tm_year - 1
            year_int_r = time.localtime().tm_year

        date_left = ''.join((year_int_l.__str__(), f"{typeOfMeet.HALF_YEAR_CHOICES[1][1]['start_month']:02d}", "01"))
        date_right = ''.join((year_int_r.__str__(), f"{typeOfMeet.HALF_YEAR_CHOICES[1][1]['start_month']:02d}", "01"))

        return date_left, date_right

    def determine_date_half_study(self, semestr):
        if time.localtime().tm_mon > typeOfMeet.HALF_YEAR_CHOICES[3][1]['finish_month']:
            year_int_l = time.localtime().tm_year
            year_int_r = time.localtime().tm_year + 1
        else:
            year_int_l = time.localtime().tm_year - 1
            year_int_r = time.localtime().tm_year

        for id, value in typeOfMeet.HALF_YEAR_CHOICES:
            if id == semestr:
                spam = value
                break

        date_left = ''.join((f"{spam['start_year'] + year_int_l:02d}",
                             f"{spam['start_month']:02d}",
                             f"{spam['start_day']:02d}"))
        date_right = ''.join((f"{spam['finish_year'] + year_int_l:02d}",
                              f"{spam['finish_month']:02d}",
                              f"{spam['finish_day']:02d}"))

        return date_left, date_right

    def make_dates_last_semestr(self):
        a, b = mainView.make_semestr_dates(self) #Получаем границы этого семестра
        day_last_semestr = a - datetime.timedelta(days=1) #Получаем последний день прошлого семестра
        left, right = mainView.make_semestr_dates(self, day_last_semestr)

        return left, right

    def make_semestr_dates(self,
                           now_day=datetime.datetime.today()):  # Определяемся в каком семестре сейчас учимся now()

        if now_day.month > typeOfMeet.HALF_YEAR_CHOICES[3][1]['finish_month']:  # This first semestr
            year_int_l = now_day.year
            year_int_r = now_day.year + 1

        else:  # This second semestr
            year_int_l = now_day.year - 1
            year_int_r = now_day.year

        if (now_day.month >= typeOfMeet.HALF_YEAR_CHOICES[3][1]['start_month'] and now_day.day >=
            typeOfMeet.HALF_YEAR_CHOICES[3][1]['start_day']) and (
                now_day.month <= typeOfMeet.HALF_YEAR_CHOICES[3][1]['finish_month'] and now_day.day <=
                typeOfMeet.HALF_YEAR_CHOICES[3][1]['finish_day']):
            return datetime.date(year_int_r, typeOfMeet.HALF_YEAR_CHOICES[3][1]['start_month'],
                                 typeOfMeet.HALF_YEAR_CHOICES[3][1]['start_day']), datetime.date(year_int_r,
                                                                                                 typeOfMeet.HALF_YEAR_CHOICES[
                                                                                                     3][1][
                                                                                                     'finish_month'],
                                                                                                 typeOfMeet.HALF_YEAR_CHOICES[
                                                                                                     3][1][
                                                                                                     'finish_day'])  # This second semestr
        else:
            return datetime.date(year_int_l, typeOfMeet.HALF_YEAR_CHOICES[1][1]['start_month'],
                                 typeOfMeet.HALF_YEAR_CHOICES[1][1]['start_day']), datetime.date(year_int_r,
                                                                                                 typeOfMeet.HALF_YEAR_CHOICES[
                                                                                                     1][1][
                                                                                                     'finish_month'],
                                                                                                 typeOfMeet.HALF_YEAR_CHOICES[
                                                                                                     1][1][
                                                                                                     'finish_day'])  # This first semestr


from dal import autocomplete


class studentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        #        if not self.request.user.is_authenticated():
        #            return student.objects.none()
        qs = student.objects.all()
        if self.q:
            qs = qs.filter(lastName__istartswith=self.q)
        return qs
