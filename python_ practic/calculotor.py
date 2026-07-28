# def add(a, b):
#     return a + b

# def subtract(a, b):
#     return a - b

# def multiply(a, b):
#     return a * b

# def divide(a, b):
#     if b == 0:
#         return "Error! Division by zero is not allowed."
#     return a / b

# print("====== Python Calculator ======")
# print("1. Addition (+)")
# print("2. Subtraction (-)")
# print("3. Multiplication (*)")
# print("4. Division (/)")

# choice = input("Enter your choice (1-4): ")

# num1 = float(input("Enter first number: "))
# num2 = float(input("Enter second number: "))

# if choice == "1":
#     print("Result:", add(num1, num2))

# elif choice == "2":
#     print("Result:", subtract(num1, num2))

# elif choice == "3":
#     print("Result:", multiply(num1, num2))

# elif choice == "4":
#     print("Result:", divide(num1, num2))

# else:
#     print("Invalid choice! Please select 1, 2, 3, or 4.")
import tkinter as tk

def click(value):
    entry.insert(tk.END, value)

def clear():
    entry.delete(0, tk.END)

def calculate():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(0, result)
    except:
        entry.delete(0, tk.END)
        entry.insert(0, "Error")

root = tk.Tk()
root.title("Python Calculator")
root.geometry("320x450")
root.resizable(False, False)

entry = tk.Entry(root, font=("Arial", 20), bd=10, relief="ridge", justify="right")
entry.pack(fill="x", padx=10, pady=10)

buttons = [
    "7","8","9","/",
    "4","5","6","*",
    "1","2","3","-",
    "0",".","=","+",
    "C"
]

frame = tk.Frame(root)
frame.pack()

row = 0
col = 0

for button in buttons:
    if button == "=":
        cmd = calculate
    elif button == "C":
        cmd = clear
    else:
        cmd = lambda x=button: click(x)

    tk.Button(frame,
              text=button,
              width=6,
              height=2,
              font=("Arial",16),
              command=cmd).grid(row=row, column=col, padx=5, pady=5)

    col += 1
    if col > 3:
        col = 0
        row += 1

root.mainloop()