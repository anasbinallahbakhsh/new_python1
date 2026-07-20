a=50
def func():
 global x
 a=11
 x=10
 return x
print(a)
print(func())
print(x)
