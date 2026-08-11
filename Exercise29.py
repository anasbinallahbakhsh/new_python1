



def number_to_string(*lst):
    return [str(x) for x in lst if type(x) in (int, float)]

lst=[True,False,[1,2,3],1.2,10,9]
print(number_to_string(*lst))