import wozzit
import network   # pylint: disable=all
import time
import wifimgr
import machine, ssd1306

# Little helper for displaying on a SSD1306 OLED screen
def oledPrint(l1=None, l2=None, l3=None, l4=None, clear=True):
    if clear:
        oled.fill(0)
    if l1 is not None:
        oled.text(l1, 0, 0)
    if l2 is not None:
        oled.text(l2, 0, 10)
    if l3 is not None:
        oled.text(l3, 0, 20)
    if l4 is not None:
        oled.text(l4, 0, 30)
    oled.show()

# Helper for maintaining a wifi connection
def wifiConnect():

    # Manage Wifi connection
    wlan = wifimgr.get_connection()
    if wlan is None:
        print("Could not initialize the network connection.")
        oledPrint(l1="No Wifi connection")
        while True:
            pass  # you shall not pass :D
    else:
        print("Connected to wifi")
        oledPrint('Connected',wlan.ifconfig()[0])

# Configure OLED display
i2c = machine.I2C(scl=machine.Pin(4), sda=machine.Pin(5))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Set the URL to your upstream Wozzit Node
to = "http://192.168.0.2:10207/"

# Create new server instance
svr = wozzit.Server()

# The following would typically be in a some kind of loop

# Initiate wifi connection (call every time you want to send)
wifiConnect()

# Create new message instance
msg = wozzit.Message()

# Set message properties (mainly schema and payload)
# msg.schema = "org.example.my-unique-schema-name"
# msg.payload = {"status": "endoflevel", "princess": {"location": "another_castle"}}

# Send the message
print("Sending: " + msg.toJSON())
oledPrint(l3='Sending...', clear=False)
r = svr.send(msg, to)

# The response is a Message instance. If the schema is wozzit.error, there was a problem
# Otherwise, expect wozzit.receipt
print("Response:")
print(r.toJSON())
if(r.schema == 'wozzit.receipt'):
    oledPrint(l4='Successful', clear=False)
else:
    oledPrint(l4='Error!', clear=False)

