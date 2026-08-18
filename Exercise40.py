import time

def calculate_time(any_func):
    def wrapper(*args, **kwargs):
        t1 = time.time()              # start time note kiya
        result = any_func(*args, **kwargs)   # asal function chalaya
        t2 = time.time()              # end time note kiya
        print(f'this function took {t2 - t1} sec to run')
        return result
    return wrapper


@calculate_time
def func():
    print('this is function')
    time.sleep(3)   # 3 second ka delay taake time measure ho sake


func()