import random

class Studinfo:
    """def __init__(self,id):
        print("ID:",id)"""
        
    def __init__(self,unm,pas):
        if unm=='admin' and pas=='admin':
            print("Login Successfull!")
        else:
            print("Error!")
        
    
        
"""n=random.randint(111,999)
st=Studinfo(n)"""

unm=input("Enter Username:")
pas=input("Enter Password:")
st=Studinfo(unm,pas)