#list comprehesion
#with the help list comprehension we can create of  list in one line

#create a list square from 1 to 10
 
# squares=[]
# for i in range(1,11):
#     squares.append(i ** 2)
# print(squares)


# squares2=[i*2 for i in range(1,11)]
# print(squares2


# negetive=[]
# for i in range(1,11):
#     negetive.append(-i)
# print(negetive)




names=['anas','umar','muhammad']
# new_list=[]
# for names in names:
#   new_list.append(names[0])
# print(new_list)

new_lsit2=[names[0] for names in names]
print(names)