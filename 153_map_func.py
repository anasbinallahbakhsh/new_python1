# map function
numbers = [1, 2, 3]

squared = list(map(lambda a: a**2, numbers))
print(squared)

# list comprehension
another_square = [i**2 for i in numbers]
print(another_square)

# loop version
def square(a):
    return a**2

new_list = []
for num in numbers:
    new_list.append(square(num))
print(new_list)

names=['abc','abcd','abcde']
length=list(map(len,names))
for i in length:
  print(i)

  print(length)