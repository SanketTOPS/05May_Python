import re

email=input("Enter your email:")

#sankettops@gmail.com
email_pattern="[a-z0-9._]+[@]+[a-z]+[\.]+[a-z]"

x=re.findall(email_pattern,email)

if x:
    print("Email is Valid....")
else:
    print("Error!Invalid Email...")