name = input("Enter your name:")
counted = []

for char in name:
    if char not in counted:
        print(char, ":", name.count(char))
        counted.append(char)