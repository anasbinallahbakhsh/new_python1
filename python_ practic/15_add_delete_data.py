# add_and_delete
user_info={
    'name':'Anas',
    'age':'24',
    'favorite_move':['coco','kimi no na wa'],
    'favorite_tune':['awakening','fairy tale']
}


#how to add data
# user_info['fav_song']=['song1','song2']
# print(user_info)
#pop method
popped_item=user_info.pop('favorite_tune')
print(type(popped_item))
print(user_info)


#popitem method
# popped_item=user_info.popitem()
# print('user_info')
# print(type(popped_item))