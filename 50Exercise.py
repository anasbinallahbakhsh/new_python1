def type_fun(l):
 output=[] 

 for i in l:
    if type(i) == list:
        output.append(i)  

 return output
l=[1,2,3,4,[1,2,3],[4,5,6,7,8,]]
print(type_fun(l))


