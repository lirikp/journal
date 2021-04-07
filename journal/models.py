# from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


# class profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     tel = models.TextField(max_length=20, blank=True)
#     location = models.CharField(max_length=30, blank=True)
#     birth_date = models.DateField(null=True, blank=True)
#
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         profile.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
#

class departament(models.Model):
    nameDep = models.CharField(max_length=255, unique=True)
    order_by = models.IntegerField(verbose_name='Порядок в отчёте',null=True, blank=True)

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

    def __str__(self):
        return "%s" % (self.nameDep)


class item(models.Model):
    itemName = models.CharField(max_length=255)
    #    itemToDep = models.ForeignKey(departament, on_delete=models.CASCADE)
    fullInfo = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return "%s" % (self.itemName)


class liveListStudent(models.Manager):
    use_in_migrations = False

    def get_queryset(self):
        return super(liveListStudent, self).get_queryset().filter(isOn=1)


class student(models.Model):
    COURSE_OF_STUDENT_CHOICES = (
        (0, 'подготовительный'),
        (1, '1 курс'),
        (2, '2 курс'),
        (3, '3 курс'),
        (4, '4 курс'),
        (5, 'стажёры'),

    )

    id = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=20, verbose_name='Имя')
    lastName = models.CharField(max_length=25, verbose_name='Фамилия')
    partonymic = models.CharField(max_length=20, verbose_name='Отчество', null=True)
    dateStartStudy = models.DateField(verbose_name='Дата начала обучения')
    dateFinishStudy = models.DateField(verbose_name='Дата окончания обучения')
    course = models.IntegerField(choices=COURSE_OF_STUDENT_CHOICES, default=1, verbose_name='Курс студента')
    isOn = models.BooleanField(verbose_name='Действительно обучается')
    paid = models.BooleanField(verbose_name='Платное отделение')
    foreignStudent = models.BooleanField(verbose_name='Иностранец')
    depStudId = models.ForeignKey(departament, on_delete=models.CASCADE, verbose_name='Отделение')
    userStudId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
                                   verbose_name='Связь с входным логином')
    phone_regex = RegexValidator(regex=r'^\+7\([0-9]{3}\)[0-9]{7}$',
                                 message="Номер должен быть следующего формата: +7(123)4567890.")
    tel = models.CharField(validators=[phone_regex], max_length=17, null=True, blank=True,
                           verbose_name='Номер телефона')
    location = models.CharField(max_length=50, blank=True, verbose_name='Адрес проживания')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    transfer = models.BooleanField(null=True, blank=True, verbose_name='Перезачёт')
    descriptionStudent = models.CharField(max_length=200, null=True, blank=True)

    # objects = models.Manager()
    objects = liveListStudent()

    liveStudentObjects = liveListStudent()
    allStudentObjects = models.Manager()

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['lastName', 'firstName']

    def __str__(self):
        # return "%s %s---%s" % (self.lastName, self.firstName, self.depStudId.nameDep)
        return "%s %s" % (self.lastName, self.firstName)


class studentArch(models.Model):
    id = models.AutoField(primary_key=True)
    idStudent = models.ForeignKey(student, on_delete=models.CASCADE,
                                  verbose_name='Связь с основной записью из таблицы студентов')
    archYearStudy = models.IntegerField(verbose_name='Дата архивации учебного года')
    course = models.IntegerField(choices=student.COURSE_OF_STUDENT_CHOICES, default=1, verbose_name='Курс студента')
    isOn = models.BooleanField(verbose_name='Действительно обучается')
    paid = models.BooleanField(verbose_name='Платное отделение')
    foreignStudent = models.BooleanField(verbose_name='Не местный')
    depStudId = models.ForeignKey(departament, on_delete=models.CASCADE, verbose_name='Департамент')

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['archYearStudy']

    def __str__(self):
        return "%s %s" % (self.idStudent.lastName, self.idStudent.firstName)


