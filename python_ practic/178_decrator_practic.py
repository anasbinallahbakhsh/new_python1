from functools import wraps

def only_data_type_allow(*data_type):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if all(type(arg) in data_type for arg in args):
                return function(*args, **kwargs)

            print("Invalid arguments")

        return wrapper

    return decorator


@only_data_type_allow(str)
def join_string(*args):

    string = ''

    for i in args:
        string += i

    return string


print(join_string('anas', 'malik'))