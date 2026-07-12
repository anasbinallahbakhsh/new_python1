def is_palindrome(word):
    reversed_word = word[::-1]
    if reversed_word == word:
        return True
    else:
        return False
print(is_palindrome("level"))#true
print(is_palindrome("anas"))#false
print(is_palindrome("madam"))#true


def is_palindrome(word):
    
    if word == word[::-1]:
        return True
    return False
print(is_palindrome("level"))#true
print(is_palindrome("anas"))#

def is_plaindrome(word):
    return word == word [::-1]
print(is_palindrome("madam"))
print(is_palindrome("level"))


def is_plaindrome(word):
    return word ==word[::-1]
print(is_palindrome("anas"))#false
print(is_palindrome("level"))#tuue
print(is_palindrome("naman"))#true