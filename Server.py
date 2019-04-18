#********************************************
# Server.py
#*********************************************
from socket import *
from datetime import datetime
import _thread


#************************************
# Function: loginProcessing
#************************************
def loginProcessing(request, connectionSocket):
    loginStatus = "Failure" # A client was not logged in when just connected
    #Strip information and print in line for debugging
    userid = request.split('\t')[1].strip()

    print('userID:  '+userid)
    USERIDSTATUS = "GOOD"
    response = "USERIDSTATUS: " + USERIDSTATUS
    response = response.encode()
    connectionSocket.send(response)
    output_file = open("Log.txt", "a")
    output_file.write(datetime.now().strftime("%H:%M:%S %B %d, %Y"))
    output_file.write("\t" + "Login Success" + "\t" + userid + "\n")
    output_file.close()
    return(True)

# End of function loginProcessing


#************************************
# Function: messageProcessing
#************************************
def messageProcessing(request,connectionSocket):
    print("processing Message")
    msg = request.split("\t")[1]
    msg = msg.encode()
    connectionSocket.send(msg)
# End of function messageProcessing


#************************************
# Function: handler
#************************************
def handler(connectionSocket):
    close = False
    while not close:
        print("waiting on client")
        message = connectionSocket.recv(4096)
        message = message.decode()
        request = message.split("\t")[0]
        print("Request message:", request)
        if(request.upper() == "QUIT"):
            close = True
        else:
            #Parse the method name from the request message
            methodName = request.split('\t')[0].strip()
            print("From", addr,methodName)

            if(methodName.upper() == "LOGIN"):
                loginProcessing(message, connectionSocket)
            elif(methodName.upper() == "MESSAGE"):
                messageProcessing(message,connectionSocket)
            else:
                print("Something went wrong")

    connectionSocket.close()
# End of function handler


# Client Listening Socket
serverPort = 12012
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(10)
print ('The server is ready!')
print("Current time is", datetime.now());


# Main Program Loop
while 1:
    connectionSocket, addr = serverSocket.accept()
    print("Connected")
    _thread.start_new_thread(handler, (connectionSocket,))


