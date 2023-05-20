def SearchString(text, pattern, k):
    results = []  # создаем пустой список для результатов
    if pattern == []:
        return 0
    for p in pattern:  # добавляем цикл по элементам списка pattern
        m = len(p)  # изменяем m на длину текущей подстроки
        R = [0xFFFFFFFF for _ in range(k + 1)]
        patternMask = {}
        if p == "":
            return 0
        if m > 31:
            return -1  # Error: The pattern is too long!
        for i in range(m):
            patternMask[p[i]] = (patternMask.get(p[i], 0xFFFFFFFF) & ~(1 << i)) | (1 << m)  # добавляем еще один бит в начало маски для каждого символа подстроки
        for i in range(len(text)):
            oldRd1 = R[0]
            R[0] |= patternMask.get(text[i], 0xFFFFFFFF)
            R[0] <<= 1
            R[0] |= 1  # добавляем еще один бит в начало маски
            for d in range(1, k + 1):
                tmp = R[d]
                R[d] = (oldRd1 & (
                            R[d] | patternMask.get(text[i], 0xFFFFFFFF))) << 1
                R[d] |= 1  # добавляем еще один бит в начало маски
                oldRd1 = tmp
            if R[k] & (1 << (m + 1)) == 0:  # сравниваем с m + 1-м битом
                results.append((i - m + 1,
                                p))  # добавляем кортеж с индексом и подстрокой в список результатов
                # убираем break
    return results  # возвращаем список результатов


text = "abcaxyxz"
pattern = ['ab', 'a']
k = 0

result = SearchString(text, pattern, k)
print(result)
