#funcation retunring funcation 
def outer_func():
    def iner_func():
        print('inside iner func')
    return iner_func
var=outer_func()
var()


def outer_func2(msg):
   def inner_func2():
       return(f"msg i s{msg}")
   print(f"message is {msg}")
   return inner_func2
var=outer_func2("hey anas bro !")
var()