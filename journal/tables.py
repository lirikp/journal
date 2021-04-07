import django_tables2 as tables

from .models import material, teacher, student


class MaterialTable(tables.Table):
    dateInit = tables.Column(verbose_name='Число/месяц', orderable=False)
    countHour = tables.Column(verbose_name='Кол-во уч. часов', orderable=False)

    topic = tables.Column(attrs={"td": {"class": "table-discip-material-topic"}}, verbose_name='Что пройдено на уроке',
                          orderable=False)
    homework = tables.Column(verbose_name='Задание на дом',orderable=False)
    meetId = tables.Column(verbose_name='Тип встречи',orderable=False)

    class Meta:
        model = material
        # add class="paleblue" to <table> tag
        # attrs = {'class': 'paleblue'}
        fields = ("dateInit", "countHour", "topic", "homework", "meetId",)
        attrs = {"class": "table-discip-material"}
        # attrs = {"td": {"class": "tables_discipline_td"}}
        # attrs = {"tr": {"class": "tables_discipline_tr"}}

        # border: 2px solid  # 000;

class TeacherContactTable(tables.Table):
    class Meta:
        model = teacher
        template_name = "django_tables2/bootstrap.html"
        fields = ('lastName', 'firstName', 'partonymic', 'tel', 'userTechId__email', 'depTeachId', 'positionId')

class StudentContactTable(tables.Table):
    class Meta:
        model = student
        template_name = "django_tables2/bootstrap.html"
        fields = ('lastName', 'firstName', 'partonymic', 'tel', 'userStudId__email', 'course','depStudId', 'paid')
