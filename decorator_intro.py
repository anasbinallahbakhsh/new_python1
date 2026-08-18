# decorators  _ehance the  functionlity of other funccccations 

def decorator_funcation(any_func):
    def wrapper_funcation():
        print('this is awesome funcation')
        any_func()
    return wrapper_funcation

# @ use for decerators
@ decorator_funcation   # this is shortcut
def func1():
   print('this is funcation 1')
func1()   

@ decorator_funcation
def func2():
    print('this is funcation 2')
func2()
# func1 = decorator_funcation(fun2)
# func1()
