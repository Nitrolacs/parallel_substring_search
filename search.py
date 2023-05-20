import logging
import time
import multiprocessing  # импортируем модуль multiprocessing
import sys

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


def bitap_search(text, pattern, k):
    text = " " + text  # Чтобы учитывались символы в начале

    results = []  # создаем пустой список для результатов
    if not pattern:
        return 0
    for p in pattern:  # добавляем цикл по элементам списка pattern
        m = len(p)  # изменяем m на длину текущей подстроки
        R = [0xFFFFFFFF for _ in range(k + 1)]
        patternMask = {}
        if p == "":
            return 0
        if m > 31 or m > len(text):
            print("Превышен размер подстроки. Завершение программы...")
            sys.exit(0)  # Error: The pattern is too long!
        for i in range(m):
            patternMask[p[i]] = patternMask.get(p[i], 0xFFFFFFFF) & ~(
                    1 << i)
        for i in range(len(text)):
            oldRd1 = R[0]
            R[0] |= patternMask.get(text[i], 0xFFFFFFFF)
            R[0] <<= 1
            for d in range(1, k + 1):
                tmp = R[d]
                R[d] = (oldRd1 & (
                        R[d] | patternMask.get(text[i], 0xFFFFFFFF))) << 1
                oldRd1 = tmp
            if R[k] & (1 << m) == 0:
                results.append((i - m,
                                p))  # добавляем кортеж с индексом и подстрокой в список результатов
                # убираем break
    return results  # возвращаем список результатов


def worker(text_part, pattern, k):  # добавляем параметр k в функцию worker
    return bitap_search(text_part, pattern,
                        k)  # передаем k в функцию bitap_search


def merge(results):  # функция merge не меняется
    merged_results = []
    offset = 0
    for result in results:
        for pair in result:
            merged_results.append((pair[0] + offset, pair[1]))
        offset += len(result)
    return merged_results


@timeit
def search(string: str, sub_string: str or tuple, case_sensitivity: bool,
           method: str, count: int, threshold: int, process: int):
    """Шаблон функции поиска"""

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
        result = bitap_search(string, sub_string_new, threshold)

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
