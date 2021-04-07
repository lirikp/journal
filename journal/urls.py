"""journal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView

from journal.views import mainView
from journal.views_arch import mainViewArch
from journal.views_journal_manager import viewReportManager

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

arch_patterns = ([
                         path('<int:arch_year>/', mainViewArch.main_arch, name='main_arch'),
                 ], 'arch',)

students_patterns = ([
                         path('', mainView.student, name='student_detail'),
                     ], 'student')

discipline_patterns = ([
                           path('<int:discipline_pk>/', mainView.discipline_detail, name='discipline_detail'),
                           path('', mainView.discipline_detail, name='discipline_detail'),
                       ], 'discipline')

score_patterns = ([
                      path('<int:discipline_pk>/<int:material_pk>/<int:student_pk>/<int:teacher_pk>/',
                           mainView.score_change, name='score_change'),
                      path('', mainView.score_redirect_to_discip, name='score_redirect_to_discip'),
                      path('<int:discipline_pk>/<int:score_pk>/delete', mainView.score_delete, name='score_del'),
                  ], 'score')

material_patterns = ([
                         path('<int:material_pk>/', mainView.material, name='material_change'),
                         path('<int:material_pk>/delete', mainView.material_delete, name='material_del'),
                         path('delete/', mainView.material_checkbox_del, name='material_checkbox_del'),
                         path('copy/', mainView.material_checkbox_copy, name='material_checkbox_copy'),
                         path('new/', mainView.material, name='material_new'),
                         path('', mainView.material, name='material_list'),
                         # path('', mainView.material_detail, name='material_detail'),
                     ], 'material')

reports_patterns = ([
                        path('report_student_all_items_with_year/<int:student_pk>/<int:discipline_pk>/',
                             mainView.report_student_all_items_with_year, name='report_student_all_items_with_year'),
                        path('report_all_student_all_items_with_year/',
                             mainView.report_all_student_all_items_with_year,
                             name='report_all_student_all_items_with_year'),
                        path('schedule/', mainView.report_schedule, name='report_schedule'),
                        path('scorecard/', mainView.report_scorecard, name='report_scorecard'),
                        path('ktp/', mainView.report_ktp, name='report_ktp'),
                        path('journal_manager/', viewReportManager.journal_manager_main, name='journal_manager'),
                        path('journal_last_semestr/', mainViewArch.journal_last_semestr, name='arch_last_semestr'),
                        path('contacts_teacher/', viewReportManager.contact_teacher, name='contacts_teacher'),
                        path('contacts_student/', viewReportManager.contact_student, name='contacts_student'),
                        path('workload/', viewReportManager.workload, name='workload'),
                        path('workload_all/', viewReportManager.workload_all, name='workload_all'),
                        path('schedule_teacher/', viewReportManager.schedule_teacher, name='schedule_teacher'),
                    ], 'reports')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(('django.contrib.auth.urls', 'users'), namespace='users')),
    # url(r'^accounts/login/$', views.auth_login, {'redirect_field_name': 'registration/login.html'}),
    # url(r'^logout/$', mainView.auth_logout),
    # url(r'^$', name='main_list'),

    # url(r'^$', mainView.main_list),
    path(r'', mainView.main_list, name='main_list'),
    path('discipline/', include((discipline_patterns), namespace='discipline')),
    path('discipline/<int:discipline_pk>/material/', include((material_patterns), namespace='material')),
    path('score/', include((score_patterns), namespace='score')),
    path('reports/', include((reports_patterns), namespace='reports')),
    path('student/', include((students_patterns), namespace='students')),
    path('arch/', include((arch_patterns), namespace='arch')),

    re_path(r'^favicon\.ico$', favicon_view),

    # path('discipline/<int:pk>/', mainView.discipline_detail, name='discipline'),
    #        url(r'^student-autocomplete/$', views.mainView.studentAutocomplete.as_view(), name='student-autocomplete',),

    # path('login/', views.LoginView.as_view(), name='login'),
]
