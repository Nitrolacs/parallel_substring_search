def bitapSearchMultiple(haystack, needle, maxErrors):
    result = []

    for p in needle:
        tmp_result = bitap_search(haystack, p, maxErrors)
        tmp_result.sort()
        for index in tmp_result:
            result.append((index, p))

    return result


def bitap_search(haystack, needle, maxErrors):
    haystackLen = len(haystack)
    needleLen = len(needle)
    result = []

    def _generateAlphabet(needle, haystack):
        alphabet = {}
        for letter in haystack:
            if letter not in alphabet:
                letterPositionInNeedle = 0
                for symbol in needle:
                    letterPositionInNeedle = letterPositionInNeedle << 1
                    letterPositionInNeedle |= int(letter != symbol)
                alphabet[letter] = letterPositionInNeedle
        return alphabet

    alphabet = _generateAlphabet(needle, haystack)

    table = []  # first index - over k (errors count, numeration starts from 1), second - over columns (letters of haystack)
    emptyColumn = (2 << (needleLen - 1)) - 1  # Generate underground level of table
    underground = []
    [underground.append(emptyColumn) for i in range(haystackLen + 1)]
    table.append(underground)

    # Execute precise matching
    k = 1
    table.append([emptyColumn])
    for columnNum in range(1, haystackLen + 1):
        prevColumn = (table[k][columnNum - 1]) >> 1
        letterPattern = alphabet[haystack[columnNum - 1]]
        curColumn = prevColumn | letterPattern
        table[k].append(curColumn)
        if (curColumn & 0x1) == 0:
            index = columnNum - needleLen
            if index not in result:
                result.append(index)

    # Execute fuzzy searching with calculation Levenshtein distance
    for k in range(2, maxErrors + 2):
        table.append([emptyColumn])
        for columnNum in range(1, haystackLen + 1):
            prevColumn = (table[k][columnNum - 1]) >> 1
            letterPattern = alphabet[haystack[columnNum - 1]]
            curColumn = prevColumn | letterPattern
            insertColumn = curColumn & (table[k - 1][columnNum - 1])
            deleteColumn = curColumn & (table[k - 1][columnNum] >> 1)
            replaceColumn = curColumn & (table[k - 1][columnNum - 1] >> 1)
            resColumn = insertColumn & deleteColumn & replaceColumn
            table[k].append(resColumn)
            if (resColumn & 0x1) == 0:
                startPos = max(0, columnNum - needleLen - 1) # taking in account Replace operation
                if startPos not in result:
                    result.append(startPos)
    return result



# Example usage
text = "мы купили помидор"
pattern = ["миддор"]
maxErrors = 1

#print(bitapSearchMultiple(text, pattern, threshold))
print(bitapSearchMultiple(text, pattern, maxErrors))

#print(bitapSearch("abcaxyxz", "a", ))
