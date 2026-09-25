# def even_genrator(n):
#     for num in range(1,n+1):
#         if num%2 == 0:
#          yield(num)
# even_num = even_genrator(20)

# for num in even_num:
#     print(num)



def even_genrator(n):
    for num in range(2,n+1,2):
       yield(num)
even_num = even_genrator(20)

for num in even_num:
     print(num)