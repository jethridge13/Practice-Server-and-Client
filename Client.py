# CSE 310 Project Group 11
# Rahul Verma
# Joshua Ethridge
# Harrison Termotto

from socket import *
import sys
import shlex

EOM = "'\r\n\r\n'"
LOGIN_KEYWORD = "LOGIN"
AG_KEYWORD = "AG"
SG_KEYWORD = "SG"
RG_KEYWORD = "RG"
LOGOUT_KEYWORD = "LOGOUT"

loggedIn = False
userId = -1

def printHelp():
    print("Help")

# Get system arguments to determine address and port
try:
    argv = sys.argv
    host = argv[1]
    port = argv[2]
    port = int(port)
except IndexError:
    print("Too few arguments given.")
    sys.exit()

# Attempt to connect to given address
clientSocket = socket(AF_INET, SOCK_STREAM)
print("Attempting to connect to " + str(host) + ":" + str(port))
clientSocket.connect((host, port))

keepRunning = True
print("Connection successful!")
while(keepRunning):
    stdin = input('>>> ')
    userInput = shlex.split(stdin)
    if(userInput[0] == "login"):
        # Login operations
        # Login requires exactly 2 arguments
        if(len(userInput) != 2):
            print("Incorrect number of arguments.")
            printHelp()
        else:
            clientSocket.send((LOGIN_KEYWORD + " " + userInput[1] + " " + EOM).encode("UTF-8"))

            # Receive data until EOM found
            dataArgs = []
            while(shlex.split(EOM)[0] not in dataArgs):
                    dataRcv = clientSocket.recv(1024)
                    dataRcv = dataRcv.decode()
                    data = shlex.split(dataRcv)
                    # Append the arguments to dataArgs
                    # This way, it will keep accepting arguments until an EOM is found
                    for i in data:
                        dataArgs.append(i)

            if(dataArgs[0] == LOGIN_KEYWORD):
                print("Login successful! Welcome user " + str(dataArgs[1]))
                loggedIn = True
                userId = int(dataArgs[1])
    elif(userInput[0] == "logout"):
        print("Logging out from the server...")
        keepRunning = False
        break
    elif(userInput[0] == "EOM"):
        clientSocket.send("'\r\n\r\n'".encode("UTF-8"))
        rcv = clientSocket.recv(1024)
        print("Received: " + rcv.decode())
        continue

clientSocket.close()