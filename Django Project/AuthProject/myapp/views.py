from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth import logout

# Create your views here.
def login(request):
    if request.method=='POST':
        email=request.POST["email"]
        pas=request.POST["password"]
        
        user=Usersignup.objects.filter(email=email,password=pas)
        if user:
            print("Login Successfull!")
            request.session['user']=email #session create
            return redirect('home')
        else:
            print("Error!Login Faild...")
    return render(request,'login.html')

def signup(request):
    if request.method=='POST':
        req=SignupForm(request.POST)
        if req.is_valid():
            req.save()
            print("Signup Successfully!")
            return redirect('/')
        else:
            print(req.errors)
    return render(request,'signup.html')

def home(request):
    user=request.session.get('user')
    return render(request,'home.html',{'user':user})

def userlogout(request):
    logout(request)
    return redirect('/')