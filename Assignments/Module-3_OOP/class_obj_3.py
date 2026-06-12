class Studinfo:
    def getdata(self,stid,stnm):
        print("ID:",stid)
        print("name:",stnm)


st=Studinfo()
#st.getdata(1,'Nirav')
stid=input("Enter an ID:")
stnm=input("Enter a Name:")
st.getdata(stid,stnm)