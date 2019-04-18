#********************************************
# Client.py
#*********************************************
from socket import *

loggedIn = False
global clientToServer


#************************************
# Function: logout
#************************************
def logout(clientSocket):
    print("Quitting...Bye Bye!")
    clientSocket.send("QUIT".encode())
    clientSocket.shutdown(1)
    clientSocket.close()
    exit(0)
# End of function logout

#************************************
# Function: message
#************************************
def message(clientSocket):
    msg = input("Type you message:\t")
    msg = "MESSAGE\t"+msg
    msg = msg.encode()
    clientSocket.send(msg)
    print("Message sent")
    response = clientSocket.recv(4096)
    response.decode()
    print(str(response))
# End of function message

#************************************
# Function: login
#************************************
def login():
    global clientToServer
    clientToServer = server_connect()
    userid = input("Please enter your userid:\t")
    msg = "LOGIN"+"\t"+userid+"\t"
    msg = msg.encode()
    clientToServer.send(msg)
    response = clientToServer.recv(4096)
    response = response.decode()
    if("BAD" in response.upper()):
        print("Failed to login", response)
    else:
        nice = response.split("\t")[0] + "\t" +response.split("\t")[0]
        print(nice)
        global loggedIn
        loggedIn = True
# End of function login


#************************************
# Function: server_connect
#************************************
def server_connect():
    serverName = "127.0.0.1"
    serverPort = 12012
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    print("Connection successful, ready to communicate")
    return clientSocket
#End of function server_connect

#Main Program Loop
while(True):
    if(loggedIn):
        print("1 - message")
        print("0 - for log-out")
        print(" ")
        choice = int(input("Your choice is: "))
        print(type(choice))
        if choice == 1:
            message(clientToServer)
        elif choice == 0:
            logout(clientToServer)
            break
    else:
        print("1 - for log-in")
        print("0 - for log-out")
        print(" ")
        choice = int(input("Your choice is: "))
        if choice == 1:
            login()
        elif choice == 0:
            logout()
            break
