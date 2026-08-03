def sublist_counter(l):
    count=0
    for i in l:
        if type(i)== list:
            count+=1
    
    return count
mixed=[1,2,3,[4,5,6],[6,5,3,],[1,0,9]]
print((sublist_counter(mixed)))