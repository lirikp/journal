from django import template
from journal.models import material, student
from datetime import datetime, timedelta

from django.contrib.auth.models import Group

register = template.Library()


@register.simple_tag(takes_context=True)
def define(context, val=None):
    return val


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='check_itogo')
def check_itogo(data):
    return True if (float(data[3]) == 0.0 and float(data[6]) == 0.0) else False


@register.filter
def convert_str_date(value):
    return datetime.strptime(value, '%Y%m%d').date()


@register.filter
def date_minus_one_day(value):
    value += timedelta(days=-1)

    return value


# @register.assignment_tag(takes_context=True)
@register.simple_tag(takes_context=True)
def count_materials(context, material_table):
    return len(material_table)


def make_data_workload(table_workload):
    semestr_dict = {
        'семестр 1': {
            9: 'сентябрь',
            10: 'октябрь',
            11: 'ноябрь',
            12: 'декабрь',
            1: 'январь',
        },
        'семестр 2': {
            2: 'февраль',
            3: 'март',
            4: 'апрель',
            5: 'май',
            6: 'июнь',

        }
    }
    table_dict = {}
    year_byd, year_pay = (0, 0)
    for semestr, semestr_dict in semestr_dict.items():
        semestr_itogo_bud, semestr_itogo_pay = (0, 0)

        for num, mounth in semestr_dict.items():
            table_dict[mounth] = [0, 0]
            find_bud = False
            find_pay = False
            for data in table_workload:
                month = int(data[0].split('-')[1])
                if not find_bud and month == num and data[1] == 0:
                    table_dict[mounth][0] = data[2]
                    semestr_itogo_bud += data[2]
                    find_bud = True
                    continue

                if not find_pay and month == num and data[1] == 1:
                    table_dict[mounth][1] = data[2]
                    find_pay = True
                    semestr_itogo_pay += data[2]

            if not find_bud:
                table_dict[mounth][0] = 0

            if not find_pay:
                table_dict[mounth][1] = 0

        table_dict[f'Итого {semestr}'] = [0, 0]
        table_dict[f'Итого {semestr}'][0] = semestr_itogo_bud
        table_dict[f'Итого {semestr}'][1] = semestr_itogo_pay
        year_byd += semestr_itogo_bud
        year_pay += semestr_itogo_pay

    table_dict[f'Итого'] = [0, 0]
    table_dict[f'Итого'][0] = year_byd
    table_dict[f'Итого'][1] = year_pay

    return table_dict


@register.simple_tag(takes_context=True)
def make_workload(context, table_workload):
    return make_data_workload(table_workload)


@register.simple_tag(takes_context=True)
def make_workload_all(context, table_workload):
    table_dict = {}
    last_id_teach = table_workload[0][0]
    teach_workload = []
    last_empty_teacher = False

    def load_to_table_dict(name_teach, tmp, table_dict, dep, change_dep, id):
        if tmp == None:
            table_dict[name_teach] = (dep, 0, 0, 0, 0, 0, 0, change_dep, id)
        else:
            table_dict[name_teach] = (
                dep, tmp['Итого семестр 1'][0], tmp['Итого семестр 2'][0], tmp['Итого'][0], tmp['Итого семестр 1'][1],
                tmp['Итого семестр 2'][1], tmp['Итого'][1], change_dep, id)

        return table_dict

    def make_data_dict_workload(tuple_workload):
        out = {}
        last_id = -1
        for _ in tuple_workload:
            if last_id != _[0]:
                id = 0
                out[_[0]] = []

            out[_[0]].append(
                {'fio': _[1], 'dep': _[2], 'date': _[3], 'pay': _[4], 'count_hour': _[5], 'dep_id': _[6]})
            last_id = _[0]

        return out

    dep_id, last_dep_id, change_dep, teach_id = (1, 1, 0, 0,)

    for id, item in make_data_dict_workload(table_workload).items():
        dep_id = item[0]['dep_id']
        if dep_id != last_dep_id:
            change_dep = 1
            teach_id = 1
        else:
            change_dep = 0
            teach_id = teach_id + 1

        last_dep_id = dep_id
        if item[0]['date'] == None and item.__len__() == 1:
            table_dict = load_to_table_dict(item[0]['fio'], None, table_dict, item[0]['dep'], change_dep, teach_id)
            continue

        if item.__len__() >= 1:
            teach_workload = []
            for _ in item:
                teach_workload.append((_['date'], _['pay'], _['count_hour']))

            table_dict = load_to_table_dict(_['fio'], make_data_workload(teach_workload), table_dict, _['dep'],
                                            change_dep, teach_id)

    return table_dict


