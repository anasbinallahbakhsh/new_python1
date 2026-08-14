# l=[10]
# if l:
#     print("yes")
# else:
#     print("no")



def to_power(num,*args):
    if args:
        return[i**num for i in args]
    else:
        return "you didn,t type anthing"
nums=[1,2,3,4]
print(to_power(3,*[2,3]))