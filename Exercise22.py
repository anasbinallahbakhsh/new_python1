def common_founder(l1,l2):
    output=[]
    for i in l1:
            if i in l2:
               output.append(i)
    return output
print(common_founder([1,2,3,4],[1,2,6,7,8]))