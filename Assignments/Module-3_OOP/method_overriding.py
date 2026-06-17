class Master:
    def signin(self,unm,pas):
        if unm=="admin" and pas=="admin":
            print("Login Success")
        else:
            print("Error!")

class home(Master):
    def signin(self, unm, pas):
        return super().signin(unm, pas)
    
    
class about(Master):
    def signin(self, unm, pas):
        return super().signin(unm, pas)