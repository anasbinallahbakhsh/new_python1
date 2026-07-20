#scope
x=5 #global varible
def func():
    global x
    x=7
    x=7 #local varibles
    return x
print(x)
print(func())
print(x)