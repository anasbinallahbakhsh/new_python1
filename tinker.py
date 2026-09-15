import tkinter as tk
import random

answer = [
    "YES! ✨",
    "NOPE 😳",
    "MAYBE 🤔",
    "DEFINITELY! 🔥",
    "ASK AGAIN 👀",
    "NOT TODAY 🧿"
]

def predict():
    result.config(text=random.choice(answer))

root = tk.Tk()
root.title("Magic python")
root.geometry("400x300")
root.configure(bg="black")

tk.Label(
    root, text="🐍 PYTHON MAGIC",
    font=("Arial", 24, "bold"),
    fg="white", bg="#151515"
).pack(pady=25)

result = tk.Label(
    root, text="Ask a Question",
    font=("Arial", 16),
    fg="cyan", bg="#151515"
)
result.pack(pady=25)

tk.Button(
    root, text="REVEAL",
    command=predict,
    font=("Arial", 14)
).pack(pady=10)

root.mainloop()