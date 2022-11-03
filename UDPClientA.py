import socket

serverName='localhost'
serverPort=18000

loop=True
while loop==True:
    print("_________________________________________________")
    print("_____________________MENU________________________")
    print("_________________________________________________")
    print()
    print("1. Get a file from the server.")
    print("2. Quit the programm.")
    choice=input("-->")
    if choice=="1":
        loop=False
    elif choice=="2":
        quit()

loop=True
while loop==True:
    print("__________Select the type of connexion___________")
    print()
    print("1. Use HTTP version 1.0 (non-persistent).")
    print("2. Use HTTP version 1.1 (persistent). ")
    choice = input("-->")
    loop=False
    '''if choice == "1":
        loop = False
    elif choice == "2":
        quit()'''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("[CLIENT]: TCP SYN request sent to the server")
s.connect(('127.0.0.1', serverPort))
print("[CLIENT]: A connexion has been established with the server" + serverName + ":" + str(serverPort))
msg = input("[CLIENT]: Enter a message to the server or exit")
while msg != 'exit':
    s.sendto(msg.encode(), (serverName, serverPort))
    data = s.recvfrom(2048)
    print("[SERVER]:", data)
    msg = input("[CLIENT]: Enter a message to the server or exit")
s.close()