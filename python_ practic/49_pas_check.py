import re

def check_password_strength(password):
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password kam az kam 8 characters ka hona chahiye.")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Kam az kam 1 uppercase letter add karo.")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Kam az kam 1 lowercase letter add karo.")

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Kam az kam 1 number add karo.")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Kam az kam 1 special character add karo.")

    if score == 5:
        strength = "Very Strong"
    elif score >= 4:
        strength = "Strong"
    elif score >= 3:
        strength = "Medium"
    else:
        strength = "Weak"

    return strength, feedback


if __name__ == "__main__":
    pwd = input("Enter a password: ")
    strength, feedback = check_password_strength(pwd)

    print(f"\nPassword Strength: {strength}")

    if feedback:
        print("Suggestions:")
        for item in feedback:
            print("-", item)