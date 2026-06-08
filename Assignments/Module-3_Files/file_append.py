file=open('tenp.txt','a')


id=input("Enter an ID:")
name=input("Enter a Name:")

file.write(f"\nID:{id}\nName:{name}")