class position(models.Model):
    id = models.AutoField(primary_key=True)
    positionName = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return "%s" % (self.positionName)


class teacher(models.Model):
    id = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=20, verbose_name='Имя')
    lastName = models.CharField(max_length=25, verbose_name='Фамилия')
    partonymic = models.CharField(max_length=20, verbose_name='Отчество', null=True)
    dateStartTeach = models.DateField(null=True, verbose_name='Начал работать')
    dateFinishTeach = models.DateField(null=True, blank=True, verbose_name='Окончил работу')
    substitution = models.IntegerField(null=True, blank=True, verbose_name='Замещающий преподаватель')
    positionId = models.ForeignKey(position, on_delete=models.CASCADE, verbose_name='Тип преподавания')
    depTeachId = models.ForeignKey(departament, default=False, on_delete=models.CASCADE, blank=True, )
    userTechId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                   verbose_name='Связь с входным логином')
    phone_regex = RegexValidator(regex=r'^\+7\([0-9]{3}\)[0-9]{7}$',
                                 message="Номер должен быть следующего формата: +7(123)4567890.")
    tel = models.CharField(validators=[phone_regex], max_length=17, null=True, blank=True,
                           verbose_name='Номер телефона')
    location = models.CharField(max_length=50, blank=True, verbose_name='Адрес проживания')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    descriptionTeachert = models.CharField(max_length=255, null=True, blank=True,
                                           verbose_name='Дополнительная информация')

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def __str__(self):
        return "%s %s %s" % (self.lastName, self.firstName, self.partonymic)


class discipline(models.Model):
    DAY_OF_WEEK_CHOICES = (
        (1, 'понедельник'),
        (2, 'вторник'),
        (3, 'среда'),
        (4, 'четверг'),
        (5, 'пятница'),
        (6, 'суббота'),
        (7, 'воскресенье'),
        (8, 'рассредоточено'),
    )

    id = models.AutoField(primary_key=True)
    nameDiscipline = models.CharField(max_length=100, null=False, verbose_name='Название дисциплины')
    itemIdToDiscip = models.ForeignKey(item, on_delete=models.CASCADE, default=1, verbose_name='Тематика дисциплины')
    dateStart = models.DateField(verbose_name='Дата начала занятий')
    dateFinish = models.DateField(verbose_name='Дата окончания занятий')
    teachIdToDiscip = models.ForeignKey(teacher, on_delete=models.CASCADE, verbose_name='Преподаватель')
    dayofWeekStartLecture = models.IntegerField(verbose_name='День недели лекции', choices=DAY_OF_WEEK_CHOICES)
    timeStartLecture = models.TimeField(verbose_name='Время начала лекции')
    timeFinishLecture = models.TimeField(verbose_name='Время окончания лекции')
    paid_discip = models.BooleanField(verbose_name='Платная дисциплина', blank=True, default=0)
    diplom  = models.BooleanField(verbose_name='Диплом', blank=True, default=0)
    isOn = models.BooleanField(verbose_name='Дисциплина включена для расписания', blank=False, default=1)
    literatura = models.TextField(verbose_name='Литература', null=True, blank=True)
    сontrol_requirements = models.TextField(verbose_name='Контрольные требования', null=True, blank=True)

    descriptionDiscipline = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Дисциплину'
        verbose_name_plural = 'Дисциплины'

    def __str__(self):
        return self.nameDiscipline

    def get_itemName(self):
        return self.itemIdToDiscip.itemName

    get_itemName.short_description = 'Предмет'
    get_itemName.admin_order_field = 'itemName'

    def get_lastName(self):
        return ' '.join([self.teachIdToDiscip.lastName, self.teachIdToDiscip.firstName])

    get_lastName.short_description = 'ФИО'
    get_lastName.admin_order_field = 'teachIdToDiscip'


