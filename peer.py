import json
import signal
import sys
from socket import *
import threading
import time
import select
from utils.message_formatter import *
from config.app_config import AppConfig
from config.logger_config import LoggerConfig
from colorama import Fore, Style
from utils.message_formatter import *
import logging
terminalLogFlag = False
logger = LoggerConfig("peer", level=logging.INFO, log_path='./logs/src', enable_console=terminalLogFlag).get_logger()

conf = AppConfig();
# Server side of peer
class PeerServer(threading.Thread):


    # Peer server initialization
    def __init__(self, username, peerServerPort, roomServerPort):

        threading.Thread.__init__(self)
        # keeps the username of the peer
        self.username = username
        # tcp socket for peer server
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        self.udpServerSocket = socket(AF_INET, SOCK_DGRAM)
        # port number of the peer server
        self.peerServerPort = peerServerPort
        self.roomServerPort = roomServerPort
        # if 1, then user is already chatting with someone
        # if 0, then user is not chatting with anyone
        self.isChatRequested = 0
        # keeps the socket for the peer that is connected to this peer
        self.connectedPeerSocket = None
        # keeps the ip of the peer that is connected to this peer's server
        self.connectedPeerIP = None
        # keeps the port number of the peer that is connected to this peer's server
        self.connectedPeerPort = None
        # online status of the peer
        self.isOnline = True
        # keeps the username of the peer that this peer is chatting with
        self.chattingClientName = None
        self.chat = 0
        self.room = 0   

    # main method of the peer server thread
    def run(self):
        print("Peer server started...")    

        # gets the ip address of this peer
        # first checks to get it for windows devices
        # if the device that runs this application is not windows
        # it checks to get it for macos devices
        try:
            self.peerServerHostname=conf.hostname
        except Exception as e:
            print(e)





        self.udpServerSocket.bind((self.peerServerHostname, self.roomServerPort))

        #socket initialization for chatting
        self.tcpServerSocket.bind((self.peerServerHostname, self.peerServerPort))
        self.tcpServerSocket.listen(4)
            
            

        # inputs sockets that should be listened
        inputs = [self.udpServerSocket, self.tcpServerSocket]
        # server listens as long as there is a socket to listen in the inputs list and the user is online
        while inputs and self.isOnline:
            # monitors for the incoming connections
            try:
                readable, writable, exceptional = select.select(inputs, [], [])
                # If a server waits to be connected enters here
                for s in readable:
                    # if the socket that is receiving the connection is 
                    # the tcp socket of the peer's server, enters here
                    if s is self.tcpServerSocket and self.room == 0:
                        # accepts the connection, and adds its connection socket to the inputs list
                        # so that we can monitor that socket as well
                        connected, addr = s.accept()
                        connected.setblocking(0)
                        inputs.append(connected)
                        # if the user is not chatting, then the ip and the socket of
                        # this peer is assigned to server variables
                        if self.isChatRequested == 0:     
                            print(self.username + " is connected from " + str(addr))
                            self.connectedPeerSocket = connected
                            self.connectedPeerIP = addr[0]
                    # Here we handle messages from rooms
                    elif s is self.udpServerSocket and self.room == 1:
                        #socket initializatoion for rooms
                        #self.udpServerSocket.bind((self.peerServerHostname, self.peerServerPort))
                        while(1):
                            data, address = self.udpServerSocket.recvfrom(1024)
                            messageReceived = data.decode()
                            print(messageReceived)
                            if(self.room == 0):
                                break
                    # if the socket that receives the data is the one that
                    # is used to communicate with a connected peer, then enters here
                    elif self.room == 0:
                        # message is received from connected peer
                        messageReceived = s.recv(1024).decode()
                        # logs the received message
                        logger.info("Received from " + str(self.connectedPeerIP) + " -> " + str(messageReceived))
                        # if message is a request message it means that this is the receiver side peer server
                        # so evaluate the chat request
                        if len(messageReceived) > 11 and messageReceived[:12] == "CHAT-REQUEST" and self.room == 0:
                            # text for proper input choices is printed however OK or REJECT is taken as input in main process of the peer
                            # if the socket that we received the data belongs to the peer that we are chatting with,
                            # enters here
                            if s is self.connectedPeerSocket:
                                # parses the message
                                messageReceived = messageReceived.split()
                                # gets the port of the peer that sends the chat request message
                                self.connectedPeerPort = int(messageReceived[1])
                                # gets the username of the peer sends the chat request message
                                self.chattingClientName = messageReceived[2]
                                # prints prompt for the incoming chat request
                                print("Incoming chat request from " + self.chattingClientName + " >> ")
                                print("Enter OK to accept or REJECT to reject:  ")
                                # makes isChatRequested = 1 which means that peer is chatting with someone
                                self.isChatRequested = 1
                            # if the socket that we received the data does not belong to the peer that we are chatting with
                            # and if the user is already chatting with someone else(isChatRequested = 1), then enters here
                            elif s is not self.connectedPeerSocket and self.isChatRequested == 1:
                                # sends a busy message to the peer that sends a chat request when this peer is 
                                # already chatting with someone else
                                message = "BUSY"
                                s.send(message.encode())
                                # remove the peer from the inputs list so that it will not monitor this socket
                                inputs.remove(s)
                        # if an OK message is received then ischatrequested is made 1 and then next messages will be shown to the peer of this server
                        elif messageReceived == "OK":
                            self.isChatRequested = 1
                        # if an REJECT message is received then ischatrequested is made 0 so that it can receive any other chat requests
                        elif messageReceived == "REJECT":
                            self.isChatRequested = 0
                            inputs.remove(s)
                        # if a message is received, and if this is not a quit message ':q' and 
                        # if it is not an empty message, show this message to the user
                        elif messageReceived[:2] != ":q" and len(messageReceived)!= 0:
                           message_after_format =  display_message(self.chattingClientName, messageReceived, True)
                           print(message_after_format)
                        # if the message received is a quit message ':q',
                        # makes ischatrequested 1 to receive new incoming request messages
                        # removes the socket of the connected peer from the inputs list
                        elif messageReceived[:2] == ":q":
                            if(self.room == 1):
                                self.room = 0
                                #leave_room()
                            else:    
                                self.isChatRequested = 0
                                inputs.clear()
                                inputs.append(self.tcpServerSocket)
                                # connected peer ended the chat
                                if len(messageReceived) == 2:
                                    print("User you're chatting with ended the chat")
                                    print("Press enter to quit the chat: ")
                        # if the message is an empty one, then it means that the
                        # connected user suddenly ended the chat(an error occurred)
                        elif len(messageReceived) == 0:    
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            print("User you're chatting with suddenly ended the chat")
                            print("Press enter to quit the chat: ")

            # handles the exceptions, and logs them
            except OSError as oErr:
                logger.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logger.error("ValueError: {0}".format(vErr))

