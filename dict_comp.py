#dicitionory comprehesion 
 #sequre[1:1,2:4,3:9]
square={f" square of  {num} is   in ":num**2 for num in range(1,11)}
print(square)
for k,v in square.items(): 
    print(f"{k},{v}")

string="anas"
word_count={char:string.count(char) for char in string}
# chracter cont in dict
print(word_count)