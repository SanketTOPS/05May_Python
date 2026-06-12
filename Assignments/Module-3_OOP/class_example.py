class Tops:
    stid=101
    stnm="Sanket"
    
    def getdata(self):
        print("This is class")
        
    def getsum(self,a,b):
        print("Sum:",a+b)


#Object of class
tp=Tops()
print("ID:",tp.stid)
print("Name:",tp.stnm)
tp.getdata()
tp.getsum(23,43)