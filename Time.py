import time
import sys
import os
import random

DEEP_RED      = '\033[38;5;88m'
PASSION_PURPLE = '\033[38;5;54m'
GOLDEN_WARM   = '\033[38;5;136m'
MIST_WHITE    = '\033[38;5;251m'
BOLD          = '\033[1m'
RESET         = '\033[0m'


def sensual_typing(text, color):
    for char in text:
        sys.stdout.write(f"{BOLD}{color}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(0.078)
    print()


def run_ehsaas_code():
    os.system('cls' if os.name == 'nt' else 'clear')

    sensual_typing("Tere ehsaason mein kho gaya main...", MIST_WHITE)
    time.sleep(1.7)

    sensual_typing("💔 Tere Ehsaas", DEEP_RED)
    time.sleep(1.3)

    lyrics = [
        "Har lafz mein tera hi naam hai,",
        "Har raat mein tera hi khayal hai,",
        "Dil ki dhadkan bhi bas tujhe pukaare,",
        "Yeh mohabbat ka ajeeb sa kamaal hai.",
        "",
        "Tere bina adhoori si hai yeh zindagi,",
        "Tere saath mile toh sab kuch aasaan hai,",
        "Chaand bhi sharma jaye teri roshni se,",
        "Tu hi toh meri sabse pyari daastaan hai."
    ]

    colors = [PASSION_PURPLE, GOLDEN_WARM, MIST_WHITE, DEEP_RED]

    for i, line in enumerate(lyrics):
        if line == "":
            print()
            time.sleep(0.6)
            continue
        color = random.choice(colors)
        sensual_typing(line, color)
        time.sleep(0.9)

    time.sleep(1)
    sensual_typing("~ The End ~", BOLD + GOLDEN_WARM)


if __name__ == "__main__":
    run_ehsaas_code()