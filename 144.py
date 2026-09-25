#function
#LIST  revere_str =true
#list
def func(l,**kwargs):
    if kwargs.get('reverse_str') == True:
        return [name[::-1].title() for name in l]
    else:
        return [name.title() for name in l]
name=['anas','malik']
print(func(name, reverse_str =True))