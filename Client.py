#####################################
# Client.py
#####################################
import threading
from socket import *

global loggedIn
loggedIn = False
global userID


#####################################
# Function: logout
#####################################
def logout():
    clientSocket = server_connect()
    print("Logging out.")
    msg = "LOGOUT\t" + userID
    msg = msg.encode()
    clientSocket.send(msg)
    response = clientSocket.recv(4096)
    response = response.decode()
    if response.split("\t")[1].upper() == "FALSE":
        print("Failed to Logout")
    else:
        print("Logged out")
        global loggedIn
        loggedIn = False
    clientSocket.close()
# End of function logout


#####################################
# Function: message
#####################################
def message():
    clientSocket = server_connect()
    toUser = input("Who are you sending a message to:\t")
    msg = input("Type you message:\t")
    msg = "MESSAGE\t"+userID+"\t"+toUser+"\t"+msg
    msg = msg.encode()
    clientSocket.send(msg)
    response = clientSocket.recv(4096)
    response = response.decode()
    if response.split("\t")[3].upper() == "FALSE":
        print("Message failed to send to " + toUser + ".")
    clientSocket.close()
# End of function message

#####################################
# Function: login
#####################################
def login():
    clientToServer = server_connect()
    global userID
    userID = input("Please enter your userid:\t")
    msg = "LOGIN"+"\t"+userID
    msg = msg.encode()
    clientToServer.send(msg)
    response = clientToServer.recv(4096)
    response = response.decode()
    clientToServer.close()
    if("FALSE" in response.upper()):
        print("Failed to login", response)
    else:
        nice = response.split("\t")[0] + "\t" +response.split("\t")[1]
        print("Logged In")
        global loggedIn
        loggedIn = True
# End of function login


#####################################
# Function: userList
#####################################
def userList():
    clientSocket = server_connect()
    msg = "USERLIST"
    msg = msg.encode()
    clientSocket.send(msg)
    response = clientSocket.recv(4096)
    response = response.decode()
    for a in response.split("\t"):
        print(a)
    clientSocket.close()
# End of function userList


#####################################
# Function: server_connect
#####################################
def server_connect():
    serverName = "127.0.0.1"
    serverPort = 12012
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    return clientSocket
# End of function server_connect


#####################################
# Function: handler
#####################################
def handler(connectionSocket):
    message = connectionSocket.recv(4096)
    message = message.decode()
    wholeMsg = message.split("\t")
    if wholeMsg[0] == "MESSAGE":
        if wholeMsg[2] == userID:
            print("Message from user " + wholeMsg[1])
            print(wholeMsg[3])
            response = "MESSAGE\t" + wholeMsg[1] + "\t" + userID + "\tTrue"
            response = response.encode()
            connectionSocket.send(response)
        else:
            print("This message was not meant for you")
    else:
        print("Error")
    connectionSocket.close()
# End of function handler


#####################################
# Function: inputListen
#####################################
def inputListen():
    listeningPort = 12013
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.bind(('', listeningPort))
    clientSocket.listen(10)
    while True:
        connectionSocket, address = clientSocket.accept()
        handler(connectionSocket)
# End of function inputListen


#####################################
# Function: userLoop
#####################################
def userLoop():
    while(True):
        if(loggedIn):
            print("1 - message")
            print("2 - get list of online users")
            print("0 - for log-out")
            print(" ")
            choice = int(input("Your choice is: "))
            if choice == 1:
                message()
            elif choice ==2:
                userList()
            elif choice == 0:
                logout()
        else:
            print("1 - for log-in")
            print("0 - for log-out")
            print(" ")
            choice = int(input("Your choice is: "))
            if choice == 1:
                login()
            elif choice == 0:
                exit(0)
# End of function userLoop


# Main Program
global listeningThread
listeningThread = threading.Thread(target=inputListen)
listeningThread.daemon = True
userThread = threading.Thread(target=userLoop)
listeningThread.start()
userThread.start()
