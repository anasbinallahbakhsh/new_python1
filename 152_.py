# we use enumerate function with for loop to track position of our
# item in iterable


names = ['abc', 'abcdef', 'anas']

# without enumerate function
pos = 0
for name in names:
    print(f"{pos} -------> {name}")
    pos += 1


# with enumerate function
for pos, name in enumerate(names):
    print(f"{pos} ---> {name}")


# define a function that takes two arguments
# 1.) list containing strings
# 2.) string that you want to find in list
def find_pos(l, target):
    for pos, name in enumerate(l):
        if name == target:
            return pos
    return -1


print(find_pos(names, 'anas'))