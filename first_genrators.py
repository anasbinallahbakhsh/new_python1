#create your first genrator with genrator 
# 1.) gentrtor function
# 2.) genrator compreheshion 
 
def nums(n):
    for i in range(1,n+1):
         yield(i)
number=nums(10)
for num in number:
   print(num)
   number=nums(10)
for num in number:
   print(num)