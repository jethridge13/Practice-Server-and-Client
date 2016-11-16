# CSE 310 Project Group 11
# Rahul Verma
# Joshua Ethridge
# Harrison Termotto

from socket import *
import threading

def removeThread(threadID):
    arrayLock.acquire()
    for i in threads:
        if(threadID == i.threadID):
            threads.remove(i)
            break
    arrayLock.release()

class ConnThread (threading.Thread):

    # This is the constructor for the thread.
    def __init__(self, threadID, socket, ip, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.socket = socket
        self.ip = ip
        self.port = port

    # This is what functionality the thread will perform while it's alive.
    def run(self):
        print("Running thread " + str(self.threadID) + " for " + str(self.ip) + ":" + str(self.port))
        keepRunning = True
        try:
            while(keepRunning):
                dataRcv = self.socket.recv(1024)
                #print(dataRcv)
                self.socket.send(str(self.threadID).encode("UTF-8"))
        except (ConnectionAbortedError, ConnectionResetError):
            print("Client from Thread" + str(self.threadID) + "@" + str(self.ip) + ":" + str(self.port) + " has disconnected.")
        removeThread(self.threadID)
    # End of run method, thread automatically ends



# Server startup begins here

DEFAULT_PORT = 9966

# Prepare the socket
serverPort = DEFAULT_PORT
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))

# Array to hold all threads
threads = []
# Threads will increment by 1, starting at 0, avoiding duplicates
freeThreadID = 0
# Semaphore for concurrency stuff
arrayLock = threading.Lock()

# Waiting for connection...
runServer = True
print("Beginning server.")
print("Listening on port " + str(serverPort))
while runServer:
    serverSocket.listen(1)

    # Connection received from client
    clientSocket, addr = serverSocket.accept()
    print("Connection received from " + str(addr[0]) + ":" + str(addr[1]))
    thread = ConnThread(freeThreadID, clientSocket, addr[0], addr[1])
    freeThreadID+= 1

    # Add the thread to the list of threads
    arrayLock.acquire()
    threads.append(thread)
    arrayLock.release()

    # Start the thread
    thread.start()
