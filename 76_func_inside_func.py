def greatest(a,b,c):
    if a>b and a>c:
        return b
    elif b>a and b>c:
        return b
    else:
        return c
print(greatest(10,20,30)) 
#Keep - it simple and stupid

def greater(a, b):
    if a > b:
        return a
    else:
        return b


def new_greatest(a, b, c):
    bigger = greater(a, b)
    return greater(bigger, c)