file=open('test.txt','w')


id=input("Enter an ID:")
name=input("Enter a Name:")

"""file.write(id)
file.write(name)"""

file.write(f"ID:{id}\nName:{name}")