import datetime
import time

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth.models import Group

from .forms import disciplineChoiceForTeacher, reportListOfJournalsForm, reportKtpForm
from .models import student, teacher, discipline, typeOfMeet,cronMysql, material
from journal.views import mainView


# from .tables import MaterialTable


class mainViewArch(LoginRequiredMixin, ListView):
    LoginRequiredMixin.login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def is_member_student(user):
        return user.groups.filter(name='student').exists()

    def is_member_teacher(user):
        return user.groups.filter(name='teacher').exists()

    @login_required
    def journal_last_semestr(request, *args, **kwargs):
        if Group.objects.get(name='teacher') in request.user.groups.all():
            data = mainView.get_data_main(request, *args, **kwargs)
            d_left, d_right = mainView.make_dates_last_semestr(request)
            teacher_id = data['userData'].id
            try:
                instance = teacher.objects.filter(pk=teacher_id)
                form = reportListOfJournalsForm(request.POST, instance=instance.first())

                discip_qs = discipline.objects.filter(teachIdToDiscip=teacher_id).order_by('dayofWeekStartLecture',
                                                                                           'timeStartLecture')
                discip_qs = discip_qs.extra(where=[f"dateStart>='{d_left.strftime('%Y-%m-%d')}' and dateFinish<='{d_right.strftime('%Y-%m-%d')}'"])
                data['disciplines_for_manager'] = discip_qs

            except ValueError:
                form = reportListOfJournalsForm()

            data['d_left'] = d_left
            data['d_right'] = d_right
            data['form'] = form
            return render(request, 'journal/report_journal_manager.html', context=data)
        else:
            raise Http404




    @login_required
    def main_arch(request, *args, **kwargs):

        if request.user.groups.filter(name='student').exists():
            return HttpResponseRedirect(reverse('students:student_detail',))
        elif request.user.groups.filter(name='teacher').exists():

            data = mainViewArch.__get_data_main(request, *args, **kwargs)


            form = reportKtpForm()
            form.fields['disciplines'].queryset = data['disciplines']

            data['form'] = form

            return render(request, 'journal/arch.html', context=data)
        else:
            raise Http404

    @login_required
    @user_passes_test(is_member_teacher)
    def discipline_detail(request, *args, **kwargs):
        data = mainViewArch.__get_data_discipline(request, *args, **kwargs)

        return render(request, 'journal/main.html', context=data)

    @login_required
    def __get_data_main(request, *args, **kwargs):
        userData = teacher.objects.filter(userTechId=request.user.id).get()

        arch_qs = cronMysql.objects.raw(
            "SELECT id, CAST(DATE_FORMAT( journal_cronmysql.dateIn, '%%Y')  AS UNSIGNED)  - 1 as 'd' "
            "FROM `journal_cronmysql` "
            "WHERE cronTypeId_id = 7 "
            "ORDER by `d` DESC ")


        now_day = datetime.datetime.today()
        format_d = now_day.strftime('%Y-%m-%d')

        discip_qs = discipline.objects.filter(teachIdToDiscip=userData.id)
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



from dal import autocomplete


class studentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        #        if not self.request.user.is_authenticated():
        #            return student.objects.none()
        qs = student.objects.all()
        if self.q:
            qs = qs.filter(lastName__istartswith=self.q)
        return qs
