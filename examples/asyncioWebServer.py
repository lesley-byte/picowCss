import network
import socket
import time
from machine import Pin
import uasyncio as asyncio
import secrets
led = Pin("LED", Pin.OUT, value=0) #Pin(15, Pin.OUT)
onboard = Pin("LED", Pin.OUT, value=0)
#print(secrets.ssid)
ssid = secrets.ssid
password = secrets.psswd

html = """<!DOCTYPE html>
<html lang="en">
    <head> 
        <meta charset="UTF-8"/>
        <link rel="stylesheet" href="/stylefile.css">
        <title>Pico W</title>
    </head>
    <body>
        <main>
        <h1>Pico</h1>
        <p>%s</p>
        <a href="/light/on">Light On</a> </br>
        <a href="/light/off">Light Off</a> </br>
        </main>
        <script type="text/javascript" src="script.js"></script>
    </body>
</html>
"""
webdocs = "/webroot/"

wlan = network.WLAN(network.STA_IF)

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
        time.sleep(1)
        
    if wlan.status() != 3:
        raise RuntimeError('Network connection failed')
    else:
        print('Connected')
        status = wlan.ifconfig()
        print('IP = ' + status[0])
        
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
        
    if led_off == 6:
        print("led off")
        led.value(0)
        stateis = "LED is OFF"
        
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
