user={}

name=input('Enter your name:')
age=input('What is your age:')
fav_tune=input('your favorite tunes separted by comma:').split(',')
fav_movies=input('your favorite movess sepreted by comma:').split(',')


user['name']=name
user['age'] =age
user['fav_tune']=fav_tune
user['fav_movies']=fav_movies

print(user)

for key, values in user.items():
    print(f"{key}:{values}")
