#summary dicitiory
#what is dicitinory
#unordered collecation of data


d={'name':'anas','age':'19'}


#or
d1=dict(name='anas', age='19')

#or
d2={
    'name':'anas',
    'age':'17',
    'fav_movies':[]
}

#how to access data from dictinory
#you canot do like
#d[0], there is no order in dictinory
#print(d['name'])


#add data inside empty list
empty_dict={}

empty_dict['key1']='value1'

empty_dict['key2']='value2'
#print(empty_dict
#

#cheack excating of values inside dict
#use in keyword for check keys


#how to intarite our dictinoey
#most common method
#for key values in item ():
# print(f"key is {key} and value is value {values}")

#to print all keys
# for i in d:
    # print(i)


    #get method
    #how to check key and excitence
#print(d.get('name'))


#Q- why we use get method
#A- to get rid of error

#Example
#print(d["name"
#        ])
#print(d.get("nameS"))

# TO  item we used pop method
#pop take one argumments which is keyname

# popped=d.pop("name")
# print(popped)
# print(d)


#popped item
popped=d.popitem()
print(popped)
print(d)