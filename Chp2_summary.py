#Strings
name="Anas"
#String  indixing
print(name[0])
#string slicing/ we can use String indixing negetive also like
print(name[-1:0:-1])
#take user input
age=int(input("Enter your age:"))
print(age)
#take user inputs
user_name, age=input("Enter  your name and age:").split()
print(user_name)
print(age)
#len funcation
print(len(name))
#lower, uper, tiltle method
print(name.title())
#find replace centre method
print(name.find("a"))
a_pos=name.find("a")
a_pos2=(name.find("a",a_pos+1))
print(a_pos2)
#print(name.center(8,"*"))
print(name.replace("n","z"))
#string are immutaible   24
