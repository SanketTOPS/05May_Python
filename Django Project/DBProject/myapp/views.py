from django.shortcuts import render
from .forms import *

# Create your views here.
def index(request):
    if request.method=='POST':
        user=UserForm(request.POST)
        if user.is_valid():
            user.save()
            print("Record inserted!")
        else:
            print(user.errors)
    return render(request,'index.html')

def showdata(request):
    data=Userinfo.objects.all()
    return render(request,'showdata.html',{'data':data})