name = input("Enter your name: ")
i = 0
Temp_var = ""
while i < len(name):
    if name[i] not in Temp_var:
        Temp_var += name[i]
        print(f"{name[i]}:{name.count(name[i])}")
        i+=1
    