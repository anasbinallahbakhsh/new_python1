


def decorator_function(any_func):
    def wrapper_function(*args, **kwargs):
        print('this is awesome function')
        return any_func(*args, **kwargs)
    return wrapper_function
@decorator_function
def func(*a):
    print(f'this is function with argument {a}')
func(7)
func(1000000)
@ decorator_function
def add(a,b):
    return a+b
print(add(2,2))