"""Модуль, реализующий функцию вычисления семестра по названию группы."""

import re
from datetime import datetime


def extract_semester_from_group_name(group_name: str) -> int:
    """
    Функция, вычисляющая семестр из названия группы.

    Например, если пришло наименование "КИ21-16/2Б", то на момент 18.05.2025
    это семестр №8.

    :param group_name: наименование студенческой группы (каждая группа в СФУ
        содержит в своем названии номер года поступления)
    :return: номер семестра
    """

    match = re.search(r"\D*(\d+)", group_name)
    if not match:
        return 0

    try:
        year_of_assignment = int(match.group(1))
    except ValueError:
        return 0

    admission_year = 2000 + year_of_assignment
    now = datetime.now()

    current_year = now.year
    current_month = now.month  # Январь = 1, Сентябрь = 9

    # 1 сентября года поступления
    admission_date = datetime(admission_year, 9, 1)

    if now > admission_date:
        full_years = (
            current_year - admission_year - (1 if current_month < 9 else 0)
        )
    else:
        return -1

    first_semester_months = {9, 10, 11, 12, 1, 2}

    if current_month in first_semester_months:
        return full_years * 2 + 1
    else:
        return full_years * 2 + 2
