#.split method
#convert string to lsit
#join method 
# convert list to string
user_info='Anas, 17' .split(',')
print(user_info)

name, age=input("enter your name and age").split(',')
print(name)
print(age)

user_info=["anas","17"]
print(','.join(user_info))