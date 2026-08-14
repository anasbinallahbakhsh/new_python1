


def multiple_nums(*args):
    multiple = 1
    print(*args)

    for i in args:
        multiple *= i

    return multiple
nums=[2,3,4,]
print(multiple_nums(*nums)) #unpack 