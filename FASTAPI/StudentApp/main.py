from fastapi import FastAPI

app=FastAPI()

stdata=[
    {
        'id':101,
        'name':'sanket'
    },
    {
            'id':102,
            'name':'nirav'
    },
    {
            'id':103,
            'name':'ashok'
    },
    {
            'id':104,
            'name':'hitesh'
    },
]

@app.get("/")
def home():
    return stdata

@app.post("/student")
def savedata():
        data={
                'id':106,
                'name':'jitesh'
        }          
        stdata.append(data)
        return {'msg':'Student added!',
                'data':data}

