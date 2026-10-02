"""
Muhammad Anas — Python Developer
A small portfolio app built with ONLY Python (Tkinter + webbrowser).

Run it:  python main.py   (or press the green Run button in PyCharm)
"""

import tkinter as tk
import webbrowser


# =====================================================================
#  1. YOUR INFO  —  EDIT THIS SECTION TO PERSONALIZE THE APP
# =====================================================================

# ---- Name and title -------------------------------------------------
NAME = "Muhammad Anas"
ROLE = "Python Developer"
SUBTITLE = "Developer & Content Creator"
APP_TITLE = "Muhammad Anas — Python Developer"   # text in the window title bar

# ---- Bio (shown on the Home page) -----------------------------------
BIO = (
    "I'm learning Python every day and turning what I learn into real "
    "projects. I enjoy solving problems, building small tools and games, "
    "and sharing my journey through content creation."
)

# ---- About Me cards: (title, description) ---------------------------
ABOUT_ITEMS = [
    ("Python Development", "Writing clean, readable Python and improving with every project."),
    ("Programming Projects", "Building tools, games and practice projects to learn by doing."),
    ("Problem Solving", "Breaking big problems into small steps and solving them one by one."),
    ("Cybersecurity", "Learning cybersecurity and ethical hacking the safe, legal way."),
    ("Content Creation", "Sharing what I learn through blogging and videos."),
]

# ---- Project cards --------------------------------------------------
# "url" is optional. Leave it as "" for no button, or paste a link
# (e.g. your GitHub repo) and a "View Project" button will appear.
PROJECTS = [
    {
        "title": "Python OOP",
        "desc": "Practice with classes, objects, inheritance and other object-oriented ideas.",
        "tags": "Python · OOP · Classes",
        "url": "",
    },
    {
        "title": "Secure Password Generator",
        "desc": "A tool that creates strong, random passwords to help keep accounts safe.",
        "tags": "Python · Security · Tool",
        "url": "",
    },
    {
        "title": "2D Space Shooter",
        "desc": "A 2D arcade-style space game where you dodge and shoot your way through.",
        "tags": "Python · Game · 2D",
        "url": "",
    },
    {
        "title": "Python Mini Projects",
        "desc": "A collection of small Python programs built to practice and learn.",
        "tags": "Python · Practice · Mini",
        "url": "",
    },
]

# ---- Timetable: (time of day, activity) -----------------------------
TIMETABLE = [
    ("Morning", "College"),
    ("Afternoon", "Blogging / Content Creation"),
    ("Evening", "Farming / Personal Work"),
    ("Night", "Python Programming"),
]

# ---- Social links ---------------------------------------------------
# Paste YOUR links between the quotes, e.g.
#   GITHUB_URL = "https://github.com/your-username"
# Empty ("") means "not added yet" — the button will show a reminder.
LINKEDIN_URL = ""   # <-- add your LinkedIn link here
GITHUB_URL = ""     # <-- add your GitHub link here
YOUTUBE_URL = ""    # <-- add your YouTube link here
TIKTOK_URL = ""     # <-- add your TikTok link here

SOCIAL_LINKS = [
    ("LinkedIn", LINKEDIN_URL),
    ("GitHub", GITHUB_URL),
    ("YouTube", YOUTUBE_URL),
    ("TikTok", TIKTOK_URL),
]


# =====================================================================
#  2. LOOK & FEEL  (colors and fonts)
# =====================================================================

BG = "#0d1117"          # window background
NAV_BG = "#010409"      # navigation bar
CARD = "#161b22"        # card background
CARD_HOVER = "#1d2430"  # card background when hovered
BORDER = "#30363d"      # card border
TEXT = "#e6edf3"        # main text
MUTED = "#8b949e"       # softer text
BLUE = "#58a6ff"        # main accent (Python blue)
YELLOW = "#ffd43b"      # second accent (Python yellow)
GREEN = "#3fb950"       # code-style accent

FONT = "Segoe UI"       # main font (falls back automatically if missing)
MONO = "Consolas"       # code-style font


# =====================================================================
#  3. SMALL REUSABLE WIDGETS
# =====================================================================