# Client side of peer
class PeerClient(threading.Thread):
    # variable initializations for the client side of the peer
    def __init__(self, ipToConnect, portToConnect, username, peerServer, responseReceived, flag, room_id ,room_peers : list, registry_name = conf.hostname):
        threading.Thread.__init__(self)
        # keeps the ip address of the peer that this will connect
        # ip address of the registry
        self.registryName = registry_name
        #self.registryName = 'localhost'
        # port number of the registry
        self.registryPort = conf.port_tcp

        self.ipToConnect = ipToConnect
        # keeps the username of the peer
        self.username = username
        # keeps the port number that this client should connect
        self.portToConnect = portToConnect
        # client side tcp socket initialization
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        self.tcpClientSocket.bind((conf.hostname,0))
        self.udpClientSocket.bind((conf.hostname,0))

        # keeps the server of this client
        self.peerServer = peerServer
        # keeps the phrase that is used when creating the client
        # if the client is created with a phrase, it means this one received the request
        # this phrase should be none if this is the client of the requester peer
        self.responseReceived = responseReceived
        # keeps if this client is ending the chat or not
        self.isEndingChat = False
        #flag to indicate room or normal chat
        self.flag = flag
        #RoomID
        self.room_id = room_id
        #list of room_peers
        self.room_peers = room_peers
        self.isRoomEmpty = False

    def update_peers(self):
        message = "UPDATE " + str(self.room_id)
        self.tcpClientSocket.send(message.encode())
        logger.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        response = self.tcpClientSocket.recv(1024).decode()
        list_start = response.index('[')
        list_end = response.index(']') + 1
        list_string = response[list_start:list_end]
        response = response.split()
        response2 = eval(list_string)
        self.room_peers = response2

    def exit(self):
        #Need to access peerServerObject to get roomPortNo to remove from list
        port_to_remove = self.peerServer.roomServerPort
        #Then go to registry and remove him
        request = "EXIT " + str(self.room_id) + " " + str(port_to_remove)
        self.tcpClientSocket.send(request.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        #Display Message ("USERNAME Disconected")
        return response

    # main method of the peer client thread
    def run(self):
        if self.flag == '6':
            print("Peer client started...")
            # connects to the server of other peer
            print("Connecting to " + self.ipToConnect + ":" + str(self.portToConnect) + "...")
            self.ipToConnect = conf.hostname
            self.tcpClientSocket.connect((self.ipToConnect, self.portToConnect))
            # if the server of this peer is not connected by someone else and if this is the requester side peer client then enters here
            if self.peerServer.isChatRequested == 0 and self.responseReceived is None:
                # composes a request message and this is sent to server and then this waits a response message from the server this client connects
                requestMessage = "CHAT-REQUEST " + str(self.peerServer.peerServerPort)+ " " + self.username
                # logs the chat request sent to other peer
                logger.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + requestMessage)
                # sends the chat request
                self.tcpClientSocket.send(requestMessage.encode())
                print("Request message " + requestMessage + " is sent...")
                # received a response from the peer which the request message is sent to
                self.responseReceived = self.tcpClientSocket.recv(1024).decode()
                # logs the received message
                logger.info("Received from " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + self.responseReceived)
                print("Response is " + self.responseReceived)
                # parses the response for the chat request
                self.responseReceived = self.responseReceived.split()
                # if response is ok then incoming messages will be evaluated as client messages and will be sent to the connected server
                if self.responseReceived[0] == "OK":
                    # changes the status of this client's server to chatting
                    self.peerServer.isChatRequested = 1
                    # sets the server variable with the username of the peer that this one is chatting
                    self.peerServer.chattingClientName = self.responseReceived[1]
                    # as long as the server status is chatting, this client can send messages
                    while self.peerServer.isChatRequested == 1:
                        # message input prompt
                        messageSent = input()
                        # sends the message to the connected peer, and logs it
                        self.tcpClientSocket.send(messageSent.encode())
                        logger.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                        # if the quit message is sent, then the server status is changed to not chatting
                        # and this is the side that is ending the chat
                        if messageSent == ":q":
                            self.peerServer.isChatRequested = 0
                            self.isEndingChat = True
                            break
                    # if peer is not chatting, checks if this is not the ending side
                    if self.peerServer.isChatRequested == 0:
                        if not self.isEndingChat:
                            # tries to send a quit message to the connected peer
                            # logs the message and handles the exception
                            try:
                                self.tcpClientSocket.send(":q ending-side".encode())
                                logger.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> :q")
                            except BrokenPipeError as bpErr:
                                logger.error("BrokenPipeError: {0}".format(bpErr))
                        # closes the socket
                        self.responseReceived = None
                        self.tcpClientSocket.close()
                # if the request is rejected, then changes the server status, sends a reject message to the connected peer's server
                # logs the message and then the socket is closed       
                elif self.responseReceived[0] == "REJECT":
                    self.peerServer.isChatRequested = 0
                    print("client of requester is closing...")
                    self.tcpClientSocket.send("REJECT".encode())
                    logger.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> REJECT")
                    self.tcpClientSocket.close()
                # if a busy response is received, closes the socket
                elif self.responseReceived[0] == "BUSY":
                    print("Receiver peer is busy")
                    self.tcpClientSocket.close()
            # if the client is created with OK message it means that this is the client of receiver side peer
            # so it sends an OK message to the requesting side peer server that it connects and then waits for the user inputs.
            elif self.responseReceived == "OK":
                # server status is changed
                self.peerServer.isChatRequested = 1
                # ok response is sent to the requester side
                okMessage = "OK"
                self.tcpClientSocket.send(okMessage.encode())
                logger.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + okMessage)
                print("Client with OK message is created... and sending messages")
                # client can send messsages as long as the server status is chatting
                while self.peerServer.isChatRequested == 1:
                    # input prompt for user to enter message
                    messageSent = input()
                    self.tcpClientSocket.send(messageSent.encode())
                    logger.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                    # if a quit message is sent, server status is changed
                    if messageSent == ":q":
                        self.peerServer.isChatRequested = 0
                        self.isEndingChat = True
                        break
                # if server is not chatting, and if this is not the ending side
                # sends a quitting message to the server of the other peer
                # then closes the socket
                if self.peerServer.isChatRequested == 0:
                    if not self.isEndingChat:
                        self.tcpClientSocket.send(":q ending-side".encode())
                        logger.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> :q")
                    self.responseReceived = None
                    self.tcpClientSocket.close()


        elif self.flag == '8':

            self.tcpClientSocket.connect((self.registryName, self.registryPort))

            print("You Joined Room Successfully ...")

            self.update_peers()
            message = f"Joined the Room "
            for peer in self.room_peers:
                if int(peer) != self.peerServer.roomServerPort:
                    formatted_message = display_message(self.username, message, True)
                    self.udpClientSocket.sendto(formatted_message.encode(), (self.ipToConnect, int(peer)))


            while True :
                self.update_peers()

                if (not self.room_peers):
                    break

                message = input()

                message = f"{message}"

                self.update_peers()

                if (len(message) != 0 and message.split()[1] == ":q"):

                    if self.exit() == "SUCCESS":

                        message = f"{self.username} Disconnected !"

                        for peer in self.room_peers:
                            self.udpClientSocket.sendto(message.encode(), (self.ipToConnect, int(peer)))
                        break
                else:
                    for peer in self.room_peers:

                        if int(peer) != self.peerServer.roomServerPort:
                            formatted_message = display_message(self.username, message, True)
                            self.udpClientSocket.sendto(formatted_message.encode(), (self.ipToConnect, int(peer)))

                        # self.tcpClientSocket.connect((self.ipToConnect, int(peer)))

                        # self.tcpClientSocket.send(message.encode())

                        # self.tcpClientSocket.close()

            print("Chat Ended!")

            self.flag = None


