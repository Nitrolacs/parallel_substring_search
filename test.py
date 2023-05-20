def SearchString(text, pattern, k):
    results = []  # создаем пустой список для результатов
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
            results.append(
                i - m + 1)  # добавляем индекс совпадения в список результатов
            # убираем break
    return results  # возвращаем список результатов


text = "себе субару бубубу"
pattern = "Бр"
k = 2

index = SearchString(text, pattern, k)
print(index)
