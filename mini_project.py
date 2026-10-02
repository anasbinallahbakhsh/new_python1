import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class WindowsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Windows App")
        self.root.geometry("1000x650")
        self.root.minsize(850, 550)

        self.bg = "#f4f6f8"
        self.sidebar = "#1f2937"
        self.primary = "#2563eb"
        self.white = "#ffffff"
        self.text = "#111827"
        self.gray = "#6b7280"

        self.root.configure(bg=self.bg)

        self.create_sidebar()
        self.create_main_area()

    # ---------------- SIDEBAR ----------------
    def create_sidebar(self):
        sidebar = tk.Frame(
            self.root,
            bg=self.sidebar,
            width=220
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        title = tk.Label(
            sidebar,
            text="PYTHON APP",
            bg=self.sidebar,
            fg="white",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(pady=(35, 40))

        self.create_nav_button(sidebar, "Dashboard", self.show_dashboard)
        self.create_nav_button(sidebar, "Tasks", self.show_tasks)
        self.create_nav_button(sidebar, "About", self.show_about)

        exit_button = tk.Button(
            sidebar,
            text="Exit",
            command=self.exit_app,
            bg="#dc2626",
            fg="white",
            activebackground="#b91c1c",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2"
        )
        exit_button.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=25,
            ipady=8
        )

    def create_nav_button(self, parent, text, command):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.sidebar,
            fg="white",
            activebackground="#374151",
            activeforeground="white",
            relief="flat",
            anchor="w",
            font=("Segoe UI", 11),
            cursor="hand2"
        )

        button.pack(
            fill="x",
            padx=15,
            pady=5,
            ipady=10
        )

    # ---------------- MAIN AREA ----------------
    def create_main_area(self):
        self.main = tk.Frame(
            self.root,
            bg=self.bg
        )
        self.main.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.show_dashboard()

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    # ---------------- DASHBOARD ----------------
    def show_dashboard(self):
        self.clear_main()

        header = tk.Frame(
            self.main,
            bg=self.bg
        )
        header.pack(
            fill="x",
            padx=35,
            pady=30
        )

        title = tk.Label(
            header,
            text="Dashboard",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 25, "bold")
        )
        title.pack(side="left")

        date = datetime.now().strftime("%d %B %Y")

        date_label = tk.Label(
            header,
            text=date,
            bg=self.bg,
            fg=self.gray,
            font=("Segoe UI", 11)
        )
        date_label.pack(side="right", pady=10)

        # Cards
        cards = tk.Frame(
            self.main,
            bg=self.bg
        )
        cards.pack(
            fill="x",
            padx=35
        )

        self.create_card(
            cards,
            "Python",
            "Development",
            0
        )

        self.create_card(
            cards,
            "Windows",
            "Desktop App",
            1
        )

        self.create_card(
            cards,
            "Tkinter",
            "GUI Framework",
            2
        )

        # Welcome section
        welcome = tk.Frame(
            self.main,
            bg=self.white
        )
        welcome.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=30
        )

        tk.Label(
            welcome,
            text="Welcome 👋",
            bg=self.white,
            fg=self.text,
            font=("Segoe UI", 22, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=(30, 10)
        )

        tk.Label(
            welcome,
            text=(
                "This is a Windows desktop application "
                "built completely with Python and Tkinter."
            ),
            bg=self.white,
            fg=self.gray,
            font=("Segoe UI", 12)
        ).pack(
            anchor="w",
            padx=30
        )

        tk.Label(
            welcome,
            text="No HTML • No CSS • No JavaScript",
            bg=self.white,
            fg=self.primary,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=20
        )

        tk.Button(
            welcome,
            text="Show Message",
            command=self.show_message,
            bg=self.primary,
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(
            anchor="w",
            padx=30
        )

    def create_card(self, parent, title, subtitle, column):
        card = tk.Frame(
            parent,
            bg=self.white,
            width=200,
            height=120
        )

        card.grid(
            row=0,
            column=column,
            padx=8,
            sticky="nsew"
        )

        parent.grid_columnconfigure(
            column,
            weight=1
        )

        card.grid_propagate(False)

        tk.Label(
            card,
            text=title,
            bg=self.white,
            fg=self.primary,
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(22, 5)
        )

        tk.Label(
            card,
            text=subtitle,
            bg=self.white,
            fg=self.gray,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            padx=20
        )

    # ---------------- TASKS ----------------
    def show_tasks(self):
        self.clear_main()

        tk.Label(
            self.main,
            text="Tasks",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 25, "bold")
        ).pack(
            anchor="w",
            padx=35,
            pady=(30, 20)
        )

        task_frame = tk.Frame(
            self.main,
            bg=self.white
        )
        task_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        tk.Label(
            task_frame,
            text="Add a Task",
            bg=self.white,
            fg=self.text,
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 10)
        )

        self.task_entry = tk.Entry(
            task_frame,
            font=("Segoe UI", 12),
            relief="solid",
            bd=1
        )
        self.task_entry.pack(
            fill="x",
            padx=25,
            ipady=8
        )

        tk.Button(
            task_frame,
            text="Add Task",
            command=self.add_task,
            bg=self.primary,
            fg="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2"
        ).pack(
            anchor="w",
            padx=25,
            pady=15,
            ipadx=15,
            ipady=6
        )

        self.task_list = tk.Listbox(
            task_frame,
            font=("Segoe UI", 11),
            bg="#f9fafb",
            relief="flat"
        )
        self.task_list.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 25)
        )

    def add_task(self):
        task = self.task_entry.get().strip()

        if not task:
            messagebox.showwarning(
                "Empty Task",
                "Please enter a task."
            )
            return

        self.task_list.insert(
            tk.END,
            "✓ " + task
        )

        self.task_entry.delete(
            0,
            tk.END
        )

    # ---------------- ABOUT ----------------
    def show_about(self):
        self.clear_main()

        tk.Label(
            self.main,
            text="About",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 25, "bold")
        ).pack(
            anchor="w",
            padx=35,
            pady=(30, 20)
        )

        about = tk.Frame(
            self.main,
            bg=self.white
        )
        about.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        tk.Label(
            about,
            text="Python Windows Application",
            bg=self.white,
            fg=self.primary,
            font=("Segoe UI", 20, "bold")
        ).pack(
            pady=(60, 15)
        )

        tk.Label(
            about,
            text=(
                "Built with Python + Tkinter\n\n"
                "Designed for Windows 10/11\n\n"
                "No HTML • No CSS • No JavaScript"
            ),
            bg=self.white,
            fg=self.gray,
            font=("Segoe UI", 12),
            justify="center"
        ).pack()

    # ---------------- MESSAGE ----------------
    def show_message(self):
        messagebox.showinfo(
            "Python App",
            "This Windows application is running successfully!"
        )

    # ---------------- EXIT ----------------
    def exit_app(self):
        answer = messagebox.askyesno(
            "Exit",
            "Do you want to close the application?"
        )

        if answer:
            self.root.destroy()


# ---------------- START APP ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = WindowsApp(root)
    root.mainloop()