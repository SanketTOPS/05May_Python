class sanket:
    sid:int
    scourse:str
    
    def s_getdata(self):
        self.sid=input("Enter Sanket's ID:")
        self.scourse=input("Enter Sanket's Course:")

class nirav(sanket):
    nid:int
    ncourse:str
    
    def n_getdata(self):
        self.nid=input("Enter Nirav's ID:")
        self.ncourse=input("Enter Nirav's Course:")

class harsh(nirav):
    hid:int
    hcourse:str
    
    def h_getdata(self):
        self.hid=input("Enter Harsh's ID:")
        self.hcourse=input("Enter Harsh's Course:")
    
class tops(harsh):
    def display(self):
        print("----Sanket's Info----")
        print("Sanket's ID:",self.sid)
        print("Sanket's Course:",self.scourse)
        print("----Nirav's Info----")
        print("Nirav's ID:",self.nid)
        print("Nirav's Course:",self.ncourse)
        print("----Harsh's Info----")
        print("Harsh's ID:",self.hid)
        print("Harsh's Course:",self.hcourse)
        
tp=tops()
tp.s_getdata()
tp.n_getdata()
tp.h_getdata()
tp.display()