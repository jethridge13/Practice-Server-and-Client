from socket import *
serverName = "localhost"
serverPort = 9966
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
#Note: In Python 3, raw_input was renamed to input
while(True):
    sentence = input('Input: ')
    if(sentence == "END"):
        break
    elif(sentence == "EOM"):
        clientSocket.send("'\r\n\r\n'".encode("UTF-8"))
        rcv = clientSocket.recv(1024)
        print("Received: " + rcv.decode())
        continue
    #Note: strings need to be encoded to be sent
    # because, "str does not support the buffer interface"
    clientSocket.send(sentence.encode("UTF-8"))
clientSocket.close()
