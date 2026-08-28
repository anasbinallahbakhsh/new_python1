name, char=input("Enter your name  char comma sperated:").split(",")
print(f"lenth of your name is{len(name)}")
print(f"character count:{name.strip().lower().count(char.strip().lower())}") #case sensetive
