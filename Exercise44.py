from functools import wraps
import time

def calculate_time(funcation):

    @wraps(funcation)
    def wrapper(*args, **kwargs):
        print(f'Executing {funcation .__name__}')
        t1 = time.time()

        returned_value = funcation(*args, **kwargs)

        t2 = time.time()
        total = t2 - t1
        print('this functin took {total_time} seconds')
        return returned_value
    return wrapper

@calculate_time
def square_finder(n):
    return[i**2 for i in range(1,n+1)]


square_finder(1000)