@register.simple_tag(takes_context=True)
def makeFIO(context, data):
    return f"{data.teacher_lastName} {data.teacher_firstName[:1]}. {data.teacher_partonymic[:1]}."


@register.simple_tag(takes_context=True)
def text_week_day(context, week_day, check):
    if check:
        return week_day
    else:
        week = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: 'Четверг', 5: 'Пятница', 6: 'Суббота',
                7: 'Воскресенье', 8: 'Рассредоточено', }
        return week[week_day]


@register.simple_tag(takes_context=True)
def type_lesson(context, _table, m_id):
    text_type = _table[3][m_id]
    return text_type
    # if text_type != 'lesson':
    #     return True
    # else:
    #     return False


@register.simple_tag(takes_context=True)
def count_students_from_discipline(context, _table):
    data = {}
    dates = {}
    students = []
    type_lesson_list = {}
    for id, student in enumerate(_table):

        data_temp = {
            'discipline_id': student.discipline_id,
            'material_id': student.material_id,
            'meetName': student.meetName,
            'student_id': student.student_id,
            'teacher_id': student.teacher_id,
            'result': student.result if student.result else None,
            'descriptionScore': student.descriptionScore if student.descriptionScore else '',
            'status_in_study': student.status_in_study,
        }
        if ' '.join([student.lastName, student.firstName, ]) in data:
            data[' '.join([student.lastName, student.firstName, ])][student.dateInit] = data_temp
        else:
            students.append(' '.join([student.lastName, student.firstName, ]))
            data[' '.join([student.lastName, student.firstName, ])] = {student.dateInit: data_temp}

        if not student.dateInit in dates:
            dates[student.dateInit] = student.material_id

        type_lesson_list[student.material_id] = student.meetName

    return {k: dates[k] for k in sorted(dates)}, students, data, type_lesson_list


@register.simple_tag(takes_context=True)
def take_score_students_from_data(context, _data):
    return _data[2]


@register.simple_tag(takes_context=True)
def take_dates_students_from_data(context, _data):
    return _data[0]


@register.simple_tag(takes_context=True)
def take_data_from_data_report_scorecard(context, _data):
    return _data[0]


@register.simple_tag(takes_context=True)
def counter_add(context, cnt, clear=False):
    if clear:
        return 1
    else:
        return cnt + 1


@register.simple_tag(takes_context=True)
def count_hours(context, material_table):
    hours = 0
    for item in material_table:
        hours += item.countHour
    return hours


def float_hours(minutes):
    if (minutes >= 20 and minutes <= 25):
        return 0.5
    elif (minutes >= 65 and minutes <= 70):
        return 1.5
    elif (minutes >= 110 and minutes <= 115):
        return 2.5
    elif (minutes >= 155 and minutes <= 160):
        return 3.5
    elif (minutes > 200 and minutes < 205):
        return 4.5
    else:
        return minutes // 45


@register.simple_tag(takes_context=True)
def count_hour(context, data):
    diff = (data.timeFinishLecture.hour * 60 + data.timeFinishLecture.minute) - (
            data.timeStartLecture.hour * 60 + data.timeStartLecture.minute)
    h = float_hours(diff)
    return h


@register.simple_tag(takes_context=True)
def count_hours_add(context, sum, hour):
    akk_hours = float_hours(((hour.timeFinishLecture.hour * 60 + hour.timeFinishLecture.minute) - (
            hour.timeStartLecture.hour * 60 + hour.timeStartLecture.minute)))
    return sum + akk_hours


