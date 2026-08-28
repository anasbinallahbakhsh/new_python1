#kwrags(key word arguments)
#** double star operator 
def func(**kwargs):
    for k , v in kwargs.items():
     print(f"{k}:{v}")
# dicitinory unpacking
d={'name':'anas','age':24}
func(**d)
func(first_name="Anas", last_name='malik')