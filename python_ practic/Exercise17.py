def reverse_element(l):
    elements=[]
    for i in l:
        elements.append(i[::-1])
    return elements

words=["ans","malik1","zohaib"]
print(reverse_element(words))

