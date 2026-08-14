#functions with all parameters
#very imporatant to unsderstand 
#PADK

#parameters
#args
#defult parametrs
#kwargss
# 

    
def func(*name, last_name='unknown', **kwargs):
    print(name)
    print(last_name)
    print(kwargs)


func('Anas', 1, 2, 3, a=1, b=2)