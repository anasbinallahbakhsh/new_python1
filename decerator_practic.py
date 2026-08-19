from functools import wraps

def only_int_allow(funcation):
    @wraps(funcation)
    def wrapper(*args, **kwargs):
        data_types = []
        for arg in args:
            data_types.append(type(arg) == int)
        if all(data_types):
            return funcation(*args, **kwargs)
        else:
            print('Invalid arguments')
    return wrapper


@only_int_allow
def add_all(*args):
    total = 0
    for i in args:
        total += i
    return total


print(add_all(1, 2, 3, 4))
print(add_all(1, 2, 3, [1, 2, 3, 4]))