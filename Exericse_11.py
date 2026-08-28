winning_number = 27
user_input = input("guess a number b/w 1 to 100: ")
user_input = int(user_input)

if user_input == winning_number:
    print("YOU WIN ! ! !")
elif user_input < winning_number:
    print("Too low!")
else:
    print("Too high!")