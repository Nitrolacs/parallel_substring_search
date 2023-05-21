"""
Модуль поиска с помощью алгоритма Bitap
"""

import logging
import time
import multiprocessing  # импортируем модуль multiprocessing

from typing import List, Tuple, Dict, Any, Callable

logging.basicConfig(
    level=logging.DEBUG,
    filename='myProgramLog.txt',
    format=' %(asctime)s - %(levelname)s - %(message)s')


def timeit(method: Callable) -> Callable:
    """
    Логирует время работы функции.
    :param method: функция, время работы которой нужно замерить
    :return: обернутая функция, которая логирует свое время работы
    """

    def timed(*args):
        ts = time.perf_counter()
        result = method(*args)
        te = time.perf_counter()
        running_time = f"{te - ts:0.4f}"

        logging.debug('%r %r %r sec' % (method.__name__, args, running_time))
        return result

    return timed


def bitap_search_multiple(haystack: str, needle: List[str], threshold: int) -> \
        List[Tuple[int, str]]:
    """
    Функция для поиска нескольких подстрок в строке с
    допустимым количеством ошибок.
    :param haystack: строка, в которой ищем подстроки
    :param needle: список подстрок, которые ищем
    :param threshold: количество ошибок, которые допускаем при сравнении
    :return: список кортежей, где первый элемент - индекс
     начала вхождения подстроки в строку, а второй элемент - сама подстрока
    """
    # Результат - список кортежей
    result = []

    # Для каждой подстроки из списка
    for pattern in needle:
        # Ищем вхождения подстроки в строку с помощью функции bitap_search
        tmp_result = bitap_search(haystack, pattern, threshold)
        # Сортируем список индексов по возрастанию
        tmp_result.sort()
        # Для каждого индекса из списка
        for index in tmp_result:
            # Добавляем кортеж из индекса и подстроки в результат
            result.append((index, pattern))

    return result


def bitap_search(haystack: str, needle: str, threshold: int) -> List[int]:
    """
    Функция для поиска подстроки в строке с допустимым количеством ошибок
    с помощью двоичного алгоритма Bitap.
    :param haystack: строка, в которой ищем подстроку
    :param needle: подстрока, которую ищем
    :param threshold: количество ошибок, которые допускаем при сравнении
    :return: список индексов, где начинаются вхождения подстроки в строку
    """
    # Длина строки и подстроки
    haystackLen = len(haystack)
    needleLen = len(needle)
    # Результат - список индексов вхождений
    result = []

    def _generateAlphabet(needle, haystack):
        """
        Вспомогательная функция для генерации алфавита
        Алфавит - это словарь, где ключи - буквы строки,
        а значения - битовые маски, показывающие позиции буквы в подстроке
        :param needle: подстрока
        :param haystack: строка
        :return:
        """
        alphabet = {}
        for letter in haystack:
            if letter not in alphabet:
                letterPositionInNeedle = 0
                for symbol in needle:
                    # Сдвигаем маску на один бит влево
                    letterPositionInNeedle = letterPositionInNeedle << 1
                    # Устанавливаем младший бит в 1, если буква не
                    # совпадает с символом
                    letterPositionInNeedle |= int(letter != symbol)
                alphabet[letter] = letterPositionInNeedle
        return alphabet

    # Генерируем алфавит по строке и подстроке
    alphabet = _generateAlphabet(needle, haystack)

    # Создаем таблицу Битапа - двумерный список битовых масок
    # Первый индекс - по k (количеству ошибок, нумерация начинается с 1),
    # второй индекс - по столбцам (буквам строки)
    table = []

    # Пустая маска - все биты установлены в 1
    emptyColumn = (2 << (needleLen - 1)) - 1

    # Генерируем нижний уровень таблицы - для k = 0
    underground = []
    [underground.append(emptyColumn) for i in range(haystackLen + 1)]
    table.append(underground)

    # Выполняем точное совпадение - для k = 1
    k = 1
    table.append([emptyColumn])
    for columnNum in range(1, haystackLen + 1):
        # Сдвигаем предыдущую маску на один бит вправо
        prevColumn = (table[k][columnNum - 1]) >> 1
        # Получаем маску для текущей буквы строки по алфавиту
        letterPattern = alphabet[haystack[columnNum - 1]]
        # Объединяем маски побитовым ИЛИ
        curColumn = prevColumn | letterPattern
        table[k].append(curColumn)
        # Проверяем младший бит текущей маски - если он равен 0,
        # значит есть точное совпадение подстроки и подпоследовательности строки
        if (curColumn & 0x1) == 0:
            # Вычисляем индекс начала вхождения подстроки в строку
            index = columnNum - needleLen
            # Добавляем индекс в результат, если его там еще нет
            if index not in result:
                result.append(index)

    # Выполняем нечеткое сравнение с расчетом расстояния Левенштейна - для
    # k от 2 до threshold + 1
    for k in range(2, threshold + 2):
        table.append([emptyColumn])
        for columnNum in range(1, haystackLen + 1):
            # Сдвигаем предыдущую маску на один бит вправо
            prevColumn = (table[k][columnNum - 1]) >> 1
            # Получаем маску для текущей буквы строки по алфави
            letterPattern = alphabet[haystack[columnNum - 1]]
            # Объединяем маски побитовым ИЛИ
            curColumn = prevColumn | letterPattern
            # Вычисляем маски для операций вставки, удаления и замены символов
            insertColumn = curColumn & (table[k - 1][columnNum - 1])
            deleteColumn = curColumn & (table[k - 1][columnNum] >> 1)
            replaceColumn = curColumn & (table[k - 1][columnNum - 1] >> 1)
            # Объединяем маски для операций побитовым И и получаем
            # итоговую маску для текущего k и столбца
            resColumn = insertColumn & deleteColumn & replaceColumn
            table[k].append(resColumn)
            # Проверяем младший бит итоговой маски - если он равен 0,
            # значит есть нечеткое совпадение подстроки и подпоследовательности
            # строки с k ошибками или меньше
            if (resColumn & 0x1) == 0:
                # Вычисляем индекс начала вхождения подстроки в строку с учетом
                # операции замены символа
                startPos = max(0, columnNum - needleLen - 1)
                # Добавляем индекс в результат, если его там еще нет
                if startPos not in result:
                    result.append(startPos)
    return result


