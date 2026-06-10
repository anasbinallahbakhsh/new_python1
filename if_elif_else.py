#if else statement

#show ticket pricing
#1 to 3 (free)
#4 to 10 9150)
#11 to 60 (250)
#above 60 290)
age=input("please input your age  :")
age=int(age)
if age==0 or age< 0:
   print("You canot Watch")
elif 0<age<=3:
    print("Ticket price is free:free")
elif 3<age<=10:
    print("Ticket price :150 ")  
elif 10<age<=60:
    print("Ticket price :250")
else:
    print("ticket price  :200")



