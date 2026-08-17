#advance min and max 

# numbers=[1,2,4,5,7]
# print(max(numbers))

names=['Anas allahbuksh','malik','ab','z']
print(max(names, key= lambda item : len(item)))


students={
     'Anas':{'score':90, 'age':17},
     'sana':{'score': 75, 'age':16},
      'ahmed':{'score': 76, 'age':15}
      }
print(max(students, key= lambda item: students[item]['score']))
# students2 = [
#     {'name': 'harshit', 'score': 90, 'age': 24},
#     {'name': 'mohit', 'score': 70, 'age': 19},
#     {'name': 'rohit', 'score': 60, 'age': 23},
# ]

# print(max(students2, key= lambda item:item.get('age')).get('name'))