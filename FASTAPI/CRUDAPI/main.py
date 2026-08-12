from fastapi import FastAPI
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import declarative_base,Session


app=FastAPI()

#Database Connection

DATSABSE_URL='sqlite:///./tops.db'

db_engine=create_engine(
    DATSABSE_URL,
    connect_args={"check_same_thread": False}
)

Base = declarative_base()

#Model Create
class Studinfo(Base):
    
    __tablename__ = "student"
    id=Column(Integer,primary_key=True)
    name=Column(String)
    city=Column(String)
 
Base.metadata.create_all(bind=db_engine)   


@app.post('/student')
def savedata(name:str,city:str):
    
    with Session(db_engine) as db:
        
        stdata=Studinfo(name=name,city=city)
        db.add(stdata)
        db.commit()
        
        return {'msg':'Record Inserted!'}
    
@app.get("/")
def getdata():
    with Session(db_engine) as db:
        stdata=db.query(Studinfo).all()
        return stdata