# main process of the peer
class peerMain:

    # peer initializations
    def __init__(self):
        # ip address of the registry
        #self.registryName = input("Enter IP address of registry: ")
        self.registryName = conf.hostname
        # port number of the registry
        self.registryPort = conf.port_tcp
        # tcp socket connection to registry
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.bind((conf.hostname,0))
        self.tcpClientSocket.connect((self.registryName,self.registryPort))
        # initializes udp socket which is used to send hello messages
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # udp port of the registry
        self.registryUDPPort = conf.port_udp
        # login info of the peer
        self.loginCredentials = (None, None)
        # online status of the peer
        self.isOnline = False
        # server port number of this peer
        self.peerServerPort = None
        #server port for rooms
        self.roomServerPort = None
        # server of this peer
        self.peerServer = None
        # client of this peer
        self.peerClient = None
        # timer initialization
        self.timer = None
        
        choice = "0"
        # as long as the user is not logged out, asks to select an option in the menu
        while choice != "3":
            # menu selection prompt
            not_allowed_message = None
            choice = input("Choose: \nCreate account: 1\nLogin: 2\nLogout: 3\nSearch: 4\nShow Online Useres: 5\nStart a chat: 6\nCreate Chatroom: 7\nJoin a room: 8\n")
            # if choice is 1, creates an account with the username
            # and password entered by the user
            if choice == "1":
                username = input("username: ")
                password = input("password: ")
                
                self.createAccount(username, password)

            # if choice is 2 and user is not logged in, asks for the username
            # and the password to login
            elif choice == "2":
               if self.isOnline:
                   print("You are already logged In")
               else:
                   username = input("username: ")
                   password = input("password: ")
                   # asks for the port number for server's tcp socket

                   #peerServerPort = int(input("Enter Peer port "))
                   #roomServerPort = int(input("Enter Room port "))
                   peerServerPort = conf.get_random_port()
                   roomServerPort = conf.get_random_port()

                   status = self.login(username, password, peerServerPort)
                   # is user logs in successfully, peer variables are set
                   if status == 1:
                       self.isOnline = True
                       self.loginCredentials = (username, password)
                       self.peerServerPort = peerServerPort
                       self.roomServerPort = roomServerPort
                       # creates the server thread for this peer, and runs it
                       self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort, self.roomServerPort)
                       self.peerServer.start()
                       # hello message is sent to registry
                       self.sendHelloMessage()


            # if choice is 3 and user is logged in, then user is logged out
            # and peer variables are set, and server and client sockets are closed
            elif choice == "3":
                if self.isOnline:
                    self.logout(1)
                    self.isOnline = False
                    self.loginCredentials = (None, None)
                    self.peerServer.isOnline = False
                    self.peerServer.tcpServerSocket.close()
                    if self.peerClient is not None:
                        self.peerClient.tcpClientSocket.close()
                    print("Logged out successfully")
                else:
                    choice = input("You are not logged in, In the firt place do you want to exit ? Yes or No : ")
                    if (choice == "Yes" or choice == "Y" or choice == "y" or choice == "yes"):
                        self.logout("exit")
                        print("Terminated The Program Successfully")
                    else:
                        choice = "other"

            # if choice is 4 and user is online, then user is asked
            # for a username that is wanted to be searched
            elif choice == "4":
               if self.isOnline:
                   username = input("Username to be searched: ")
                   searchStatus = self.searchUser(username)
                   # if user is found its ip address is shown to user
                   if searchStatus != None and searchStatus != 0:
                       print("IP address of " + username + " is " + searchStatus)
               else:
                   print("You must log in to be able search for users")


            # if choice is 5 and user is online, then user is asked
            # to enter the username of the user that is wanted to be chatted
            elif choice == "5":
                if self.isOnline:
                    self.showOnlineUsers()
                else:
                    print("You need to log in to be able to see online peers")

            elif choice == "6":
                if self.isOnline:
                    username = input("Enter the username of user to start chat: ")
                    searchStatus = self.searchUser(username)
                    # if searched user is found, then its ip address and port number is retrieved
                    # and a client thread is created
                    # main process waits for the client thread to finish its chat
                    if searchStatus != None and searchStatus != 0:
                        searchStatus = searchStatus.split(":")
                        self.peerServer.chat = 1
                        self.peerClient = PeerClient(ipToConnect=searchStatus[0], portToConnect=int(searchStatus[1]),
                                                     username=self.loginCredentials[0], peerServer=self.peerServer,
                                                     responseReceived=None, flag='6', room_id=None, room_peers=None)
                        # starting a thread for the current peer client
                        self.peerClient.start()
                        # join will wait for the previous start thread to finish
                        self.peerClient.join()
                else:
                    print("You must be logged In to be able to start a chat")

            # if this is the receiver side then it will get the prompt to accept an incoming request during the main loop
            # that's why response is evaluated in main process not the server thread even though the prompt is printed by server
            # if the response is ok then a client is created for this peer with the OK message and that's why it will directly
            # sent an OK message to the requesting side peer server and waits for the user input
            # main process waits for the client thread to finish its chat

            elif choice == "7":
                if self.isOnline:
                    # This choice creates a new chatroom and saves it in the database
                    room_id = input("Enter a Room ID: ")
                    self.create_room(room_id)
                    print("Room Created Successfully\n")
                else:
                    print("You need to be logged in to be able to create your room !!")


            elif choice == "8":
                if self.isOnline:
                    # This choice joins already existing chatroom
                    room_id = input("Enter a Room ID: ")
                    search_status = self.search_room(room_id)

                    if search_status != 0 and search_status != None:
                        # def __init__(self, ipToConnect, portToConnect, username, peerServer, responseReceived, flag, room_peers : list)
                        ipToConnect = self.registryName
                        self.peerServer.room = 1
                        self.peerClient = PeerClient(ipToConnect, None, self.loginCredentials[0], self.peerServer, None,
                                                     '8', room_id, search_status)
                        self.peerClient.start()
                        self.peerClient.join()
                else:
                    print("You should be logged in to be able to join a room");


            elif choice == "OK" or choice == "ok" or choice == "Ok" :
                if self.isOnline:
                    okMessage = "OK " + self.loginCredentials[0]
                    logger.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)
                    self.peerServer.connectedPeerSocket.send(okMessage.encode())
                    self.peerClient = PeerClient(self.peerServer.connectedPeerIP, self.peerServer.connectedPeerPort,
                                                 self.loginCredentials[0], self.peerServer, "OK", '6', None, None)
                    self.peerClient.start()
                    self.peerClient.join()
                else:
                    print("Something went wrong you are probabliy not online right now")
            # if user rejects the chat request then reject message is sent to the requester side

            elif choice == "REJECT" or choice == "Reject" or choice =="reject":
                if self.isOnline:
                    self.peerServer.connectedPeerSocket.send("REJECT".encode())
                    self.peerServer.isChatRequested = 0
                    logger.info("Send to " + self.peerServer.connectedPeerIP + " -> REJECT")
                else:
                    print("Something went wrong you are probabliy not online right now")

            # if choice is cancel timer for hello message is cancelled
            elif choice == "CANCEL" or choice == "Cancel" or choice == "cancel":
                print("Closing the connectoin Correctly")
                self.timer.cancel()
                break

        # if main process is not ended with cancel selection
        # probabliy something went wrong we need to handle it here and close manually
        # socket of the client is closed
        if choice != "CANCEL" or choice != "cancel" or choice != "Cancel":
            print("Closing the connection manually the choice selection didn't end up with cancel command !!")
            self.tcpClientSocket.close()


    def create_room(self, room_id):
        # join message to create an account is composed and sent to registry
        # if response is success then informs the user for account creation
        # if response is exist then informs the user for account existence
        message = "CREATE " + room_id
        logger.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logger.info("Received from " + self.registryName + " -> " + response)
        if response == "creation-success":
            print("Room created...")
        elif response == "room_exist":
            print("Room already exits")

    # function for searching an online user
     # function for searching an online user
    def search_room(self, room_id):
        # a search message is composed and sent to registry
        # custom value is returned according to each response
        # to this search message
        message = "JOINROOM " + room_id + " " + str(self.roomServerPort)
        logger.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()

        # for example "success ['4001', '8001', '3001', '5001']"
        # list start = 8 which is the index of [
        # list end =  40 which is the index of ]
        # list string is extracted using the start and ending list !!!
        list_start = response.index('[')
        list_end = response.index(']') + 1
        list_string = response[list_start:list_end]
        # converts the extracted String to an actual python list
        response2 = eval(list_string)

        response = response.split()
        logger.info("Received from " + self.registryName + " -> " + " ".join(response))
        if response[0] == "success":
            print(room_id + " is found successfully...")
            return response2
        
        elif response[0] == "search-fail":
            print(room_id + " is not found")
            return 0

    # def join_room(self, search_status, port_no):
    #     if search_status == 0:
    #         print("Room Not Found!")
    #     else:
    #         message = "JOINROOM " + search_status + " " + port_no
    #         logger.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
    #         self.tcpClientSocket.send(message.encode())
    #         response = self.tcpClientSocket.recv(1024).decode()
    #         if response == 'success':
    #             print("Joined Room Successfully")



    
    
    # account creation function
    def createAccount(self, username, password):
        # join message to create an account is composed and sent to registry
        # if response is success then informs the user for account creation
        # if response is exist then informs the user for account existence
        message = "JOIN " + username + " " + password
        logger.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logger.info("Received from " + self.registryName + " -> " + response)
        if response == "join-success":
            print("Account created...")
        elif response == "join-exist":
            print("choose another username or login...")

    # login function
    def login(self, username, password, peerServerPort):
        # a login message is composed and sent to registry
        # an integer is returned according to each response
        message = "LOGIN " + username + " " + password + " " + str(peerServerPort)
        logger.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logger.info("Received from " + self.registryName + " -> " + response)
        if response == "login-success":
            print("Logged in successfully...")
            return 1
        elif response == "login-account-not-exist":
            print("Account does not exist...")
            return 0
        elif response == "login-online":
            print("Account is already online...")
            return -1
        elif response == "login-wrong-password":
            print("Wrong password...")
            return 3
    
    # logout function
    def logout(self, option):
        # a logout message is composed and sent to registry
        # timer is stopped

        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]
            self.timer.cancel()
        elif option == "exit":
            print("Successfully terminated the program")
            exit()
        else:
            message = "LOGOUT"
        logger.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        

    # function for searching an online user
    def searchUser(self, username):
        # a search message is composed and sent to registry
        # custom value is returned according to each response
        # to this search message
        message = "SEARCH " + username
        logger.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        logger.info("Received from " + self.registryName + " -> " + " ".join(response))
        if response[0] == "search-success":
            print(username + " is found successfully...")
            return response[1]
        elif response[0] == "search-user-not-online":
            print(username + " is not online...")
            return 0
        elif response[0] == "search-user-not-found":
            print(username + " is not found")
            return None


    def showOnlineUsers(self):
        # a search message is composed and sent to registry
        # custom value is returned according to each response
        # to this search message
        message = "ONLINE_USERS"
        logger.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        received_data = self.tcpClientSocket.recv(4096).decode()
        # Deserialize the JSON data back into a Python object (list of online users)
        received_online_users = json.loads(received_data)


        # ... (existing code)

        received_data = self.tcpClientSocket.recv(4096).decode()
        # Deserialize the JSON data back into a Python object (list of online users)
        received_online_users = json.loads(received_data)

        # Check if the received_online_users list is empty
        if not received_online_users:
            print("No users online right now.")
        else:
            # Create a list of lists representing the table data
            table_data = [
                [user['username'], user['ip'], user['port']] for user in received_online_users
            ]

            # Define the headers for the table
            headers = ["Username", "IP", "Port"]

            # Print the table using tabulate
            #print(tabulate(table_data, headers, tablefmt="grid"))

    # function for sending hello message
    # a timer thread is used to send hello messages to udp socket of registry
    def sendHelloMessage(self):
        message = "HELLO " + self.loginCredentials[0]
        logger.info("Send to " + self.registryName + ":" + str(self.registryUDPPort) + " -> " + message)
        self.udpClientSocket.sendto(message.encode(), (self.registryName, self.registryUDPPort))
        self.timer = threading.Timer(conf.peerSendTime, self.sendHelloMessage)
        self.timer.start()

print("from time ")
# peer is started
main = peerMain()

