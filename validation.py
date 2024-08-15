from datetime import datetime




def validation_number(number = str):
    if len(number) == 11 and number[0] == '7' and number.isnumeric():
        return True
    else:
        return "Некорректный формат номера. Выполни запрос повторно с корректным номером в формате 7**********"

def is_valid_date(data_from, data_to):
    date_format = '%d.%m.%Y'
    if data_from == data_to:
        return "Дата конца не должна равняться дате начала. Выполни запрос повторно"
    try:
        a = datetime.strptime(data_from, date_format)
        b = datetime.strptime(data_to, date_format)
        if not((b-a).days<=7 and (b-a).days>=1):
            return "Между датами должно быть от 1 до 7 дней"
        return True
    except ValueError:
        return "Некорректный формат даты. Выполни запрос повторно с корректной датой в формате дд.мм.гггг"

def is_valid_date_new(data_from):
    date_format = '%d.%m.%Y'
    try:
        datetime.strptime(data_from, date_format)
        return True
    except ValueError:
        return "Некорректный формат даты. Выполни запрос повторно с корректной датой в формате дд.мм.гггг"


def is_valid_summa(summa):

    if str(summa).isnumeric() and int(summa) > 0:
        return True
    else:
        return "Некорректная сумма. Сумма должна быть больше 0"
