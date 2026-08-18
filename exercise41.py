import time

def calculate_time(any_func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = any_func(*args, **kwargs)
        t2 = time.time()
        print(f"this function took {t2 - t1} sec to run")
        return result
    return wrapper


@calculate_time
def func():
    print('this is function')
    time.sleep(3)


func()