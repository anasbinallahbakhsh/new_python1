def is_palindrome(word):
    reverse_word = word[::-1]

    if word == reverse_word:
        return True
    else:
        return False


print(is_palindrome("madam"))   # True
print(is_palindrome("level"))   # True
print(is_palindrome("horse"))   # False
print(is_palindrome("naman"))   # True