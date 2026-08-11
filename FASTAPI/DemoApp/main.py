from fastapi import FastAPI

app=FastAPI()

@app.get('/')
def home():
    return {"msg":"Welcome to FAST API"}

@app.get('/about')
def about():
    return {"msg":"Welcome to About Page"}

@app.get('/contact')
def contact():
    return {"msg":"Welcome to Contact Page"}


