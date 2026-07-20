# Junior Developer
# def is_palindrome(word):
#     reversed_word = word[::-1]
#     if reversed_word == word:
#         return True
#     else:
#         return False

# print(is_palindrome("level"))   # True
# print(is_palindrome("anas"))    # False
# print(is_palindrome("madam"))   # True


# # Mid-Level Developer
# def is_palindrome(word):
#     if word == word[::-1]:
#         return True
#     return False

# print(is_palindrome("level"))   # True
# print(is_palindrome("anas"))    # False


# Senior Developer
def is_palindrome(word):
    return word == word[::-1]

print(is_palindrome("anas"))    # False
print(is_palindrome("level"))   # True
print(is_palindrome("naman"))   # True