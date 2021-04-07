from django import forms
from django.forms import Select

from .models import student, listOfStudForDiscipline, discipline, material, typeOfMeet, score, departament, teacher
from django.contrib.auth.models import User


class disciplineChoiceForTeacher(forms.Form):
    def __init__(self, user_id, *args, **kwargs):
        self.user_id = user_id
        super().__init__(*args, *kwargs)
        discipline.objects.filter(teachIdToDiscip=user_id)

    def get_disciplines_for_id_teacher(self):
        return forms.ModelChoiceField(queryset=discipline.objects.filter(teachIdToDiscip=self.user_id), required=True)

    class Meta:
        model = discipline
        fields = ('nameDiscipline', 'dateStart')


class CustomFormInlineForStudent(forms.ModelForm):
    # student = forms.ModelChoiceField(queryset=student.objects.filter(isOn=1))
    # field_order = ['-lastName',]

    class Meta:
        model = student
        exclude = [""]


class studentForm(forms.ModelForm):
    # student = forms.ModelChoiceField(queryset=student.objects.all().filter(isOn=1))
    # lastName = forms.ModelChoiceField(
    #     queryset=student.objects.all(),
    #     widget=autocomplete.ModelSelect2(url='student-autocomplete')
    # )

    class Meta:
        model = student
        fields = ('__all__')


class disciplineForm(forms.ModelForm):
    class Meta:
        model = discipline
        exclude = [""]


class listOfStudForDisciplineForm(forms.ModelForm):
    class Meta:
        model = listOfStudForDiscipline
        exclude = [""]


class listOfStudForDisciplineInlineForm(forms.ModelForm):
    class Meta:
        model = listOfStudForDiscipline
        exclude = [""]


class materialForm(forms.ModelForm):
    # dateInit = forms.DateField()

    countHour = forms.ChoiceField(choices=material.COUNT_HOUR_CHOICE)
    topic = forms.CharField(max_length=255, required=False)
    homework = forms.CharField(max_length=255, required=False)
    meetId = forms.ModelChoiceField(queryset=typeOfMeet.objects.all(), empty_label=None, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'].widget.attrs.update({'class': 'text-area-inline'})
        self.fields['topic'].widget.attrs.update({'title': '255 символов максимально'})
        self.fields['homework'].widget.attrs.update({'class': 'text-area-inline'})
        self.fields['homework'].widget.attrs.update({'title': '255 символов максимально'})
        self.fields['countHour'].widget.attrs.update({'class': 'countHour-inline'})
        self.fields['meetId'].widget.attrs.update({'class': 'meetId-inline'})
        self.fields['dateInit'].widget.attrs.update({'class': 'dateInit-inline'})


    class Meta:
        model = material
        widgets = {
            'dateInit': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date', }),
            'discipMaterialId': forms.HiddenInput(),
            'teachIdToMaterial': forms.HiddenInput(),
            "isCount": forms.HiddenInput(),

            "id": forms.HiddenInput(),
        }
        fields = ('id', 'dateInit', 'countHour', 'topic', 'homework', 'meetId', 'discipMaterialId', 'teachIdToMaterial',
                  'isCount')

        # exclude = ["discipMaterialId", "teachIdToMaterial" , "isCount"]

    def clean(self, *args, **kwargs):
        dateInit = self.cleaned_data.get('dateInit')
        obj_material = material.objects.filter(dateInit=dateInit,
                                               discipMaterialId=self.cleaned_data.get('discipMaterialId'),
                                               teachIdToMaterial=self.cleaned_data.get('teachIdToMaterial'))
        if (not self.instance.pk and obj_material.count() > 0) or (
                'dateInit' in self.changed_data and self.instance.pk and obj_material.count() == 1):  # ФФФ
            if not 'dateInit' in self._errors:
                from django.forms.utils import ErrorList
                self._errors['dateInit'] = ErrorList()
            self._errors['dateInit'].append('Дата материала не должна повторяться!')
        obj_discip = discipline.objects.filter(pk=self.data['discipMaterialId']).get()
        if dateInit > obj_discip.dateFinish or dateInit < obj_discip.dateStart:
            if not 'dateInit' in self._errors:
                from django.forms.utils import ErrorList
                self._errors['dateInit'] = ErrorList()
            self._errors['dateInit'].append(
                'Дата материала не может быть больше даты конца или меньше начала текущего учебного семестра')

        countHour = float(self.cleaned_data.get('countHour'))
        if countHour < 0:
            if not 'countHour' in self._errors:
                from django.forms.utils import ErrorList
                self._errors['countHour'] = ErrorList()
            self._errors['countHour'].append('Количество часов не может быть отрицательным!')

        if self.cleaned_data.get('meetId').id in [2] and countHour != 0:
            if not 'countHour' in self._errors:
                from django.forms.utils import ErrorList
                self._errors['countHour'] = ErrorList()
            self._errors['countHour'].append(
                'Количество часов должно быть равно нулю, если это отчётное занятие (экзамен, и.т.п.)')


class reportScheduleForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=student.objects.filter(isOn=1))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].widget.attrs.update({'class': 'text-label'})

    class Meta:
        model = student

        fields = ('id', 'firstName', 'lastName',)


class reportListOfJournalsForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=teacher.objects.filter(userTechId_id__is_active=1).order_by('lastName', 'firstName'))
    paid = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].widget.attrs.update({'class': 'text-label'})

    class Meta:
        model = teacher

        fields = ('id', 'firstName', 'lastName',)


class contactTeacherForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=teacher.objects.filter(userTechId_id__is_active=1).order_by('lastName', 'firstName'))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].widget.attrs.update({'class': 'text-label'})

    class Meta:
        model = teacher

        fields = ('id', 'firstName', 'lastName', 'partonymic', 'tel', 'userTechId')


class contactStudentForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(queryset=student.objects.filter(isOn=1).order_by('lastName', 'firstName'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].widget.attrs.update({'class': 'text-label'})

    class Meta:
        model = student

        fields = ('id', 'firstName', 'lastName', 'partonymic', 'tel', 'userStudId')


class reportKtpForm(forms.ModelForm):
    disciplines = forms.ModelChoiceField(queryset=discipline.objects.none(), required=True, empty_label=None, )

    material_choice = forms.BooleanField(required=False)

    class Meta:
        model = discipline
        fields = ('nameDiscipline', 'teachIdToDiscip', 'literatura', 'сontrol_requirements', "material_choice")
        widgets = {"material_choice": forms.CheckboxInput()}

    def __init__(self, *args, **kwargs):
        # self.qs_discip = kwargs.pop('qs_discip', None)
        # self.disciplines = forms.ModelChoiceField(queryset=self.qs_discip)
        super().__init__(*args, **kwargs)
        self.fields['disciplines'].widget.attrs.update({'class': 'selector400px'})


class reportStudentAllItemsWithYearForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=student.objects.filter(isOn=1))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].widget.attrs.update({'class': 'text-label'})

    class Meta:
        model = student

        fields = ('id', 'firstName', 'lastName',)


from django.db.models import BLANK_CHOICE_DASH


class reportScorecardForm(forms.ModelForm):
    TRANSFORM_YEAR_CHOICES = tuple()
    for id, value in typeOfMeet.HALF_YEAR_CHOICES:
        TRANSFORM_YEAR_CHOICES = TRANSFORM_YEAR_CHOICES + ((id, value['name']), )
    TRANSFORM_YEAR_CHOICES = (('', '--- Выберите значение ---'),) + TRANSFORM_YEAR_CHOICES

    nameDep = forms.ModelChoiceField(queryset=departament.objects.filter(id__range=[1, 7]), empty_label='--- Выберите значение ---')
    course = forms.ChoiceField(choices=(('', '--- Выберите значение ---'),) +  student.COURSE_OF_STUDENT_CHOICES)
    halfYear = forms.ChoiceField(choices=TRANSFORM_YEAR_CHOICES)
    meetName = forms.ModelChoiceField(queryset=typeOfMeet.objects.filter(id__range=[2, 6]).order_by('id'),
                                      empty_label=None)
    paid = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nameDep'].widget.attrs.update({'class': 'selector400px'})
        self.fields['halfYear'].widget.attrs.update({'class': 'selector400px'})
        self.fields['course'].widget.attrs.update({'class': 'selector400px'})
        self.fields['meetName'].widget.attrs.update({'class': 'selector400px'})
        self.fields['paid'].widget.attrs.update({'class': 'scorecard-checkbox'})

    class Meta:
        model = student

        fields = ('id', 'firstName', 'lastName', 'course', 'paid')


class scoreForm(forms.ModelForm):
    descriptionScore = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descriptionScore'].widget.attrs.update({'class': 'text-area-inline'})
        self.fields['descriptionScore'].widget.attrs.update({'title': '255 символов максимально'})

    class Meta:
        model = score
        widgets = {
            'teachIdToScore': forms.HiddenInput(),
            'studentId': forms.HiddenInput(),
            "materialId": forms.HiddenInput(),
            "disciplineId": forms.HiddenInput(),
            "id": forms.HiddenInput(),
        }

        fields = ('id', 'result', 'descriptionScore', 'teachIdToScore', 'studentId', 'materialId', 'disciplineId',)

    def clean(self, *args, **kwargs):
        teachIdToScore = self.cleaned_data.get('teachIdToScore').id
        obj_discipline = discipline.objects.get(id=self.cleaned_data['disciplineId'].id)

        if obj_discipline.teachIdToDiscip_id != teachIdToScore:
            if not 'result' in self._errors:
                from django.forms.utils import ErrorList
                self._errors['result'] = ErrorList()
            self._errors['result'].append(
                'Вы не можете поставить оценку в чужой дисциплине, обратитесь к администратору')