def worker(text_part: str, pattern: List[str], threshold: int) \
        -> List[Tuple[int, str]]:
    """
    Поиск нескольких подстрок в части строки с допустимым количеством ошибок.
    :param text_part: часть строки, в которой ищем подстрок
    :param pattern: список подстрок, которые ищем
    :param threshold:  количество ошибок, которые допускаем при сравнении
    :return:
    """
    # Передаём параметры в функцию
    return bitap_search_multiple(text_part, pattern,
                                 threshold)


def merge(results: List[List[Tuple[int, str]]]) -> List[Tuple[int, str]]:
    """
    Функция для объединения результатов поиска по нескольким частям строки.
    :param results: список списков кортежей, где каждый список соответствует
                    одной части строки, а каждый кортеж содержит индекс начала
                    вхождения подстроки в часть строки и саму подстроку
    :return: список кортежей, где первый элемент - индекс начала вхождения
             подстроки в исходной строке,
             а второй элемент - сама подстрока
    """
    merged_results = []
    offset = 0
    for result in results:
        for pair in result:
            merged_results.append((pair[0] + offset, pair[1]))
        offset += len(result)
    return merged_results


@timeit
def search(string: str, sub_string: str or tuple, case_sensitivity: bool,
           method: str, count: int, threshold: int, process: int) \
        -> Tuple[int] or Dict[str, Tuple[int]] or None:
    """
    Функция поиска
    :param string: строка, в которой ищем подстроки
    :param sub_string: одна подстрока или кортеж из нескольких
                       подстрок, которые ищем
    :param case_sensitivity: флаг регистрозависимости поиска
    :param method: метод поиска - "first" или "last"
    :param count: количество индексов начала вхождений подстроки или подстрок,
                  которые нужно вернуть
    :param threshold: количество ошибок, которые
                      допускаем при сравнении
    :param process: количество процессов для параллельного поиска
    :return: кортеж из индексов начала вхождений либо словарь, где ключи -
             подстроки, а значения - кортежи из индексов начала вхождений.
    """

    if not case_sensitivity:
        string = string.lower()

        if isinstance(sub_string, tuple):
            sub_string = tuple([word.lower() for word in sub_string])
        else:
            sub_string = sub_string.lower()

    if isinstance(sub_string, str):
        sub_string_new = [sub_string]
    else:
        sub_string_new = list(sub_string)

    if process:
        pool = multiprocessing.Pool(
            processes=process)  # создаем пул процессов с заданным количеством
        # process
        text_parts = [string[i:i + len(string) // process] for i in
                      range(0, len(string),
                            len(string) // process)]  # разбиваем текст на равные
        # части по длине

        # Умножаем на process, чтобы создать список из process
        # одинаковых элементов.
        # Это нужно для того, чтобы функция zip смогла сопоставить каждой части
        # текста один и тот же список подстрок.
        results = pool.starmap(worker, zip(text_parts, [sub_string_new] * process, [
            threshold] * process))  # передаем threshold в качестве параметра k
        # для каждого процесса
        result = merge(
            results)  # используем функцию merge для объединения списка
        # результатов в один
    else:
        result = bitap_search_multiple(string, sub_string_new, threshold)

    # если искали несколько подстрок - формируем словарь с
    # результатами по каждой подстроке
    if isinstance(sub_string, tuple):
        counter = 0

        if method == "last":
            result = result[::-1]

        information = dict()
        for word in sub_string:
            information[word] = []

        for pair in result:
            counter += 1
            if counter <= count:
                information[pair[1]].append(pair[0])

        for key, item in information.items():
            if item:
                information[key] = tuple(item)
            else:
                information[key] = None
    # если искали одну подстроку - формируем кортеж с результатами
    else:
        information = []

        for item in result:
            information.append(item[0])

        if method == "last":
            information = list(information[::-1])[:count]
        elif method == "first":
            information = list(information[:count])

        if information:
            information = tuple(information)

    # если ничего не нашли - возвращаем None
    if len(information) == 0:
        information = None
    # если нашли несколько подстрок - проверяем есть ли хоть одна
    # непустая запись в словаре
    elif isinstance(information, dict):
        is_value = False
        for _, value in information.items():
            if value is not None:
                is_value = True
        # если все записи пустые - возвращаем None
        if not is_value:
            information = None

    return information
