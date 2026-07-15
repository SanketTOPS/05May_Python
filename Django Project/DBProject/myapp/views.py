from django.shortcuts import render,redirect
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

def updatedata(request,id):
    stid=Userinfo.objects.get(id=id)
    if request.method=='POST':
        user=UserForm(request.POST,instance=stid)
        if user.is_valid():
            user.save()
            print("Record updated!")
            return redirect('showdata')
        else:
            print(user.errors)
    return render(request,'updatedata.html',{'stid':stid})

def deletedata(request,id):
    stid=Userinfo.objects.get(id=id)
    Userinfo.delete(stid)
    return redirect('showdata')