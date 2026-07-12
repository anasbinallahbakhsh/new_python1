def is_palindrome(word):
 reverse_word = word[::-1]
 if word == reverse_word:   
        return True
 else:
        return False
print(is_palindrome("madam"))#true
print(is_palindrome("level"))#true
print(is_palindrome("anas"))#False
    