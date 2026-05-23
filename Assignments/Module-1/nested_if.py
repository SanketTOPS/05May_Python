s1=int(input("Enter Subject1:"))
s2=int(input("Enter Subject2:"))
s3=int(input("Enter Subject3:"))
s4=int(input("Enter Subject4:"))

total=s1+s2+s3+s4
print("Total:",total)

pr=total/4
print("PR:",pr)

if s1>=40 and s2>=40 and s3>=40 and s4>=40:#root - parent
    if pr>=70: #child
        print("Result:A+")
    elif pr>=60: #child
        print("REsult:A")
    elif pr>=50: #child
        print("Result:B")
    elif pr>=40: #child
        print("Result:C")
else:
    print("Result:FAIL")
