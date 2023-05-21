"""
Главный файл модуля
"""

import os
import argparse

import search
import random
import textwrap

from colorama import init
from typing import Union, TextIO


def reading_file(file_name: str = "") -> Union[str, bool]:
    """
    Чтение строки из файла
    :param file_name: название файла
    :return: считанная информация
    """
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


def colored_print_tuple(string: str, all_sub_strings: Union[str, list[str]],
                        result: Union[None, tuple, dict], rfile) -> None:
    """
    Вывод для того случая, когда передана одна подстрока
    :param string: Строка
    :param all_sub_strings: Подстроки
    :param result: Результат в виде индексов вхождений подстрок
    :param rfile: Результирующий файл
    :return: None
    """

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

    if rfile:
        rfile.write("Строка:\n" + str(string) + "\n")
        rfile.write("Подстрока:\n" + str(all_sub_strings) + "\n")
        rfile.write("Индексы найденной подстроки:\n" + str(result))
        rfile.close()


def colored_print_dict(string: str, result: Union[None, dict],
                       rfile: TextIO) -> None:
    """
    Печать нескольких подстрок
    :param string: Исходная строка
    :param result: Результат
    :param rfile: Результирующий файл
    :return: None
    """

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

                    output_string += f"\033[{color}m {letter[1]}\033[0m".\
                        replace(' ', '')
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

    if rfile:
        rfile.write("Строка:\n" + str(string) + "\n")
        rfile.write("Найденные подстроки:\n" + str(result)[1:-1])
        rfile.close()


def colored_output(string: str, all_sub_strings: Union[str, list[str]],
                   result: Union[None, tuple, dict], rfile: TextIO) -> None:
    """
    Красивый вывод строк
    :param string: строка
    :param all_sub_strings: подстроки
    :param result: результат
    :param rfile: результирующий файл
    :return: None
    """
    if isinstance(result, tuple):
        colored_print_tuple(string, all_sub_strings, result, rfile)
    else:
        colored_print_dict(string, result, rfile)


def search_substring_in_string(string: str, sub_strings: Union[str, list[str]],
                               case_sensitivity: bool, method: str,
                               count: int, threshold: int, process: int,
                               rfile: TextIO) -> None:
    """
    Вызов функции поиска из модуля
    :param string: Исходная строка
    :param sub_strings: Подстроки
    :param case_sensitivity: Чувствительность к регистру букв
    :param method: Метод поиска
    :param count: Количество вхождений
    :param threshold: Количество ошибок
    :param process: Количество процессов
    :param rfile: Результирующий файл
    :return: None
    """

    if len(sub_strings) == 1:
        all_sub_strings = sub_strings[0]
    else:
        all_sub_strings = tuple(sub_strings)

    result = search.search(string, all_sub_strings, case_sensitivity, method,
                           count, threshold, process)

    if not result:
        print("Подстроки не найдены.")

    colored_output(string, all_sub_strings, result, rfile)


def parse_args() -> None:
    """
    Обработка параметров командной строки
    :return: None
    """

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

    parser.add_argument("-rf", "--result_file", type=str, default=None,
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
                        default=0,
                        help="Максимальное количество ошибок")
    parser.add_argument("-p", "--process", type=int, dest="process",
                        default=None,
                        help="Количество процессов")

    # В эту переменную попадает результат разбора аргументов командной строки.
    args = parser.parse_args()

    if not (args.string or args.file):
        # Если не была передана строка или путь к файлу
        print("Укажите строку или путь к файлу.")
        return None

    if not args.sub_string:
        print("Укажите подстроки, которые необходимо искать.")
        return None

    string = ""

    if args.string:
        string = args.string

    elif args.file:
        string = reading_file(args.file)
        if not string:
            return None

    result_file = args.result_file
    rfile = None

    if result_file:
        try:
            rfile = open(result_file, "w", encoding="utf-8")
        except PermissionError:
            print("Не получается открыть файл для записи результата.")
            return None

    sub_strings = args.sub_string

    case_sensitivity = args.case_sensitivity

    method = args.method

    count = len(string)

    if args.count:
        if args.count > 0:
            count = args.count
        else:
            print("Количество не может быть отрицательным числом.")
            return None

    threshold = args.threshold

    if args.threshold < 0:
        print("Количество ошибок не может быть отрицательным числом.")
        return None

    process = None

    if args.process:
        if args.process > 0:
            process = args.process
        else:
            print("Количество процессов не может быть отрицательным числом.")
            return None

    search_substring_in_string(string, sub_strings, case_sensitivity, method,
                               count, threshold, process, rfile)


def main() -> None:
    """Точка входа"""
    init()  # Инициализируем Colorama
    parse_args()


if __name__ == '__main__':
    main()