class listOfStudForDiscipline(models.Model):
    STATUS_OF_DISCIPLINE = (
        (0, 'нормальный студент'),
        (1, 'перезачёт'),
    )

    id = models.AutoField(primary_key=True)
    discipListId = models.ForeignKey(discipline, on_delete=models.CASCADE)
    studId = models.ForeignKey(student, on_delete=models.CASCADE)
    status = models.IntegerField(verbose_name='Статус студента в дисциплине', choices=STATUS_OF_DISCIPLINE, default=0, )

    class Meta:
        verbose_name = 'Список студентов в дисциплине'
        verbose_name_plural = 'Список студентов в дисциплинах'
        ordering = ['-studId__lastName', ]

    def get_lastName(self):
        return self.studId.lastName

    get_lastName.short_description = 'Фамилия'

    # get_lastName.admin_order_field = 'lastName'

    def get_firstName(self):
        return self.studId.firstName

    get_firstName.short_description = 'Имя'

    # get_firstName.admin_order_field = 'firstName'

    def get_nameDep(self):
        return self.studId.depStudId.nameDep

    get_nameDep.short_description = 'Отделение'

    # get_nameDep.admin_order_field = 'departament__nameDep'

    def get_nameDiscipline(self):
        return self.discipListId.nameDiscipline

    get_nameDiscipline.short_description = 'Дисциплина'

    # get_nameDiscipline.admin_order_field = 'nameDiscipline'

    def __str__(self):
        # return '{}---{} {}---{}'.format(self.studId.depStudId.nameDep, self.studId.lastName, self.studId.firstName,
        #                                self.discipListId.nameDiscipline)
        return '{}'.format(self.studId.depStudId.nameDep)


class typeOfMeet(models.Model):
    MEET_CHOICES = (
        ('lesson', 'lesson'),
        ('exam', 'exam'),
        ('itogo_1', 'itogo_1'),
        ('itogo_2', 'itogo_2'),
        ('itogo_3', 'itogo_3'),
        ('itogo_4', 'itogo_4'),
    )

    HALF_YEAR_CHOICES = (
        (3,
         {'name': '1 четверть', 'start_year': 0, 'start_month': 9, 'start_day': 1, 'finish_year': 0, 'finish_month': 10,
          'finish_day': 31}),
        (4,
         {'name': '1 семестр', 'start_year': 0, 'start_month': 9, 'start_day': 1, 'finish_year': 1, 'finish_month': 1,
          'finish_day': 31}),
        (5,
         {'name': '3 четверть', 'start_year': 1, 'start_month': 2, 'start_day': 9, 'finish_year': 1, 'finish_month': 4,
          'finish_day': 30}),
        (6,
         {'name': '2 семестр', 'start_year': 1, 'start_month': 2, 'start_day': 1, 'finish_year': 1, 'finish_month': 8,
          'finish_day': 31}),
    )

    id = models.AutoField(primary_key=True)
    meetName = models.CharField(max_length=10, choices=MEET_CHOICES, default='lesson')
    verboseName = models.CharField(max_length=24, default='', null=True, blank=True)

    class Meta:
        verbose_name = 'Статус встречи'
        verbose_name_plural = 'Статусы встреч'

    def __str__(self):
        return self.verboseName


