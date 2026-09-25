from functools import wraps
def only_data_types_allow(data_type):
    def decorator( funcation):
        @wraps(funcation)
        def wrapper(*args,**kwargs):
            if all([type(arg) == data_type for arg in args]):
                return funcation(*args,**kwargs)
            print("Invalid argumments")
        return wrapper
    return decorator

@only_data_types_allow(str)
def string_join(*args):
    string=''
    for i in args:
        string+=i
    return string
print(string_join('Anas','malik'))