from dal import autocomplete
from django.contrib import admin
from django.forms import modelformset_factory

from journal.forms import studentForm, CustomFormInlineForStudent
from journal.models import *



class itemAdmin(admin.ModelAdmin):
    model = item
    list_display = ("itemName", "fullInfo")
    search_fields = ("itemName",)
    ordering = ["itemName", ]


'''    def get_name(self, obj):
        return obj.itemToDep.nameDep

    get_name.short_description = 'Отделение'
    get_name.admin_order_field = 'itemToDep'
'''


class teacherAdmin(admin.ModelAdmin):
    model = teacher
    list_display = ('lastName', 'firstName', 'partonymic',)
    search_fields = ("lastName", 'firstName',)
    ordering = ["lastName", 'firstName', ]


#    list_filter = ("firstName", "lastName")

class studentAdmin(admin.ModelAdmin):
    model = student
    list_display = ('lastName', 'firstName', 'partonymic',)
    search_fields = ("lastName", 'firstName',)
    ordering = ["lastName", 'firstName', ]

    def get_queryset(self, request):
        return self.model.allStudentObjects.filter()

    #form = studentForm

    class Meta:
        widgets = {
            'student': autocomplete.ModelSelect2(url='student-autocomplete')
        }


class listOfStudForDisciplineAdmin(admin.ModelAdmin):
    model = listOfStudForDiscipline
    list_display = ("get_lastName", "get_firstName", "get_nameDep", "get_nameDiscipline",)
    search_fields = ("studId__lastName", "studId__firstName", "studId__depStudId__nameDep",)
    list_filter = ("studId__depStudId__nameDep",)  # "discipListId__nameDiscipline",)

    def get_queryset(self, request):
        return self.model.objects.all().filter(studId__isOn=1)


class discipStudentInline(admin.TabularInline):
#class discipStudentInline(admin.StackedInline):

    model = listOfStudForDiscipline


    MyFormSet = modelformset_factory(model, fields=["discipListId", 'studId'],)
#    formset = MyFormSet(queryset=student.objects.filter(isOn=1))

    form = CustomFormInlineForStudent
    admin.TabularInline.verbose_name = 'Студент'

    extra = 1

    def has_change_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        return self.model.objects.filter(studId__isOn=1).order_by("studId__lastName",)


class disciplineAdmin(admin.ModelAdmin):
    model = discipline
    list_display = ("get_itemName", "paid_discip", "dateStart", "dateFinish", "nameDiscipline","timeStartLecture","timeFinishLecture", "get_lastName")
    search_fields = ("teachIdToDiscip__lastName", "teachIdToDiscip__firstName", "nameDiscipline", "itemIdToDiscip__itemName",)

    inlines = [discipStudentInline]
    ordering = ["dayofWeekStartLecture", 'timeStartLecture', ]

    date_hierarchy = 'dateStart'
#    def get_queryset(self, request):
#   return self.model.objects.extra(where=['isOn = 1'])
#        return self.model.objects.filter(score__studentId__isOn=1)


class materialAdmin(admin.ModelAdmin):
    model = material
    list_display = ("dateInit", "countHour", "isCount", "topic", "meetId")
    list_filter = ("countHour", "isCount", "meetId")
    # search_fields = ("topic",)
    # prepopulated_fields = {'slug': ('title',)}
    # raw_id_fields = ('author',)

    date_hierarchy = 'dateInit'

class scoreAdmin(admin.ModelAdmin):
    model = score
    list_display = ("studentId", "disciplineId", "teachIdToScore", "materialId", "result")
    list_filter = ("result",)
    search_fields = ("studentId","disciplineId",)
    # prepopulated_fields = {'slug': ('title',)}
    # raw_id_fields = ('author',)


    date_hierarchy = 'dateIn'
    #ordering = ["studentId", "disciplineId", ]


admin.site.register(teacher, teacherAdmin)
admin.site.register(material, materialAdmin)
admin.site.register(score,scoreAdmin)
admin.site.register(typeOfMeet)
admin.site.register(student, studentAdmin)
admin.site.register(departament)
admin.site.register(discipline, disciplineAdmin)
admin.site.register(listOfStudForDiscipline, listOfStudForDisciplineAdmin)
admin.site.register(position)
admin.site.register(item, itemAdmin)

admin.site.enable_nav_sidebar = False

