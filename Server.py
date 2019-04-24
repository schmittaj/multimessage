#####################################
# Server.py
#####################################
from socket import *
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

global userListLock
global userInfo


#####################################
# Function: loginProcessing
#####################################
def loginProcessing(request, connectionSocket, address):
    userid = request.split('\t')[1].strip()
    input = (userid, address)
    good = add_user_to_list(input)
    response = "LOGIN\t" + str(good)
    response = response.encode()
    connectionSocket.send(response)
    connectionSocket.close()
    return good
# End of function loginProcessing


#####################################
# Function: messageProcessing
#####################################
def messageProcessing(request,connectionSocket):
    sender = request.split("\t")[1]
    receiver = request.split("\t")[2]
    msg = request.split("\t")[3]
    outgoing = "MESSAGE\t" + sender + "\t" + receiver + "\t" + msg
    outgoing = outgoing.encode()
    addr = get_user_socket(receiver)
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((addr,12013))
    clientSocket.send(outgoing)
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
#####################################
def logoutProcessing(message,connectionSocket):
    userid = message.split('\t')[1].strip()
    success = remove_user_from_list(userid)
    response = "LOGOUT\t" + str(success)
    response = response.encode()
    connectionSocket.send(response)
    connectionSocket.close()
# End of function logoutProcessing


#####################################
# Function: add_user_to_list
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
#####################################
def get_user_socket(userName):
    userListLock.acquire()
    output = ()
    for a in range(0,len(userInfo)):
        if userInfo[a][0] == userName:
            output = userInfo[a][1]
    userListLock.release()
    return output
# End of function get_user_socket


#####################################
# Function: handler
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

userInfo = []
userListLock = threading.Lock()

#executor = ThreadPoolExecutor(max_workers=5)
print('The server is ready!')
print("Current time is", datetime.now());


# Main Program Loop
while True:
    connectionSocket, addr = serverSocket.accept()
    #fut = executor.submit(handler, (connectionSocket, addr))
    handThread = threading.Thread(target=handler, args=(connectionSocket, addr[0]))
    handThread.start()
