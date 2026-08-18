from functools import wraps

def decorator_funcation(any_func):
    @wraps(any_func)
    def wrapper_funcation(*args, **kwargs):
        """this is wrapper function"""
        print('this is awesome function')
        return any_func(*args, **kwargs)
    return wrapper_funcation   # <-- ab ye decorator_funcation ke andar hai, wrapper_funcation ke bahar


@decorator_funcation
def add(a, b):
    '''this is add function'''
    return a + b


print(add.__doc__)
print(add.__name__)
print(add(2, 3))