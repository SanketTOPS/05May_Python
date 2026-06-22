import sqlite3

try:
    db=sqlite3.connect('tops.db')
    print("Database created/connected!")
except Exception as e:
    print(e)

#Table Create
tbl_create="create table studinfo(id integer primary key autoincrement,name varchar(20),city varchar(20))"

try:
    db.execute(tbl_create)
    print("Table created!")
except Exception as e:
    print(e)
    
#Insert Data
"""insert_data="insert into studinfo(name,city)values('sanket','rajkot'),('nirav','surat'),('ashok','bhavnagar'),('hitesh','baroda'),('mahesh','ahmedabad')"

try:
    db.execute(insert_data)
    db.commit()
    print("Record inserted!")
except Exception as e:
    print(e)"""
    
#Update Data
"""update_data="update studinfo set city='navsari' where id=4"
try:
    db.execute(update_data)
    db.commit()
    print("Record updated!")
except Exception as e:
    print(e)"""

#Delete_Data
"""delete_data="delete from studinfo where id=5"
try:
    db.execute(delete_data)
    db.commit()
    print("Record deleted!")
except Exception as e:
    print(e)"""

cr=db.cursor()

#Select Data
select_data="select * from studinfo"
try:
    cr.execute(select_data)
    data=cr.fetchall()
    #data=cr.fetchmany(3)
    #data=cr.fetchone()
    #print(data)
    for i in data:
        print(i)
except Exception as e:
    print(e)
    