from functools import wraps
import time
def calculate_time(funcation):
    @wraps(function)
     print(f'executing {function.__name__}')
    def wrapper(args,**kwrags):
      t1=time.time()
      returned_value=function(*args,**kwrags)
      t2=time.time()
      total=time-time
      print(f"this funcation took {total-time} seconds")
      return  returned_value
    return wrapper
def square_finder(n):
   return[i**2 for i in range (1,n+1)]
square_finder(1000)