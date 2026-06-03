import pandas

"""stdata={
    'id':[1,2,3,4,5],
    'name':['sanket','hitesh','ashok','darshan','gopal'],
    'city':['rajkot','baroda','surat','ahmedabad','navsari']
}"""

#print(stdata)
"""dt=pandas.DataFrame(stdata)
print(dt)"""

# -------------------- #

dt=pandas.read_excel('data.xlsx')
print(dt)
