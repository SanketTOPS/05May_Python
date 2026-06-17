class Studinfo:
    #private
    __stid=101
    __stnm="Sanket"
    
    def __getdata(self): #private
        print("ID:",self.__stid)
        print("Name:",self.__stnm)
    
    def display(self):
        self.__getdata()
    
st=Studinfo()
st.display()

