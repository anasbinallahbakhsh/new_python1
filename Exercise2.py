number1 = int(input("enter a first number: "))
number2 = int(input("enter a second number: "))
number3 = int(input("enter a third number: "))
total = number1 + number2 + number3
average = total / 3
print(f"average is {average}")

numbers = input("enter three numbers (comma separated): ").split(",")
number1 = int(numbers[0])
number2 = int(numbers[1])
number3 = int(numbers[2])
total = number1 + number2 + number3
average = total / 3
print(f"average of {numbers[0]}, {numbers[1]}, {numbers[2]} is {average}")