# list compreshhension
# square=[i**2 for i in range(1,11)]
# print(square)

# how to use if statement in lc

# even_num=[i for i in range(1,11) if i%2==0 ]
# print(even_num)
# mixed=[i*2 if (i%2==0) else -i for i in range(1,11)]
# print(mixed)

n1=[[1,2,3],[1,2,3],[1,2,3]]
new_lsit=[ [i for i in range(1,4)] for j in range (3)]
print(new_lsit)