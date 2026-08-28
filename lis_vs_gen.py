import time
#list vs genratpr
#memoey usage vs time
# when to use the list
#when to use genarator
t1=time.time()
l=[i**2 for i in range(1000000)]
t2=time.time()
print(t2-t1)

t1=time.time()
#g=(i**2 for i in range(1000000) )
t1=time.time()
print(t1-t2)