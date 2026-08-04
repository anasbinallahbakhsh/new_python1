# looping in tuple
# tuple with one elememt 
# tuple without parnthesics

guitars='yamaha','butoon rouge','tylor'
#print(type(guitars))
# tuple unpacking 


guitarsists=("Meneli jamal","Eddie van Deer Mar",'Andrew foy')
guitarsists1,guitarsists2,guitarsists3=(guitarsists)
#print(guitarsists1)


#list inside tuple
favorites=('southren mangolia',['okyo Ghoual theme','landscape'])
favorites[1].pop()
favorites[1].append("we made it")
print(favorites)
# some function that u can use in tuple
mixed=(1,2,3,4.0)

# for loop and tuple
for i in mixed:
 #print(i)

# #NOTE:- use caaaan use while loop to
# #tuple  with one element
 nums=(1,) #if we want to make tuple than we must be used comma ", " 
 words=('wors1')
# print(type(nums))
# print(type(words))

#min ,ax sum
print(sum(mixed))