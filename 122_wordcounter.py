#word counter
# Anas
def word_conter(s):
    count={}
    for char in s:
        count[char]= s.count(char) 
    return count
print(word_conter("anass"))