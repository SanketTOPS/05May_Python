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

