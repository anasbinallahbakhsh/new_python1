#replace() method
#find() method
string=("she is beautiful and she is good dancer")
#print(string.replace("is","was", 2)) # yaha par mai bta saku ga ka kitna ya konsa woeld change karna hai
#find method kafi useful ha
is_pos1=string.find("is")
is_pos2=string.find("is",is_pos1 + 1)
print(is_pos2)