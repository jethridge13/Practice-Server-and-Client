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
SD_KEYWORD = "SD"

AG_DEFAULT = 5
SG_DEFAULT = 5
RG_DEFAULT = 5

loggedIn = False
userId = -1


def receiveData(socket):
    dataArgs = []
    while shlex.split(EOM)[0] not in dataArgs:
        dataRcv = socket.recv(1024)
        dataRcv = dataRcv.decode()
        data = shlex.split(dataRcv)
        # Append the arguments to dataArgs
        # This way, it will keep accepting arguments until an EOM is found
        for i in data:
            dataArgs.append(i)
    return dataArgs


def printHelp():
    print("Help - Supported Commands: ")
    print("login <#> - Takes one argument, your user ID. Will log you into the server to access the forum. You must "
          "login before you can access any of the other commands.")
    print("help - Displays this help menu.")
    print("ag [<#>] - Has one optional argument. Returns a list of all existing discussion groups, N groups at a time. "
          "If the argument is not provided, a default value of " + str(AG_DEFAULT) + " will be used. When in ag mode, "
          " the following subcommands are available.")
    print("\ts - Subscribe to groups. Takes between 1 and N arguments. Subscribes to all groups listed in the argument." )
    print("\tu - Unsubscribe to groups. Same functionality as s, but instead unsubscribes.")
    print("\tn - Lists the next N discussion groups. If there are no more to display, exits ag mode.")
    print("\tq - Exits from ag mode.")
    print("sg [<#>] - Has one optional argument. Returns a list of all subscribed groups, N groups at a time. If the "
          "argument is not provided, then a default value of " + str(SG_DEFAULT) + " will be used.")
    print("rg <gname> [<#>] - Takes one mandatory argument and one optional argument. It displays the top N posts in a "
          "given discussion group. The argument, 'gname' determines which group to display. If the optional argument is"
          " not provided, then a default value of " + str(RG_DEFAULT) + " will be used. After entering this command, the "
          "application will enter 'rg' mode, which uses the following subcommands.")
    print("\t[#] - The post number to display. Entering this mode will give even more subcommands.")
    print("\t\tn - Display, at most, n more lines of content.")
    print("\t\tq - Quit this read mode to return to normal rg mode")
    print("\tr [#] - Marks the given post as read. If a single number is specified, then that single post will be marked"
          " as read. You can use the format, 'n-m' to mark posts n through m as read.")
    print("\tn - Lists the next n posts. If there are no more posts to display, exits rg mode.")
    print("\tp - Post to the group. This subcommand will enter post mode.")
    print("\t\tThe application will request a title for the post. Then, the application will allow you to write the "
          "body of the post. It will accept input until you enter a blank line, followed by a period, followed by "
          "another blank line. After this command sequence is accepted, the post will be submitted and you will be "
          "returned to rg mode.")
    print("logout - Logs you out from the server, subsequently closing the application.")


#TODO Once subscription is implemented, update this to work
def subscribe(groups):
    for i in groups:
        print("Subscribed to " + str(i))


#TODO Once subscription is implemented, update this to work
def unsub(groups):
    for i in groups:
        print("Unsubscribed to " + str(i))


# This function handles the implementation of the ag command. It uses the submethods subscribe() and unsubscribe()
def ag(n):
    clientSocket.send((AG_KEYWORD + " " + EOM).encode("UTF-8"))
    dataArgs = receiveData(clientSocket)
    groupsLeft = 0
    currentMaxGroup = 2
    if dataArgs[0] == AG_KEYWORD:
        groupsLeft = int(dataArgs[1])
        while(groupsLeft > 0):
            for i in range(currentMaxGroup, currentMaxGroup + n):
                print(str(i - 1) + ". " + dataArgs[i])
            currentMaxGroup = currentMaxGroup + n
            groupsLeft = groupsLeft - n
            nextSequence = False
            while(not nextSequence):
                stdin = input(str(userId) + "(AG Mode)>>> ")
                userInput = shlex.split(stdin)
                if userInput[0] == "s":
                    # Subscribe to group
                    groupsToSub = userInput[1:]
                    subscribe(groupsToSub)
                elif userInput[0] == "u":
                    # Unsubscribe to group
                    groupsToUnsub = userInput[1:]
                    unsub(groupsToUnsub)
                elif userInput[0] == "n":
                    nextSequence = True
                elif userInput[0] == "q":
                    groupsLeft = 0
                    nextSequence = True
    print("Exiting AG Mode")



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
while keepRunning:
    if loggedIn:
        stdin = input(str(userId) + ">>> ")
    else:
        stdin = input('>>> ')
    userInput = shlex.split(stdin)
    if not loggedIn:
        if userInput[0] == "login":
            # Login operations
            if not loggedIn:
                # Login requires exactly 2 arguments
                if len(userInput) != 2:
                    print("Incorrect number of arguments.")
                    printHelp()
                else:
                    print(userInput[1])
                    clientSocket.send((LOGIN_KEYWORD + " '" + userInput[1] + "' " + EOM).encode("UTF-8"))

                    # Receive data until EOM found
                    dataArgs = receiveData(clientSocket)

                    if dataArgs[0] == LOGIN_KEYWORD :
                        print("Login successful! Welcome user " + str(dataArgs[1]))
                        loggedIn = True
                        userId = dataArgs[1]
        elif userInput[0] == "help":
            printHelp()
        else:
            print("Please login before issuing commands.")
            printHelp()
    else:
        if userInput[0] == "login":
            print("You are already logged in.")
            printHelp()
        elif userInput[0] == "help":
            printHelp()
        elif userInput[0] == "ag":
            #TODO Add in the optional argument functionality
            if len(userInput) == 2 and userInput[1].isdigit() and int(userInput[1]) > 0:
                ag(int(userInput[1]))
            elif len(userInput) == 1:
                ag(AG_DEFAULT)
            else:
                print("Incorrect usage for ag.")
                printHelp()
        elif userInput[0] == "logout":
            print("Logging out from the server...")
            clientSocket.send((LOGOUT_KEYWORD + " " + EOM).encode("UTF-8"))
            dataArgs = receiveData(clientSocket)
            if(dataArgs[0] == LOGOUT_KEYWORD):
                print("Received from server: " + dataArgs[1])
            keepRunning = False
            break
        elif userInput[0] == "EOM":
            clientSocket.send("'\r\n\r\n'".encode("UTF-8"))
            rcv = clientSocket.recv(1024)
            print("Received: " + rcv.decode())
            continue
        elif userInput[0] == "sd":
            clientSocket.send((SD_KEYWORD + " " + EOM).encode("UTF-8"))

if loggedIn:
    clientSocket.close()
