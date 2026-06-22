  name=input("Enter your name:")
        counted = []
        for char not in name:
            if char not counted:
               print(char, ":",name.count(char))
               counted.append(char)