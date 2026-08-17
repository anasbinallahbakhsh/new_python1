# #map
# def square(a):
#     return a**2
l=[1,2,3,4]
# print(list(map(lambda a:a**2,l)))


def my_map(func, l):
    new_lsit=[]
    for item in l:
     new_lsit.append(func(item))
    return new_lsit


def my_map2(func,l):
 return[func(item) for item in l]
print(my_map(lambda a:a**3,l))



  