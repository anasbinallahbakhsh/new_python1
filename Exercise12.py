#MODIFY  NUMBER GUESSING NUMBER
winning_number = 43
guees = 1
number = int(input("guess a number betwen 1 and 100:"))
game_over = False


while not game_over:
    if number == winning_number:
        print(f"you guess this number and guess this number{guees} times")
        game_over = True
    else:
        if number < winning_number:
            print("Too low")
            guess+=1
            number=int(input("guess again:"))
        else:
            print(" too high")
            guees+=1
            number=int(input("guess again"))


winning_number=40
guees=1
number=int(input("guess a number betwen 1 and 100:"))
game_over=False
while not game_over:
    if  number == winning_number:
        print(f"yoy guess this number {guees} times")
        game_over=True
    else:
        if number < winning_number:
         print("Too low")
        guees+=1
        number=int(input("guess again:"))
else:
    print("Too low:")
    guess+=1
    number=int(input("guess again:"))
 