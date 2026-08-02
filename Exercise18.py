def filter_odd_even(l):
    odd = []
    even = []

    for i in l:
        if i % 2 == 0:
            even.append(i)
        else:
            odd.append(i)

    return [odd, even]


numbers = [1, 2, 3, 4, 5, 6, 7, 8]
print(filter_odd_even(numbers))