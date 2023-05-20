import os
import argparse

import search
import random
import textwrap

from colorama import init
from typing import Union


def reading_file(file_name: str = "") -> Union[str, bool]:
    """Чтение строки из файла"""
    file_strings = ""
    string = ""
    if not file_name:
        file_name = input(
            "Введите имя файла (с расширением), откуда нужно считать строку: ")

    if not os.path.exists(file_name):
        print("Такого файла не существует.")
        return False

    with open(file_name, "r", encoding='utf-8') as file:
        for line in file:
            file_strings += line

    if file_strings and file_strings != " " * len(file_strings):
        string = ''.join(file_strings.split("\n"))

    print("Считано из файла: ")

    for line in textwrap.wrap(string, width=120)[:10]:
        print(line)

    string = file_strings.replace('\n', '\\n')

    return string


def check_fields(string: str, lst_sub_strings: Union[str, list[str]],
                 case_sensitivity: bool, method: str, count: int) -> bool:
    """Проверка наличия значений у полей"""
    empty_fields = []
    if not string:
        empty_fields.append("Строка для поиска")

    if not lst_sub_strings:
        empty_fields.append("Подстроки для поиска")

    if case_sensitivity not in (True, False):
        empty_fields.append("Чувствительность к регистру")

    if not method:
        empty_fields.append("Метод поиска")

    if not count:
        empty_fields.append("Количество вхождений")

    if empty_fields:
        print("У вас отсутствуют следующие поля:")
        for field in empty_fields:
            print(f"\t{field}")
        return False

    return True


def colored_print_tuple(string: str, all_sub_strings: Union[str, list[str]],
                        result: Union[None, tuple, dict]) -> None:
    """Вывод для того случая, когда передана одна подстрока"""

    output_string = ""
    color = random.randint(31, 36)  # Берём все цвета, кроме чёрного и белого
    coloring_indexes = []  # Индексы символов, которые мы будем раскрашивать

    # Получаем индексы символов, которые мы будем раскрашивать
    for i in result:
        for j in range(i, i + len(all_sub_strings)):
            coloring_indexes.append(j)

    # Получаем пару (индекс, символ)
    for letter in enumerate(string):
        # Если символ по этому индексу необходимо раскрасить
        if letter[0] in coloring_indexes:
            letter = list(letter)

            output_string += f"\033[{color}m {letter[1]}\033[0m".replace(' ',
                                                                         '')
            continue

        output_string += letter[1]

    print("Найденные подстроки:")

    for line in textwrap.wrap(output_string, width=120)[:10]:
        print(line)

    print("Набор индексов начала каждой подстроки:")
    print(f"\033[{color}m{result}\033[0m")


def colored_print_dict(string: str, result: Union[None, dict]) -> None:
    """Печать нескольких подстрок"""
    count_row = 0  # Количество строк, которое выводится

    if not result:
        return None

    for key in result:  # Получаем ключи словаря

        output_string = ""
        color = random.randint(31,
                               36)  # Берём все цвета, кроме чёрного и белого
        coloring_indexes = []  # Индексы символов, которые мы будем раскрашивать

        if result[key]:  # Если подстрока найдена

            # Получаем индексы символов, которые мы будем раскрашивать
            for i in result[key]:
                for j in range(i, i + len(key)):
                    coloring_indexes.append(j)

            # Получаем пару (индекс, символ)
            for letter in enumerate(string):
                if letter[0] in coloring_indexes:
                    letter = list(letter)

                    output_string += f"\033[{color}m {letter[1]}\033[0m".replace(
                        ' ', '')
                    continue

                output_string += letter[1]

            print("Найденные подстроки:")

            for line in textwrap.wrap(output_string, width=120)[:10]:
                print(line)

            print("Набор индексов начала каждой подстроки:")
            print(f"\033[{color}m{key}: {result[key]}\033[0m")

        else:
            print("Найденные подстроки:")
            for line in textwrap.wrap(string, width=120)[:10]:
                print(line)
            print("Набор индексов начала каждой подстроки:")
            print(f"\033[{color}m{key}: {result[key]}\033[0m")


def colored_output(string: str, all_sub_strings: Union[str, list[str]],
                   result: Union[None, tuple, dict]) -> None:
    """Красивый вывод строк"""
    if isinstance(result, tuple):
        colored_print_tuple(string, all_sub_strings, result)
    else:
        colored_print_dict(string, result)


def search_substring_in_string(string: str, sub_strings: Union[str, list[str]],
                               case_sensitivity: bool, method: str,
                               count: int, threshold: int, process: int) -> None:
    """Вызов функции поиска из модуля"""

    if len(sub_strings) == 1:
        all_sub_strings = sub_strings[0]
    else:
        all_sub_strings = tuple(sub_strings)

    result = search.search(string, all_sub_strings, case_sensitivity, method,
                           count, threshold, process)

    if not result:
        print("Подстроки не найдены.")

    colored_output(string, all_sub_strings, result)


def parse_args():
    """Обработка параметров командной строки"""

    # Осуществляем разбор аргументов командной строки
    parser = argparse.ArgumentParser(description="Получение параметров для "
                                                 "нечеткого "
                                                 "поиска подстроки в введённой "
                                                 "строке")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", type=str, dest="file",
                       help="Путь до файла")
    group.add_argument("-s", "--string", type=str, dest="string",
                       help="Исходная строка")

    parser.add_argument("-rf", "--result-file", type=str, default=None,
                        dest="result_file", help="Файл для записи результата")

    parser.add_argument("-ss", "--sub_string", nargs="+", type=str,
                        dest="sub_string",
                        help="Одна или несколько подстрок, которые необходимо "
                             "найти")
    parser.add_argument("-cs", "--case_sensitivity", dest="case_sensitivity",
                        help="Чувствительность к регистру", action="store_true")
    parser.add_argument("-m", "--method", choices=("first", "last"),
                        dest="method",
                        help="Метод поиска", default="first")
    parser.add_argument("-c", "--count", type=int, dest="count",
                        help="Количество совпадений, которое нужно найти",
                        default=None)
    parser.add_argument("-t", "--threshold", type=int, dest="threshold",
                        default=1,
                        help="Максимальное количество ошибок")
    parser.add_argument("-p", "--process", type=int, dest="process",
                        default=None,
                        help="Количество процессов")

    # В эту переменную попадает результат разбора аргументов командной строки.
    args = parser.parse_args()

    if not (args.string or args.file):
        # Если не была передана строка или путь к файлу
        print("Укажите строку или путь к файлу.")
        return False

    if not args.sub_string:
        print("Укажите подстроки, которые необходимо искать.")
        return False

    string = ""

    if args.string:
        string = args.string

    elif args.file:
        string = reading_file(args.file)
        if not string:
            return False

    sub_strings = args.sub_string

    case_sensitivity = args.case_sensitivity

    method = args.method

    count = args.count

    if count and count < 0:
        print("Количество не может быть отрицательным числом.")
        return None

    threshold = args.threshold

    if args.threshold < 0:
        print("Количество ошибок не может быть отрицательным числом.")
        return None

    process = args.process

    if process and process < 0:
        print("Количество процессов не может быть отрицательным числом.")

    """
    result_file = args.result_file


    if result_file:
        try:
            rfile = open(result_file, "w", encoding="utf-8")
        except PermissionError:
            print("Ошибка при открытии файла для записи результата")
            return None
    """

    search_substring_in_string(string, sub_strings, case_sensitivity, method,
                               count, threshold, process)


def main() -> None:
    """Точка входа"""
    init()  # Инициализируем Colorama
    parse_args()


if __name__ == '__main__':
    main()
