def common_element(list1, list2):
    common = []

    for i in list1:
        if i in list2:
            common.append(i)

    return common


list1 = [1, 2, 3, 4, 5, 5]
list2 = [1, 2, 7, 8, 9, 0]

print(common_element(list1, list2))