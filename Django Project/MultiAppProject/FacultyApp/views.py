from django.shortcuts import render
from StudApp.models import *

# Create your views here.
def findex(request):
    data=StudInfo.objects.all()
    return render(request,'findex.html',{'data':data})