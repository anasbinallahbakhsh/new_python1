#iterator vs iterable
numbers=[1,2,3,4] #itrable
squares = map(lambda a:a**2 , numbers) # iterator


print(next(squares))
print(next(squares))
print(next(squares)) 