class HoverButton(tk.Label):
    """A flat, modern button that changes color on hover."""

    def __init__(self, parent, text, command, primary=True):
        self.primary = primary
        self.normal_bg = BLUE if primary else CARD
        self.hover_bg = "#79b8ff" if primary else CARD_HOVER
        self.fg = "#0d1117" if primary else TEXT
        super().__init__(
            parent, text=text, font=(FONT, 11, "bold"), fg=self.fg,
            bg=self.normal_bg, padx=22, pady=10, cursor="hand2",
            highlightthickness=1, highlightbackground=BLUE if primary else BORDER,
        )
        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.normal_bg))
        self.bind("<Button-1>", lambda e: command())


class Card(tk.Frame):
    """A dark card with a border that lights up when the mouse is over it."""

    def __init__(self, parent):
        super().__init__(parent, bg=CARD, highlightthickness=1,
                         highlightbackground=BORDER)
        self._members = [self]      # widgets whose background should change
        self._wrap_labels = []      # labels whose text should wrap with the card
        self.register_widget(self)
        self.bind("<Configure>", self._update_wrap)

    def register_widget(self, widget):
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")

    def label(self, text, font, fg=TEXT, wrap=False, pady=(0, 0), anchor="w"):
        """Create a label inside the card."""
        lbl = tk.Label(self, text=text, font=font, fg=fg, bg=CARD,
                       anchor=anchor, justify="left")
        lbl.pack(fill="x", padx=22, pady=pady)
        self._members.append(lbl)
        self.register_widget(lbl)
        if wrap:
            self._wrap_labels.append(lbl)
        return lbl

    def make_clickable(self, command):
        """Make the whole card (and everything inside it) clickable."""
        for w in self._members:
            w.config(cursor="hand2")
            w.bind("<Button-1>", lambda e: command(), add="+")

    def _update_wrap(self, event):
        for lbl in self._wrap_labels:
            lbl.config(wraplength=max(120, event.width - 50))

    def _on_enter(self, event=None):
        self.config(highlightbackground=BLUE)
        for w in self._members:
            w.config(bg=CARD_HOVER)

    def _on_leave(self, event=None):
        # Only "un-hover" if the mouse really left the whole card
        x, y = self.winfo_pointerxy()
        under = self.winfo_containing(x, y)
        while under is not None:
            if under is self:
                return
            under = under.master
        self.config(highlightbackground=BORDER)
        for w in self._members:
            w.config(bg=CARD)


