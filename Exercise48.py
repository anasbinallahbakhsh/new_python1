def even_genrator(n):
    for nums in range(2,n+1,2):
      yield(nums)
even_num=even_genrator(20)
for num in even_num:
     print(num)



