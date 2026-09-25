def filter_even_odd(l):
    even=[]
    odd=[]
    for i in l:
        if i%2 ==0:
           even.append(i)
        else:
            odd.append(i)
        output=[even,odd]
    return output
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
print(filter_even_odd(numbers))