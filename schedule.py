import requests
from bs4 import BeautifulSoup

# Возвращает список групп с сайта вуза
def get_groups():
    page = requests.get('http://inet.ibi.spb.ru/raspisan/menu.php?tmenu=12&cod=0')
    soup = BeautifulSoup(page.text, 'html.parser')
    group_options = soup.find_all('option')
    groups = {i.text: i.get('value') for i in group_options}
    return groups

# Заменяет слова в тексте расписания на более приятные пользователю
# Получает строку с текстом про предмет
# Возвращает переделанную строку
def beautifier(subject):
    subject = subject.replace('-Экз', '(ЭКЗАМЕН)')
    subject = subject.replace('-Конс', '(Консультация)')
    subject = subject.replace('-ДифЗ', '(ДИФ ЗАЧЕТ)')
    subject = subject.replace('-Зач', '(ЗАЧЕТ)')
    subject = subject.replace('-Лекц', '(Лекция)')
    subject = subject.replace('-Прак', '(Практика)')
    subject = subject.replace('ауд. Дистанцион', 'Дистант')
    subject = subject.replace('--------', '\n\t\t')
    return subject

# Получает нужную дату и номер группы
# Возвращает html страницу с расписанием с сайта вуза
def get_schedule_page(date, group_id):
    URL = 'http://inet.ibi.spb.ru/raspisan/rasp.php'
    date = date.format('DD.MM.YYYY')
    page = requests.post(URL, data = {
            'rtype': 1, 
            'group' : group_id,
            'datafrom' : date,
            'dataend' : date}
        )
    return page

# Преобразовывает html в строку с расписанием, готовую для отправки пользователю
# Получет html страницу
# Возвращает строку с расписанием
def get_schedule_str(schedule_page):
    soup = BeautifulSoup(schedule_page.text, 'html.parser')

    if soup.get_text() == 'Информации для отображения отчета не обнаружено! Измените период.':
        # В случаях, когда на сайте вуза не отображается информация по техническим причинам со стороны вуза,
        # будет невозможно получить не только расписание, но и список групп. 
        # Проверка на наличие списка групп поможет не сообщать ложно об отсутствии занятий
        if not get_groups():
            return 'Сайт вуза лагает. Напиши позже :)'
        return 'Нет занятий. Отдыхай :з'
        
    #  Для удобства будем работать не со всем текстом, а с ячейками таблицы
    td_tags = soup.find_all('td') 
    td_tags = [tag.get_text() for tag in td_tags]

    #  Первые две ячейки - ненужный текст
    td_tags = td_tags[2:]

    mid = len(td_tags) // 2
    #  Первая половина ячеек - временной диапазон занятий
    time = td_tags[:mid]
    #  Средний элемент - дата
    schedule = td_tags[mid] + '\n\n'
    #  Вторая половина ячеек - названия дисциплин
    subjects = td_tags[mid+1:]

    # Собираем все в текст сообщения
    for i in range(mid):
        schedule += '⏰ '
        schedule += time[i]
        schedule += '\t'
        # Если пробел - пустое окно в ячейке
        if subjects[i] == u'\xa0':
            schedule += 'Окно. Отдыхай :з'
        else:
            schedule += beautifier(subjects[i])
        schedule += '\n\n'

    return schedule

# Получает нужную дату и номер группы
# Возвращает строку с расписанием, готовую для отправки пользователю
def get_schedule(date, group_id):
    schedule_page = get_schedule_page(date, group_id)
    return get_schedule_str(schedule_page)