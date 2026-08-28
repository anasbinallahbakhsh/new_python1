def reformat(s: str) -> str:
    letters = [char for char in s if char.isalpha()]
    numbers = [char for char in s if char.isdigit()]

    if abs(len(letters) - len(numbers)) > 1:
        return ""

    if len(letters) >= len(numbers):
        first, second = letters, numbers
    else:
        first, second = numbers, letters

    result = []
    for i in range(len(second)):
        result.append(first[i])
        result.append(second[i])

    if len(first) > len(second):
        result.append(first[-1])

    return "".join(result)