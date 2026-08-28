
2# make flexible functions
# * operator args
# *args

def total(*args):
    return sum(args)

def all_total(*args):
    total = 0
    for nums in args:
        total += nums
    return total

print(all_total(1, 2, 3, 4, 5, 6))