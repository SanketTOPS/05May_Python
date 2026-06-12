class Studinfo:
    stid=0
    stnm=''
    
    def getdata(self):
        self.stid=input("Enter an ID:")
        self.stnm=input("Enter a Name:")
    
    def printdata(self):
        print("ID:",self.stid)
        print("Name:",self.stnm)

st=Studinfo()
st.getdata()
st.printdata()