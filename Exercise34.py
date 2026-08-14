def func(l,reverse_str=False):
    if reverse_str:
        l=l[::-1]
        print(l)
names=('anas','malik')        
print(func(names,reverse_str=True))


def func(l, reverse_str=False):
    if reverse_str:
        l = l[::-1]
        print(l)

names = ('anas', 'malik')
print(func(names, reverse_str=True))




def func(l, reverse_str=False):
    if reverse_str:
        l = l[::-1]
    return l

names = ('anas', 'malik')
print(func(names, reverse_str=True))