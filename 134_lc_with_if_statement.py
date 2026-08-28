#list comprehension with if else statement
numbers=list(range (1,11))
#print(numbers)
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#[2,4,6]
nums=[]
for i in numbers:
 if i%2==0:
  nums.append(i)
print(nums)

even_numbers=[i for i in numbers if i%2==0]


even_nums2=[i for i in range(1,20) if i%2==0]


print(even_numbers)
print(even_nums2)
odd_nums=[i for i in range(20,31) if i%2==1]
print(odd_nums)