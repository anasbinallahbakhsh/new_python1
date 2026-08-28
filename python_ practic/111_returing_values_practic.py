def func(int1,int2):
    add=int1+int2
    multiply=int1*int2
    return add,multiply
print(func(4,5))
add, multiply=func(4,5)
print(add)
print(multiply)