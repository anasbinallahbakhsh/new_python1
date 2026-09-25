def power_to(nums,*args):
    if args:
        return[ i**2 for i in nums]
    else:
        return "you didn,t tyoe anthing"
nums=[2,3,4]
print(power_to(2,*nums))