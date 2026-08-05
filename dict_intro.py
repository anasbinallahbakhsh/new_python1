# dictinories intro
# Q - we we use dactnories ?
# A - becausae of limmition of list, list are enough represent 
# real data 
#Example
user=['Anas',16,['coco','kimi no na wa',]],['awekening','fairy tale']
# this list conatain username ,age fav movies,fav ringtones

# Q - what are dictironaries
# A- unorderd collecations of data in key : value pair

# how to create dictinories

user= {'name' : 'Anas', 'age':'16'}
#print(user)
#print(type(user))

# seond method to create dictinories
user1=dict(name='Anas', age= '16')
#print(user1)
print(user['name'])



# which type of data dictnoiry can store
# A- anything
# numbers,strings,list,dictnory


user_info={
    'name': 'Anas',
    'age' : 16,
    'fav_movies':['coco','kimi no na wa'],
    'fav_tunes':['awekening','fairy tale']
}
#print(user_info['fav_movies'])
user_info2={}
user_info2['name']='mohit'
user_info2['age']='16'
print(user_info2)
# How to add data in  empty dictionary
