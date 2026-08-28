#fromkeys
#d={'name','unknown','age','unknown'}


d=dict.fromkeys(['name','age'],['unknown','unknown'])
# print(d)




# get method useful

d={'name':'Muhammad','age':'unknown'}
#print(d['names'])

#print(d.get('name')) BATTER
# if 'naem' in d:
#     print('present')
# else:
#     print('not presentr')

# if d.get('name'):
#     print('present')
# else:
#     print('not present')

# if none false else true

print(d.clear())
print(d)
d1=d.copy()
d1=d
# 
print(d1 is d )