class material(models.Model):
    COUNT_HOUR_CHOICE = (
        (0, 0),
        (0.5, 0.5),
        (1.0, 1.0),
        (1.5, 1.5),
        (2.0, 2.0),
        (2.5, 2.5),
        (3.0, 3.0),
        (3.5, 3.5),
        (4.0, 4.0),
        (4.5, 4.5),
        (5.0, 5.0),
    )

    id = models.AutoField(primary_key=True)
    dateInit = models.DateField(verbose_name='Дата изучения материала')
    countHour = models.FloatField(default=2, choices=COUNT_HOUR_CHOICE, verbose_name='Количество часов')
    isCount = models.BooleanField(default=True, verbose_name='Пойдёт в отчёт')
    topic = models.TextField(null=True, blank=True, verbose_name='Тема занятия')
    homework = models.TextField(null=True, blank=True, verbose_name='Домашнее задание')
    meetId = models.ForeignKey(typeOfMeet, on_delete=models.CASCADE, verbose_name='Тип занятия')
    discipMaterialId = models.ForeignKey(discipline, on_delete=models.CASCADE, verbose_name='Дисциплина')
    teachIdToMaterial = models.ForeignKey(teacher, on_delete=models.CASCADE, verbose_name='Преподаватель')

    def get_absolute_url(self):
        pass

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['dateInit']

    def __str__(self):
        return "'%s'Topic:%s Преподаватель:%s %s" % (
            self.dateInit.strftime("%Y-%m-%d"), ' ' + self.topic, self.teachIdToMaterial.lastName,
            self.teachIdToMaterial.firstName)


class score(models.Model):
    RESULT_CHOICES = (
        # (u'\u00b7', u'\u00b7'),
        ('5+', '5+'),
        ('5-', '5-'),
        ('5', '5'),
        ('4+', '4+'),
        ('4-', '4-'),
        ('4', '4'),
        ('3+', '3+'),
        ('3-', '3-'),
        ('3', '3'),
        ('2+', '2+'),  # special for Khodjko Olga Kazemirovna
        ('2', '2'),
        ('зачёт', 'зачёт'),
        # ('п/з', 'п/зачет'),
        ('Н', 'Н'),
        ('осв', 'осв'),
        ('н.с.', 'н.с.'),
        ('', '')
    )

    id = models.AutoField(primary_key=True)
    dateIn = models.DateTimeField(auto_now=True, verbose_name='Дата оценки')
    teachIdToScore = models.ForeignKey(teacher, on_delete=models.CASCADE, verbose_name='Преподаватель')
    studentId = models.ForeignKey(student, on_delete=models.CASCADE, verbose_name='Студент')
    materialId = models.ForeignKey(material, on_delete=models.CASCADE, verbose_name='Материал')
    disciplineId = models.ForeignKey(discipline, on_delete=models.CASCADE, verbose_name='Дисциплина')
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='', null=True, verbose_name='Оценка')
    countEdit = models.IntegerField(default=0)
    editOnScore = models.BooleanField(default=True)
    descriptionScore = models.CharField(max_length=255, null=True, blank=True, verbose_name='Доп. информация')

    class Meta:
        verbose_name = 'Оценку'
        verbose_name_plural = 'Оценки'

        constraints = [
            models.UniqueConstraint(fields=['disciplineId', 'materialId', 'studentId', 'teachIdToScore'],
                                    name="uniq-score")
        ]


class cronType(models.Model):
    id = models.AutoField(primary_key=True)
    cronTypeName = models.CharField(max_length=255, null=True, blank=True, verbose_name='Название и доп. информация')
    cronTypeFile = models.CharField(max_length=255, null=True, blank=True, verbose_name='Исполнительная единица')
    dateTimeInitCron = models.DateTimeField(null=True, blank=True, verbose_name='Дата исполнения')

    class Meta:
        verbose_name = 'Крон тип'
        verbose_name_plural = 'Крон типы'

    def __str__(self):
        return "%s %s" % (self.cronTypeName, self.cronTypeName)


class cronMysql(models.Model):
    id = models.AutoField(primary_key=True)
    dateIn = models.DateTimeField(auto_now=True, verbose_name='Дата события')
    cronTypeId = models.ForeignKey(cronType, on_delete=models.CASCADE, verbose_name='Тип крона')
    run = models.BooleanField(default=False, verbose_name='Исполняется')
    errorStatus = models.BooleanField(default=False, verbose_name='Исполнительный статус')
    errorInfo = models.CharField(max_length=255, null=True, blank=True, verbose_name='Доп. информация после исполнения')
