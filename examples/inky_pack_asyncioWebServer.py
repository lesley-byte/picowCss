# To incorporate the pimoroni inky pack with this instead

import network
import socket
import time
from machine import Pin
import uasyncio as asyncio
import secrets
import index
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_INKY_PACK

display = PicoGraphics(display=DISPLAY_INKY_PACK)


display = PicoGraphics(display=DISPLAY_INKY_PACK)

# you can change the update speed here!
# it goes from 0 (slowest) to 3 (fastest)
display.set_update_speed(2)

display.set_font("bitmap8")

button_a = Button(12)  #Buttons not used in this but named incase you want to use them.
button_b = Button(13)
button_c = Button(14)


# a handy function we can call to clear the screen
# display.set_pen(15) is white and display.set_pen(0) is black
def clear():
    display.set_pen(15)
    display.clear()
led = Pin("LED", Pin.OUT, value=0) #Pin(15, Pin.OUT)


onboard = Pin("LED", Pin.OUT, value=0)
#print(secrets.ssid)
ssid = secrets.ssid
password = secrets.psswd
html = index.html
webdocs = "/webroot/"
wlan = network.WLAN(network.STA_IF)
status = wlan.ifconfig()
def connect_to_network():
    wlan.active(True)
    wlan.config(pm = 0xa11140)
    wlan.connect(ssid, password)  
    max_wait = 10
    
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >=3:
            break
        max_wait -=1
        print('Waiting for connection...')
        clear()
        display.set_pen(0)
        display.text("Waiting for Connection", 10, 10, 240, 3)
        display.update()
        time.sleep(0.5)
        time.sleep(1)
        
    if wlan.status() != 3:
        clear()
        display.set_pen(0)
        display.text("Network Connection Failed", 10, 10, 240, 3)
        display.update()
        time.sleep(0.5)
        raise RuntimeError('Network connection failed')
    else:
        print('Connected')
        status = wlan.ifconfig()
        print('IP = ' + status[0])
        clear()
        display.set_pen(0)
        display.text("IP = ", 10, 10, 240, 3)
        display.text(status[0], 10,50,240,3)
        display.text("Connected", 10,90,240,3)
        display.update()
        time.sleep(0.5)
        
async def serve_client(reader, writer):
    print("Client connected")
    request_line = await reader.readline()
    print("Request: ", request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass
    
    request = str(request_line)
    led_on = request.find('/light/on')
    led_off = request.find('/light/off')
    css = request.find('.css')
    js = request.find('.js')
    print('led on = ' + str(led_on))
    print('led off = ' + str(led_off))
    
    
    stateis = ''
    if led_on == 6:
        print("led on")
        led.value(1)
        stateis = "LED is ON"
        clear()
        display.set_pen(0)
        display.text("IP = ", 10, 10, 240, 3)
        display.text(status[0], 10,50,240,3)
        display.text("LED is ON", 10,90,240,3)
        display.update()
        time.sleep(0.5)
        
    if led_off == 6:
        print("led off")
        led.value(0)
        stateis = "LED is OFF"
        clear()
        display.set_pen(0)
        display.text("IP = ", 10, 10, 240, 3)
        display.text(status[0], 10,50,240,3)
        display.text("LED is OFF", 10,90,240,3)
        display.update()
        time.sleep(0.5)
    
    response = html % stateis
    if css > 0:
        print("css")
        requestedfile = request[6:css+4]
        f = open(webdocs + 'stylefile.css')
        response = f.read()
        f.close()
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/css\r\n\n')
        writer.write(response)
    elif js > 0:
        print("js")
        requestedfile = request[6:css+4]
        f = open(webdocs + 'script.js')
        response = f.read()
        f.close()
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/js\r\n\n')
        writer.write(response)
        
    else:
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        writer.write(response)
    
    await writer.drain()
    await writer.wait_closed()
    print("Client disconnected")
    
async def main():
    print('Connecting to network...')
    connect_to_network()
    
    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))
    count = 0
    while True:
        #onboard.on()
        print("heartbeat")
        await asyncio.sleep(0.50)
        print("lub-dub..." + str(count))
        #onboard.off()
        count = count + 1
        await asyncio.sleep(10)
        
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
