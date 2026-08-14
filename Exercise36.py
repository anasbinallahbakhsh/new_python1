def func(l,**kwargs):
    if kwargs.get('reverse_str')==True:
        return [name[::-1].tile() for name in l]
    else:
        return[name.tile() for naem in l]

name=['anas','malik']
print(func(name,reverse_str= True))