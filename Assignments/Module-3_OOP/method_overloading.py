class Studinfo:
    #Method Overloading
    def getdata(self,id):
        print("ID:",id)
        
    def getdata(self,name):
        print("Name:",name)
        
st=Studinfo()
st.getdata(101)
st.getdata("Sanket")