def reflow(container, widgets, min_width=300, gap=14):
    """Arrange widgets in a grid whose column count adapts to the window width."""
    state = {"cols": 0}

    def apply(event=None):
        cols = max(1, min(len(widgets), container.winfo_width() // min_width))
        if cols == state["cols"]:
            return
        state["cols"] = cols
        for w in widgets:
            w.grid_forget()
        for c in range(8):
            container.columnconfigure(c, weight=0, uniform="")
        for i, w in enumerate(widgets):
            w.grid(row=i // cols, column=i % cols, sticky="nsew",
                   padx=gap // 2, pady=gap // 2)
        for c in range(cols):
            container.columnconfigure(c, weight=1, uniform="cards")

    container.bind("<Configure>", apply)


# =====================================================================
#  4. PAGES
# =====================================================================

class Page(tk.Frame):
    """Base class for every page: adds padding and an optional heading."""

    def __init__(self, parent, title=None, subtitle=None):
        super().__init__(parent, bg=BG)
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True, padx=44, pady=30)
        if title:
            tk.Label(self.body, text=title, font=(FONT, 26, "bold"),
                     fg=TEXT, bg=BG, anchor="w").pack(fill="x")
            tk.Frame(self.body, bg=YELLOW, height=3, width=56).pack(anchor="w", pady=(6, 8))
        if subtitle:
            tk.Label(self.body, text=subtitle, font=(FONT, 11),
                     fg=MUTED, bg=BG, anchor="w").pack(fill="x", pady=(0, 14))


class HomePage(Page):
    def __init__(self, parent, go_to):
        super().__init__(parent)
        self.body.columnconfigure(0, weight=3)
        self.body.columnconfigure(1, weight=2)
        self.body.rowconfigure(0, weight=1)

        # ---- left side: intro text
        left = tk.Frame(self.body, bg=BG)
        left.grid(row=0, column=0, sticky="w", padx=(0, 30))

        tk.Label(left, text="> Hello, I'm", font=(MONO, 13), fg=GREEN,
                 bg=BG, anchor="w").pack(fill="x")
        tk.Label(left, text=NAME, font=(FONT, 40, "bold"), fg=TEXT,
                 bg=BG, anchor="w").pack(fill="x", pady=(4, 0))
        tk.Label(left, text=ROLE, font=(FONT, 22, "bold"), fg=BLUE,
                 bg=BG, anchor="w").pack(fill="x")
        tk.Label(left, text=SUBTITLE, font=(FONT, 13), fg=YELLOW,
                 bg=BG, anchor="w").pack(fill="x", pady=(2, 16))
        bio = tk.Label(left, text=BIO, font=(FONT, 12), fg=MUTED, bg=BG,
                       justify="left", anchor="w")
        bio.pack(fill="x")
        left.bind("<Configure>", lambda e: bio.config(wraplength=max(200, e.width - 10)))

        buttons = tk.Frame(left, bg=BG)
        buttons.pack(anchor="w", pady=(24, 0))
        HoverButton(buttons, "View Projects", lambda: go_to("Projects")).pack(side="left")
        HoverButton(buttons, "Get in Touch", lambda: go_to("Social"),
                    primary=False).pack(side="left", padx=(12, 0))

        # ---- right side: a code-style card (very "developer")
        code = Card(self.body)
        code.grid(row=0, column=1, sticky="ew")
        code.label("● ● ●", (FONT, 10), fg=MUTED, pady=(14, 8))
        lines = [
            ("class", " Developer", ":"),
            ("    name", f' = "{NAME}"', ""),
            ("    role", f' = "{ROLE}"', ""),
            ("    learning", ' = ["Python", "Cybersecurity"]', ""),
            ("    creates", ' = "Content"', ""),
        ]
        for i, (a, b, c) in enumerate(lines):
            colour = BLUE if a == "class" else TEXT
            code.label(a + b + c, (MONO, 11), fg=colour,
                       pady=(0, 14 if i == len(lines) - 1 else 2))


class AboutPage(Page):
    def __init__(self, parent):
        super().__init__(parent, "About Me",
                         "What I do and what I'm learning.")
        grid = tk.Frame(self.body, bg=BG)
        grid.pack(fill="both", expand=True)
        cards = []
        for i, (title, desc) in enumerate(ABOUT_ITEMS, start=1):
            card = Card(grid)
            card.label(f"0{i}", (MONO, 11), fg=YELLOW, pady=(16, 0))
            card.label(title, (FONT, 14, "bold"), pady=(2, 4))
            card.label(desc, (FONT, 10), fg=MUTED, wrap=True, pady=(0, 16))
            cards.append(card)
        reflow(grid, cards, min_width=280)


class ProjectsPage(Page):
    def __init__(self, parent):
        super().__init__(parent, "My Projects",
                         "Things I've built while learning Python.")
        grid = tk.Frame(self.body, bg=BG)
        grid.pack(fill="both", expand=True)
        cards = []
        for p in PROJECTS:
            card = Card(grid)
            card.label("</>", (MONO, 13, "bold"), fg=GREEN, pady=(16, 0))
            card.label(p["title"], (FONT, 15, "bold"), pady=(4, 4))
            card.label(p["desc"], (FONT, 10), fg=MUTED, wrap=True)
            card.label(p["tags"], (MONO, 9), fg=BLUE, pady=(10, 0 if p["url"] else 16))
            if p["url"]:
                url = p["url"]
                link = card.label("View Project →", (FONT, 10, "bold"),
                                  fg=YELLOW, pady=(8, 16))
                link.config(cursor="hand2")
                link.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
            cards.append(card)
        reflow(grid, cards, min_width=360)


class TimetablePage(Page):
    def __init__(self, parent):
        super().__init__(parent, "My Timetable",
                         "A simple look at my daily routine.")
        for when, what in TIMETABLE:
            row = Card(self.body)
            row.pack(fill="x", pady=6)
            inner = tk.Frame(row, bg=CARD)
            inner.pack(fill="x", padx=22, pady=14)
            row._members.append(inner)
            row.register_widget(inner)
            for text, font, fg, side in [
                (when, (FONT, 13, "bold"), YELLOW, "left"),
                ("→", (FONT, 14), MUTED, "left"),
                (what, (FONT, 13), TEXT, "left"),
            ]:
                lbl = tk.Label(inner, text=text, font=font, fg=fg, bg=CARD,
                               width=11 if text == when else 0, anchor="w")
                lbl.pack(side=side, padx=(0, 14))
                row._members.append(lbl)
                row.register_widget(lbl)


class SocialPage(Page):
    def __init__(self, parent):
        super().__init__(parent, "Social Links",
                         "Find me online — click a card to open it in your browser.")
        grid = tk.Frame(self.body, bg=BG)
        grid.pack(fill="x")
        cards = []
        for name, url in SOCIAL_LINKS:
            card = Card(grid)
            card.label(name, (FONT, 16, "bold"), pady=(18, 2))
            card.label("Open " + name + " →", (FONT, 10), fg=BLUE, pady=(0, 18))
            card.make_clickable(lambda n=name, u=url: self.open_link(n, u))
            cards.append(card)
        reflow(grid, cards, min_width=220)

        self.status = tk.Label(self.body, text="", font=(FONT, 10),
                               fg=YELLOW, bg=BG, anchor="w")
        self.status.pack(fill="x", pady=(14, 0))

    def open_link(self, name, url):
        if url.strip():
            webbrowser.open(url)
            self.status.config(text=f"Opening {name}...", fg=GREEN)
        else:
            self.status.config(
                text=f"No {name} link yet — add it near the top of main.py.",
                fg=YELLOW)


# =====================================================================
#  5. MAIN APP WINDOW + NAVIGATION BAR
# =====================================================================

class NavButton(tk.Frame):
    """One item in the navigation bar, with hover + active underline."""

    def __init__(self, parent, text, command):
        super().__init__(parent, bg=NAV_BG)
        self.active = False
        self.label = tk.Label(self, text=text, font=(FONT, 11, "bold"),
                              fg=MUTED, bg=NAV_BG, padx=14, pady=12,
                              cursor="hand2")
        self.label.pack()
        self.bar = tk.Frame(self, bg=NAV_BG, height=3)
        self.bar.pack(fill="x")
        for w in (self, self.label):
            w.bind("<Enter>", lambda e: self._refresh(True))
            w.bind("<Leave>", lambda e: self._refresh(False))
            w.bind("<Button-1>", lambda e: command())

    def set_active(self, value):
        self.active = value
        self._refresh(False)

    def _refresh(self, hover):
        self.label.config(fg=BLUE if self.active else (TEXT if hover else MUTED))
        self.bar.config(bg=BLUE if self.active else NAV_BG)


class PortfolioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=BG)
        self.minsize(780, 580)
        self._center(1040, 700)

        # ---- navigation bar
        nav = tk.Frame(self, bg=NAV_BG)
        nav.pack(fill="x")
        tk.Label(nav, text="<Anas/>", font=(MONO, 15, "bold"), fg=BLUE,
                 bg=NAV_BG, padx=22).pack(side="left")

        # Packed from the right, so we go in reverse to read: Home | About | ... | Social
        self.nav_buttons = {}
        for name in ["Social", "Timetable", "Projects", "About", "Home"]:
            btn = NavButton(nav, name, lambda n=name: self.show(n))
            btn.pack(side="right", padx=2)
            self.nav_buttons[name] = btn

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ---- pages (stacked on top of each other, one shown at a time)
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.pages = {
            "Home": HomePage(container, self.show),
            "About": AboutPage(container),
            "Projects": ProjectsPage(container),
            "Timetable": TimetablePage(container),
            "Social": SocialPage(container),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show("Home")

    def show(self, name):
        self.pages[name].tkraise()
        for n, btn in self.nav_buttons.items():
            btn.set_active(n == name)

    def _center(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{max(y - 20, 0)}")


# =====================================================================
#  6. START THE APP
# =====================================================================

if __name__ == "__main__":
    # Makes text sharper on Windows high-DPI screens (safe to ignore elsewhere)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    PortfolioApp().mainloop()