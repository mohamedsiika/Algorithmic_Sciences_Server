import socket
import threading


# port=44445
# IP="135.181.96.160"
import time

port = 5050
IP = "localhost" #socket.gethostbyname(socket.gethostname())  # gets the ip server
ADDR = (IP, port)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
text=input().encode()
client.send(text)

msg=client.recv(1024)
print(msg)
time.sleep(3)
