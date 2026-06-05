import qrcode

#url="https://www.tops-int.com/"

data="Hello Students!"

qr=qrcode.make(data)
qr.save("dt.png")