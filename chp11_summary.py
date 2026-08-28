# def add(a,b):
#     return a+b


# def new_add(*args):
#     total=0
#     for num in args:
#         total +=num
#     return total
# # print(new_add(1,2,3))

# # l=[1,2,3,40]
# # print(new_add(*l))    # _______> list ko unpack karna ka lia ham star use kaarta hain


# # kwargs mens keyword arguments ,**
# def func(**kwrags):
#     print(kwrags) 
#     print(type(kwrags)) # -----> gather as dictinorya
# func(name='Aans',age=17)   
















def func2(name,*args,last_name='unknown',**kweags):
    print(name)
    print(args)
    print(last_name)
    print(kweags)
func2('anas', 1,2,3, a=1,b=2)