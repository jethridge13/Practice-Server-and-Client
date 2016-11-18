# CSE 310 Project Group 11
# Rahul Verma
# Joshua Ethridge
# Harrison Termotto
#
# ERRORS:
# 0     Command not found
# 1     Login invalid

from socket import *
import threading
import shlex
import os
import signal
import sys

DEFAULT_PORT = 9966

EOM = "'\r\n\r\n'"

LOGIN_KEYWORD = "LOGIN"
AG_KEYWORD = "AG"
SG_KEYWORD = "SG"
RG_KEYWORD = "RG"
LOGOUT_KEYWORD = "LOGOUT"
ERROR_KEYWORD = "ERROR"
SD_KEYWORD = "SD"

LOGOUT_SND = " 'Logging you out from the server.' "
NOCMD_SND = " 0 'That is not a recognized command.' "

USER_FILE = "users.txt"

serverRunning = False

# ***Persistence functionality starts here***
if os.path.exists(USER_FILE):
    print("User file found! Loading users...")
    userFile = open(USER_FILE, "r")
else:
    print("User file not found. Creating user file.")
    userFile = open(USER_FILE, "w+")
users = []
usersLock = threading.Lock()
for i in userFile:
    userId = i.rstrip()
    users.append(userId)
userFile.close()

# ***Helper methods start here***

# This method removes a thread from the array of threads
def removeThread(threadID):
    arrayLock.acquire()
    for i in threads:
        if(threadID == i.threadID):
            threads.remove(i)
            break
    arrayLock.release()

# This is a method which will handle a client logging in to the server
def clientLogin(socket, identity, args):
    print("Login received from " + identity)
    if (args[1].isdigit()) and int(args[1]) == -1:
        print("Invalid login from " + identity)
        socket.send((ERROR_KEYWORD + " 1 'Login invalid' " + EOM).encode("UTF-8"))
        return
    userFound = False
    for i in users:
        if i == args[1]:
            userFound = True
    if not(userFound):
        usersLock.acquire()
        users.append(args[1])
        userFile = open(USER_FILE, "a")
        userFile.write(args[1])
        userFile.write("\n")
        userFile.close()
        usersLock.release()
        print("New user found. Added user " + str(args[1]))
    socket.send((LOGIN_KEYWORD + " '" + args[1] + "' " + EOM).encode("UTF-8"))
    print("Valid login from " + identity)


# This method safetly quits the server, closing all open files, threads, and such.
def quitServer():
    print("Quitting server!")
    for i in threads:
        print("Closing " + i.identity)
        i.socket.shutdown(SHUT_RDWR)
        i.socket.close()
    loginThread.serverSocket.close()
    sys.exit(0)

def signalHandler(signal, frame):
    print("TEST")


# ***This is the thread object***
# When Thread.start() is run, the run method will run. Upon return of the run method, the thread dies.
# This thread is to handle listening to the various clients
class ConnThread (threading.Thread):

    # This is the constructor for the thread.
    def __init__(self, threadID, socket, ip, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.socket = socket
        self.ip = ip
        self.port = port
        self.identity = "Thread" + str(self.threadID) + "@" + str(self.ip) + ":" + str(self.port)

    # This is what functionality the thread will perform while it's alive.
    def run(self):
        print("Running thread " + str(self.threadID) + " for " + str(self.ip) + ":" + str(self.port))
        keepRunning = True
        try:
            while(keepRunning):
                dataArgs = []

                # Receive data until an EOM is found
                while(shlex.split(EOM)[0] not in dataArgs):
                    dataRcv = self.socket.recv(1024)
                    dataRcv = dataRcv.decode()
                    #print(dataRcv)
                    #self.socket.send(str(self.threadID).encode("UTF-8"))
                    # Split the arguments, keeping quoted arguments together
                    data = shlex.split(dataRcv)
                    # Append the arguments to dataArgs
                    # This way, it will keep accepting arguments until an EOM is found
                    for i in data:
                        dataArgs.append(i)
                    #print(dataArgs)

                # EOM found, search for arguments
                if(dataArgs[0] == LOGIN_KEYWORD):
                    # Perform login operations
                    clientLogin(self.socket, self.identity, dataArgs)
                elif(dataArgs[0] == AG_KEYWORD):
                    # Perform ag operations
                    self.socket.send((AG_KEYWORD + " " + EOM).encode("UTF-8"))
                elif(dataArgs[0] == SG_KEYWORD):
                    # Perform sg operations
                    self.socket.send((SG_KEYWORD + " " + EOM).encode("UTF-8"))
                elif(dataArgs[0] == RG_KEYWORD):
                    # Perform rg operations
                    self.socket.send((RG_KEYWORD + " " + EOM).encode("UTF-8"))
                elif(dataArgs[0] == LOGOUT_KEYWORD):
                    # Perform logout operations
                    self.socket.send((LOGOUT_KEYWORD + LOGOUT_SND + EOM).encode("UTF-8"))
                    self.socket.close()
                    print("Client from " + self.identity + " has disconnected.")
                    keepRunning = False
                elif(dataArgs[0] == SD_KEYWORD):
                    # Perform shutdown operations
                    # This is mostly for testing
                    # If this stays in, it must be password protected
                    keepRunning = False
                    quitServer()
                else:
                    # Print non-recognized keyword
                    self.socket.send(ERROR_KEYWORD + NOCMD_SND + EOM)

        except (ConnectionAbortedError, ConnectionResetError):
            # If a client closes without using the logout functionality
            self.socket.close()
            print("Client from " + self.identity + " has disconnected unexpectedly.")

        # Client disconnected, remove thread from array of active threads
        print("Closing " + self.identity)
        removeThread(self.threadID)
    # End of run method, thread automatically ends


class LoginThread(threading.Thread):

    def __init__(self, serverSocket):
        threading.Thread.__init__(self)
        self.serverSocket = serverSocket

    def run(self):
        print("Login Thread running")
        freeThreadID = 0
        runServer = True
        # Functionality loop
        while runServer:
            try:
                self.serverSocket.listen(1)
                # Connection received from client
                clientSocket, addr = self.serverSocket.accept()
                print("Connection received from " + str(addr[0]) + ":" + str(addr[1]))
                thread = ConnThread(freeThreadID, clientSocket, addr[0], addr[1])
                freeThreadID+= 1

                # Add the thread to the list of threads
                arrayLock.acquire()
                threads.append(thread)
                arrayLock.release()

                # Start the thread
                thread.start()
            except OSError:
                print("The socket in the login thread has closed.")
                print("If this was triggered by something other than a server shutdown, a critical error has occured.")
                runServer = False


# ***Server startup begins here***

signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGBREAK, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)

# Prepare the socket
serverPort = DEFAULT_PORT
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))

# Array to hold all threads
threads = []
# Threads will increment by 1, starting at 0, avoiding duplicates
# Semaphore for concurrency stuff
arrayLock = threading.Lock()

# Waiting for connection...
print("Beginning server.")
print("Listening on port " + str(serverPort))

# Create a thread for logging in
loginThread = LoginThread(serverSocket)
loginThread.start()
# Wait for the login thread to end
loginThread.join()

