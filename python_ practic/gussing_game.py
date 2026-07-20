winning_numbr=10
guess=1
number=int(input("guess a number b\w 1 and 100:"))
game_over=False

while not game_over:
    if number == winning_numbr:
        print(f"you win and guess this in time{guess}")
    
    else:
        if number < winning_numbr:
            print("To low")
            guess+=1
            number=int(input("guess again:"))
else:
    print("too high")
    number=int(input("gueess again:"))
    