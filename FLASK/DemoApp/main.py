from flask import Flask

app=Flask(__name__) #app init.

@app.route('/')
def index():
    return "Hello Flask!"

@app.route('/about')
def about():
    return "This is About!"

@app.route('/contact')
def contact():
    return "This is Contact!"

app.run(debug=True,port=3800)