@register.simple_tag(takes_context=True)
def get_value_from_dict_matrix(context, data, item, date):
    value = ' '
    if date in data[item]:
        value = data[item][date]

    return value


@register.simple_tag(takes_context=True)
def get_teach_name(context, data, item):
    dict_keys = data[item].keys()
    first_elem_key = list(dict_keys)[:1]
    value = data[item][first_elem_key[0]]
    return value['teach_name']


@register.simple_tag(takes_context=True)
def get_value_from_simple_matrix(context, data, item, fio):
    value = ' '
    if item in data[fio]:
        value = data[fio][item]['result']

    return value


@register.simple_tag(takes_context=True)
def get_status_from_simple_matrix(context, data, item, fio):
    status = 0
    if item in data[fio]:
        status = data[fio][item]['status']

    return status


@register.simple_tag(takes_context=True)
def get_title_from_simple_matrix(context, data, item, fio):
    title = ''
    if item in data[fio]:
        title = data[fio][item]['title']

    return title

@register.simple_tag(takes_context=True)
def get_meetName_from_simple_matrix(context, data, item, fio):
    meetName = ''
    if item in data[fio]:
        meetName = data[fio][item]['meetName']

    return meetName


@register.simple_tag(takes_context=True)
def report_student_all_scores(context, _table):
    data = {}
    dates = {}
    nameDiscipline = []
    student_name = ''
    course = ''

    for id, row in enumerate(_table):
        if id == 0:
            student_name = " ".join((row.lastName, row.firstName))
            course = row.course

        teach_name = " ".join((row.prep_lastName, row.prep_firstName[0:1] + '.', row.prep_partonymic[0:1] + '.'))

        if row.nameDiscipline in data:
            data[row.nameDiscipline][row.dateInit] = {'result': row.result,
                                                      'teach_name': teach_name,
                                                      'descriptionScore': row.descriptionScore,
                                                      'meet_id': row.meetId, }
        else:
            nameDiscipline.append(row.nameDiscipline)
            data[row.nameDiscipline] = {row.dateInit: {'result': row.result,
                                                       'teach_name': teach_name,
                                                       'descriptionScore': row.descriptionScore,
                                                       'meet_id': row.meetId, }
                                        }

        if not row.dateInit in dates:
            dates[row.dateInit] = ""

    return student_name, {k: dates[k] for k in sorted(dates)}, nameDiscipline, data, course


@register.simple_tag(takes_context=True)
def make_data_from_report_scorecard(context, _table):
    data = {}
    items = {}

    for row in _table:
        student_name = " ".join((row.lastName, row.firstName))

        if student_name in data:
            if row.item_id in data[student_name]:
                if data[student_name][row.item_id]['meet_id'] in [3, 4]:
                    data[student_name][row.item_id] = {'result': row.result, 'meet_id': row.meet_id,
                                                       'date': row.dateInit, 'status': row.status,
                                                       'title': ' '.join([row.t_l, row.t_f]),
                                                       'meetName': row.meetName}
            else:
                data[student_name][row.item_id] = {'result': row.result, 'meet_id': row.meet_id, 'date': row.dateInit,
                                                   'status': row.status, 'title': ' '.join([row.t_l, row.t_f]),
                                                   'meetName': row.meetName}
        else:
            data[student_name] = {
                row.item_id: {'result': row.result, 'meet_id': row.meet_id, 'date': row.dateInit, 'status': row.status,
                              'title': ' '.join([row.t_l, row.t_f]),
                              'meetName': row.meetName}}

        if not row.item_id in items:
            items[row.item_id] = row.itemName

    return {k: items[k] for k in sorted(items)}, data


@register.simple_tag(takes_context=True)
def takes_data_for_material_list_manager(context, id):
    return material.objects.filter(discipMaterialId=id)


@register.simple_tag(takes_context=True)
def compare_dates_with_now(context, d):
    return d < datetime.today().date()


@register.simple_tag(takes_context=True)
def takes_data_for_discipline_list_manager(context, id):
    now_day = datetime.today()
    return student.objects.raw(
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
        [id, now_day.strftime('%Y-%m-%d')])
