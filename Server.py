#####################################
# Server.py
#
# A server for multiple user messaging,
# uses a thread pool to handle communication
# with clients.
#####################################
from socket import *
from datetime import datetime
import threading
from multiprocessing.dummy import Pool

global userListLock
global userInfo
global userPort

#####################################
# Function: loginProcessing
#
# Takes and checks passed in user name, saves address,
# and gives the user a listening port to use
# (to avoid conflicts since were running
# this on a single machine).
#####################################
def loginProcessing(request, connectionSocket, address):
    userid = request.split('\t')[1].strip()
    global userPort
    input = (userid, address, userPort)
    good = add_user_to_list(input)
    response = "LOGIN\t" + str(good)
    if good:
        response += "\t" + str(userPort)
        userPort += 1
        print(str(datetime.now()) + ": " + str(userid) + " logged in.")
    response = response.encode()
    connectionSocket.send(response)
    connectionSocket.close()
    return good
# End of function loginProcessing


#####################################
# Function: messageProcessing
#
# Takes the message, gets the recipient's
# connection information, sends message to
# recipient, then waits for an ack and
# passes back the ack or nack.
#####################################
def messageProcessing(request,connectionSocket):
    sender = request.split("\t")[1]
    receiver = request.split("\t")[2]
    msg = request.split("\t")[3]
    outgoing = "MESSAGE\t" + sender + "\t" + receiver + "\t" + msg
    outgoing = outgoing.encode()
    addr, usrPort = get_user_socket(receiver)
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((addr, usrPort))
    clientSocket.send(outgoing)
    print(str(datetime.now()) + ": " + str(sender) + " is sending a message to " + str(receiver))
    ack = clientSocket.recv(4096)
    ack = ack.decode()
    ackMsg = ack.split("\t")[3]
    clientSocket.close()
    resp = "MESSAGE\t" + sender + "\t" + receiver + "\t" + ackMsg
    resp = resp.encode()
    connectionSocket.send(resp)
    connectionSocket.close()
# End of function messageProcessing


#####################################
# Function: getListProcessing
#
# Takes a request from a client for the
# list of currently connected users and
# sends client the list.
#####################################
def getListProcessing(connectionSocket):
    lst = get_user_list()
    message = "USERLIST\t"
    for a in lst:
        message += str(a) + "\t"
    message = message.encode()
    connectionSocket.send(message)
    connectionSocket.close()
# End of function getListProcessing


#####################################
# Function: logoutProcessing
#
# Takes a logout request from client, removes
# client for list of active users, and then
# lets client know they've been logged out.
#####################################
def logoutProcessing(message,connectionSocket):
    userid = message.split('\t')[1].strip()
    success = remove_user_from_list(userid)
    print(str(datetime.now()) + ": " + str(userid) + " logged out.")
    response = "LOGOUT\t" + str(success)
    response = response.encode()
    connectionSocket.send(response)
    connectionSocket.close()
# End of function logoutProcessing


#####################################
# Function: add_user_to_list
#
# Adds the users name, ip address, and
# listening port number to list of active
# clients.
# Threads need to acquire lock to access the list.
#####################################
def add_user_to_list(userName):
    userListLock.acquire()
    alreadyExists = False
    for a in range(0,len(userInfo)):
        if userInfo[a][0] == userName[0]:
            alreadyExists = True
    if not alreadyExists:
        userInfo.append(userName)
    userListLock.release()
    return not alreadyExists
# End of function add_user_to_list


#####################################
# Function: get_user_list
#
# Gets the list of current users from user
# list and returns it.
# Threads need to acquire lock to access the list.
#####################################
def get_user_list():
    userListLock.acquire()
    names = []
    for a in range(0, len(userInfo)):
        names.append(userInfo[a][0])
    userListLock.release()
    return names
# End of function get_user_list


#####################################
# Function: remove_user_from_list
#
# Takes in a user name and removes that user
# from the current user list.
# Threads need to acquire lock to access the list.
#####################################
def remove_user_from_list(userName):
    userListLock.acquire()
    inList = False
    index = -1
    for a in range(0, len(userInfo)):
        if userInfo[a][0] == userName:
            inList = True
            index = a
    if inList:
        userInfo.pop(index)
    userListLock.release()
    return inList
# End of function remove_user_from_list


#####################################
# Function: get_user_socket
#
# Takes in a user name and returns their
# ip address and listening port.
# Threads need to acquire lock to access the list.
#####################################
def get_user_socket(userName):
    userListLock.acquire()
    for a in range(0,len(userInfo)):
        if userInfo[a][0] == userName:
            outputAddr = userInfo[a][1]
            outputPort = userInfo[a][2]
    userListLock.release()
    return outputAddr, outputPort
# End of function get_user_socket


#####################################
# Function: handler
#
# Initially handles message from client
# and routes to approiate function for
# further handling.
#####################################
def handler(connectionSocket, address):
    message = connectionSocket.recv(4096)
    message = message.decode()
    request = message.split("\t")[0]

    # Parse the method name from the request message
    methodName = request.split('\t')[0].strip()

    if(methodName.upper() == "LOGIN"):
        loginProcessing(message, connectionSocket, address)
    elif(methodName.upper() == "MESSAGE"):
        messageProcessing(message,connectionSocket)
    elif(methodName.upper() == "LOGOUT"):
        logoutProcessing(message,connectionSocket)
    elif(methodName.upper() == "USERLIST"):
        getListProcessing(connectionSocket)
    else:
        print("Something went wrong")

    connectionSocket.close()
# End of function handler


# Client Listening Socket
serverPort = 12012
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(10)


userPort = 12013
userInfo = []
userListLock = threading.Lock()
threadPool = Pool(10)

print('The server is ready!')
print("Current time is", datetime.now());


# Main Program Loop
while True:
    connectionSocket, addr = serverSocket.accept()
    threadPool.apply_async(handler,(connectionSocket, addr[0]))
