import tkinter
from tkinter import ttk,messagebox

tk=tkinter.Tk()
tk.title("NewApp")
tk.geometry("400x400")
tk.config(background="lightblue")

"""l1=tkinter.Label(text="Firstname:")
l1.pack()

l2=tkinter.Label(text="Lastname:")
l2.pack()"""

"""l1=tkinter.Label(text="Firstname:",bg="lightblue",fg="red",font='Courier 15 bold')
l1.place(x=0,y=0)

l2=tkinter.Label(text="Lastname:",bg="lightblue",fg="red",font='Courier 15 bold')
l2.place(x=0,y=30)"""

l1=tkinter.Label(text="Firstname:",bg="lightblue",fg="red",font='Courier 15 bold')
l1.grid(row=0,column=0,sticky='w')

l2=tkinter.Label(text="Lastname:",bg="lightblue",fg="red",font='Courier 15 bold')
l2.grid(row=1,column=0,sticky='w')

t1=tkinter.Entry()
t1.grid(row=0,column=1,sticky='w')
t2=tkinter.Entry()
t2.grid(row=1,column=1,sticky='w')

r1=tkinter.Radiobutton(value=0,text="Male",bg="lightblue",fg="red",font='Courier 15 bold')
r2=tkinter.Radiobutton(value=1, text="Female",bg="lightblue",fg="red",font='Courier 15 bold')
r1.grid(row=2,column=0,sticky='w')
r2.grid(row=2,column=1,sticky='w')

ch1=tkinter.Checkbutton(text="Django",bg="lightblue",fg="red",font='Courier 15 bold')
ch2=tkinter.Checkbutton(text="Flask",bg="lightblue",fg="red",font='Courier 15 bold')
ch3=tkinter.Checkbutton(text="Oddo",bg="lightblue",fg="red",font='Courier 15 bold')

ch1.grid(row=3,column=0,sticky='w')
ch2.grid(row=4,column=0,sticky='w')
ch3.grid(row=5,column=0,sticky='w')

city=['Rajkot','Ahmedabad','Surat','Baroda']
combo=ttk.Combobox(values=city)
combo.grid(row=6,column=0,sticky='w')

def btnClick():
    #print("Button Clicked...")
    """fnm=t1.get()
    lnm=t2.get()
    print("Firstname:",fnm)
    print("Lastname:",lnm)
    """
    #messagebox.showerror("Error","Something went wrong...")
    #messagebox.showinfo("Success","Login Success!")
    #messagebox.showwarning("Warning","Entry missing...")
    messagebox.showinfo("Your Details",f"Firstname:{t1.get()}\nLastname:{t2.get()}")

btn=tkinter.Button(text="Submit",bg="lightblue",fg="red",font='Courier 15 bold',command=btnClick)
btn.place(x=150,y=250)

tk.mainloop()