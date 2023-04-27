import time

import logging
from typing import Optional

logging.basicConfig(
    level=logging.DEBUG,
    filename='myProgramLog.txt',
    format=' %(asctime)s - %(levelname)s - %(message)s')


def timeit(method):
    """Логирует время работы функции"""

    def timed(*args):
        ts = time.perf_counter()
        result = method(*args)
        te = time.perf_counter()
        running_time = f"{te - ts:0.4f}"

        logging.debug('%r %r %r sec' % (method.__name__, args, running_time))
        return result

    return timed


# Класс Bitap
class Bitap:
    # Конструктор класса
    def __init__(self, patterns):
        # Сохраняем список подстрок для поиска
        self.patterns = patterns
        # Вычисляем минимальную длину подстроки
        self.m = min(len(pattern) for pattern in patterns)
        # Выбираем количество подшаблонов
        self.s = 2
        # Вычисляем длину каждого подшаблона
        self.t = self.m // self.s
        # Вычисляем хеш-значения и сдвиги для каждого подшаблона каждой подстроки
        self.h = []
        self.shift = []
        for pattern in patterns:
            h = [self.hash_pattern(pattern, i * self.t, (i + 1) * self.t) for i
                 in range(self.s)]
            shift = [self.t * (self.s - i - 1) for i in range(self.s)]
            self.h.append(h)
            self.shift.append(shift)

    # Метод для вычисления хеш-значения подстроки
    def hash_pattern(self, pattern, i, j):
        h = 0
        for k in range(i, j):
            h = h * 256 + (ord(pattern[k]) - ord('a'))
        return h

    # Метод для поиска подстрок в тексте
    def get_keywords_found(self, text):
        # Вычисляем длину текста
        n = len(text)
        # Создаем список для хранения результатов поиска
        results = []
        # Итерация по тексту
        for i in range(n - self.m + 1):
            # Итерация по подстрокам
            for j, pattern in enumerate(self.patterns):
                # Флаг совпадения подшаблонов
                subpatterns_match = True
                # Итерация по подшаблонам
                for k in range(self.s):
                    # Если хеш-значение подшаблона не совпадает с хеш-значением фрагмента текста
                    if self.hash_pattern(text, i + k * self.t,
                                         i + (k + 1) * self.t) != self.h[j][k]:
                        # Несовпадение подшаблона
                        subpatterns_match = False
                        break
                # Если все подшаблоны совпали
                if subpatterns_match:
                    # Если полная подстрока совпадает с фрагментом текста
                    if text[i:i + self.m] == pattern:
                        # Добавляем результат в список в формате (индекс начала найденной подстроки, значение подстроки)
                        results.append((i, pattern))
                    # Сдвиг на длину подстроки
                    i += self.m
                else:
                    # Сдвиг на соответствующее значение из массива сдвигов
                    i += self.shift[j][k]
        # Возвращаем список результатов поиска
        return results


@timeit
def search(string: str, sub_string: str or tuple, case_sensitivity: bool,
           method: str, count: int, threshold: int, n_process: Optional[int]):
    """Шаблон функции поиска"""

    if count == 0 or n_process == 0:
        return {}


    if not case_sensitivity:
        string = string.lower()

        sub_string = list([word.lower() for word in sub_string])

    # Создаем пустой набор для хранения возможных длин подстрок
    possible_lengths = set()
    # Вычисляем длину исходной строки
    string_length = len(string)
    # Перебираем все подстроки из списка
    for substring in sub_string:
        # Вычисляем длину подстроки
        substring_length = len(substring)
        # Определяем диапазон допустимых длин подстрок с учетом параметра threshold
        min_length = substring_length - threshold
        max_length = substring_length + threshold
        # Добавляем все целые числа из этого диапазона в набор possible_lengths
        possible_lengths |= set(range(min_length if min_length > 1 else 1,
                                      (max_length if max_length < string_length
                                       else string_length) + 1))

    if isinstance(sub_string, str):
        sub_string_new = [sub_string]
        bitap = Bitap(sub_string_new)
    else:
        bitap = Bitap(list(sub_string))

    result = bitap.get_keywords_found(string)

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

    if len(information) == 0:
        information = None
    elif isinstance(information, dict):
        is_value = False
        for _, value in information.items():
            if value is not None:
                is_value = True
        if not is_value:
            information = None

    return information
