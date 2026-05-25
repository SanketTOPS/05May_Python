stdata={'id':101,'name':'sanket','city':'rajkot'}
#print(stdata)
#print(stdata["name"])
#print(stdata.get("city"))

#print(stdata.keys())
#print(stdata.values())

#print(len(stdata))

"""if 'name' in stdata:
    print("Yes...")
else:
    print("Noo")"""
    
"""if 'sanket' in stdata.values():
    print("Yes...")
else:
    print("Noo")"""
    
"""for i in stdata:
    print(i)"""
    
"""for i in stdata.values():
    print(i)"""
    
"""for i in stdata.items():
    print(i)"""

"""for i,j in stdata.items():
    #print(i,j)
    print(f"Key:{i} and Value:{j}")"""
    
# ------------------------ #
#print(stdata)
#stdata["id"]=102 #Update value
#stdata["sub"]="Python" #Value Add
#stdata.pop('city')
#stdata.clear()
#del stdata
#del stdata["id"]
print(stdata)

#newstdata=stdata.copy()
#print(newstdata)

newstdata={'id':102,'name':'Nirav','city':'Baroda'}
print(newstdata)