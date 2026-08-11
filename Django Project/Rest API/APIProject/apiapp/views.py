from django.shortcuts import render
from .serializers import *
from .models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

@api_view(['GET'])
def getall(request):
    udata=Userinfo.objects.all()
    serial=UserSerial(udata,many=True)
    return Response(data=serial.data,status=status.HTTP_200_OK)
    
@api_view(['GET'])
def getuid(request,id):
    try:
        uid=Userinfo.objects.get(id=id)
    except Userinfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serial=UserSerial(uid)
    return Response(data=serial.data,status=status.HTTP_200_OK)

@api_view(['GET','DELETE'])
def deleteuid(request,id):
    try:
        uid=Userinfo.objects.get(id=id)
    except Userinfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method=='GET':
        serial=UserSerial(uid)
        return Response(data=serial.data,status=status.HTTP_200_OK)
    if request.method=='DELETE':
        Userinfo.delete(uid)
        return Response(status=status.HTTP_202_ACCEPTED)
        
@api_view(['POST'])
def savedata(request):
    if request.method=='POST':
        serial=UserSerial(data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT'])    
def updatedata(request,id):
    try:
        uid=Userinfo.objects.get(id=id)
    except Userinfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method=='GET':
        serial=UserSerial(uid)
        return Response(data=serial.data,status=status.HTTP_200_OK)
    if request.method=='PUT':
        serial=UserSerial(data=request.data,instance=uid)
        if serial.is_valid():
            serial.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        