import tkinter as tk

def click(value):
    entry.insert(tk.END, value)

def clear():
    entry.delete(0, tk.END)

def calculate():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(0, str(result))
    except:
        entry.delete(0, tk.END)
        entry.insert(0, "Error")

root = tk.Tk()
root.title("Python Calculator")
root.geometry("350x500")
root.resizable(False, False)

entry = tk.Entry(
    root,
    font=("Arial", 22),
    justify="right",
    bd=8,
    relief="ridge"
)
entry.pack(fill="x", padx=10, pady=10)

frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

buttons = [
    "7", "8", "9", "/",
    "4", "5", "6", "*",
    "1", "2", "3", "-",
    "0", ".", "=", "+",
    "C"
]

row = 0
col = 0

for button in buttons:

    if button == "=":
        command = calculate
    elif button == "C":
        command = clear
    else:
        command = lambda x=button: click(x)

    tk.Button(
        frame,
        text=button,
        font=("Arial", 18),
        width=5,
        height=2,
        command=command
    ).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    col += 1

    if col == 4:
        col = 0
        row += 1

for i in range(5):
    frame.grid_rowconfigure(i, weight=1)

for i in range(4):
    frame.grid_columnconfigure(i, weight=1)

root.mainloop()