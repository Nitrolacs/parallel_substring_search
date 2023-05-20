import logging
import time

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


def SearchString(text, pattern, k):
    result = -1
    m = len(pattern)
    R = [0xFFFFFFFF for _ in range(k + 1)]
    patternMask = {}
    if pattern == "":
        return 0
    if m > 31:
        return -1  # Error: The pattern is too long!
    for i in range(m):
        patternMask[pattern[i]] = patternMask.get(pattern[i], 0xFFFFFFFF) & ~(
                1 << i)
    for i in range(len(text)):
        oldRd1 = R[0]
        R[0] |= patternMask.get(text[i], 0xFFFFFFFF)
        R[0] <<= 1
        for d in range(1, k + 1):
            tmp = R[d]
            R[d] = (oldRd1 & (R[d] | patternMask.get(text[i], 0xFFFFFFFF))) << 1
            oldRd1 = tmp
        if R[k] & (1 << m) == 0:
            result = i - m + 1
            break
    return result


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

    information = dict()
    for word in sub_string_new:
        information[word] = []

    for word in sub_string_new:
        index = SearchString(string, word,
                             threshold)  # Используем функцию SearchString
        # для поиска первого вхождения слова с заданным порогом ошибок
        if index != -1:
            information[word].append(
                index)  # Добавляем индекс в список для данного слова

    if method == "last":  # Если нужно найти последнее вхождение
        for word in sub_string_new:
            index = SearchString(string[::-1], word[::-1],
                                 threshold)  # Ищем первое вхождение обратной
            # строки с заданным порогом ошибок
            if index != -1:
                information[word].append(len(string) - index - len(
                    word))  # Добавляем индекс последнего вхождения для
                # данного слова

    for key, item in information.items():
        if item:
            information[key] = tuple(item[
                                     :count])  # Оставляем только count первых или последних индексов для каждого слова
        else:
            information[key] = None

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
