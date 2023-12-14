"""
Registry Server for Peer-to-Peer Chat Application

This Python script implements a registry server for a peer-to-peer chat application. The registry server
facilitates communication between peers by managing user accounts, online status, and room creation.
It also handles both TCP and UDP connections, allowing peers to register, log in, log out, search for
other users, and create/join rooms.

The key components and functionalities of the registry server include:

1. **ClientThread Class:**
   - Represents a thread for each connected peer.
   - Handles user registration, login, logout, and search operations.
   - Manages the UDP server thread for each peer.

2. **UDPServer Class:**
   - Represents the UDP server thread associated with each connected peer.
   - Implements a timer mechanism to handle timeouts and disconnect inactive peers.

3. **Main Registry Server:**
   - Listens for incoming TCP and UDP connections on specified ports.
   - Manages user accounts, online status, and peer threads.
   - Utilizes the 'db' module for database operations related to user accounts and rooms.
   - Monitors incoming connections and spawns new ClientThread instances for each connected peer.

4. **Database Operations:**
   - Uses the 'db' module to perform database operations, such as user registration, login, logout,
     account existence checks, room creation, joining, and updating.

5. **Logging:**
   - Utilizes the 'logging' module to log server activities and received messages.

6. **Peer-to-Peer Communication:**
   - Enables peers to register, log in, log out, search for other users, and create/join rooms.
   - Manages online status and UDP connections to keep track of active peers.

7. **Thread Synchronization:**
   - Uses locks to ensure thread-safe access to shared resources and prevent race conditions.

Note: The script listens for incoming connections and processes peer messages. The UDP server threads
are responsible for managing timeouts and disconnecting inactive peers.

Author: [Your Name]
Date: [Current Date]
"""



from socket import *
import threading
import select
import logging
import db
from utils.loader import *
import os
from dotenv import main
import os
#main.load_dotenv()
#host = os.getenv('REGISTRY_HOSTNAME_IP')




# onlinePeers list for online account
onlinePeers = {}

# accounts list for accounts
accounts = {}

# tcpThreads list for online client's thread
tcpThreads = {}

# This class is used to process the peer messages sent to registry
# for each peer connected to registry, a new client thread is created
class ClientThread(threading.Thread):



    # initializations for client thread
    def __init__(self, peerIp, peerPort, tcpPeerClientSocket):
        # Thread constructor for initialization
        threading.Thread.__init__(self)
        # ip of the connected peer
        self.ip = peerIp
        # lock for now is None
        self.lock = None
        # port number of the connected peer
        self.port = peerPort
        # socket of the peer
        self.tcpClientSocket = tcpPeerClientSocket
        # username, online status and udp server initializations
        self.username = None
        self.isOnline = True
        self.udpServer = None
        # At this point we successfully connected to the peer trying to connect with us
        print("Registry message : New thread started for peer at " + peerIp + ":" + str(peerPort))

    # run method contains the code that the thread wll execute
    def run(self):
        # locks for thread which will be used for thread synchronization
        # locks make sure that no two threads will access the same resource at the same time
        # this will prevent race condition or and ensure data integrity
        self.lock = threading.Lock()
        print("Connection from: " + self.ip + ":" + str(port))
        print("IP Connected: " + self.ip)
        
        while True:
            try:
                # waits for incoming messages from peers
                message = self.tcpClientSocket.recv(1024).decode().split()

                # if message is empty or something went wrong
                if not message:
                    print("No message received, client may have disconnected.")
                    break

                logging.info("Received from " + self.ip + ":" + str(self.port) + " -> " + " ".join(message))            
                #   JOIN    #
                if message[0] == "JOIN":
                    # join-exist is sent to peer,
                    # if an account with this username already exists
                    if db.is_account_exist(message[1]):
                        response = "join-exist"
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)  
                        self.tcpClientSocket.send(response.encode())
                    # join-success is sent to peer,
                    # if an account with this username is not exist, and the account is created
                    else:
                        db.register(message[1], message[2])
                        response = "join-success"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())
                #   LOGIN    #
                elif message[0] == "LOGIN":
                    # login-account-not-exist is sent to peer,
                    # if an account with the username does not exist
                    if not db.is_account_exist(message[1]):
                        response = "login-account-not-exist"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())
                    # login-online is sent to peer,
                    # if an account with the username already online
                    elif db.is_account_online(message[1]):
                        response = "login-online"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())
                    # login-success is sent to peer,
                    # if an account with the username exists and not online
                    else:
                        # retrieves the account's password, and checks if the one entered by the user is correct
                        retrievedPass = db.get_password(message[1])
                        # if password is correct, then peer's thread is added to threads list
                        # peer is added to db with its username, port number, and ip address
                        if retrievedPass == message[2]:
                            self.username = message[1]
                            self.lock.acquire()
                            try:
                                tcpThreads[self.username] = self
                            finally:
                                self.lock.release()

                            db.user_login(message[1], self.ip, message[3])
                            # login-success is sent to peer,
                            # and a udp server thread is created for this peer, and thread is started
                            # timer thread of the udp server is started
                            response = "login-success"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                            self.tcpClientSocket.send(response.encode())
                            self.udpServer = UDPServer(self.username, self.tcpClientSocket)
                            self.udpServer.start()
                            self.udpServer.timer.start()
                        # if password not matches and then login-wrong-password response is sent
                        else:
                            response = "login-wrong-password"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                            self.tcpClientSocket.send(response.encode())
                #   LOGOUT  #
                elif message[0] == "LOGOUT":
                    # if user is online,
                    # removes the user from onlinePeers list
                    # and removes the thread for this user from tcpThreads
                    # socket is closed and timer thread of the udp for this
                    # user is cancelled
                    if len(message) > 1 and message[1] != None and db.is_account_online(message[1]):
                        db.user_logout(message[1])
                        self.lock.acquire()
                        try:
                            if message[1] in tcpThreads:
                                del tcpThreads[message[1]]
                        finally:
                            self.lock.release()
                        print(self.ip + ":" + str(self.port) + " is logged out")
                        self.tcpClientSocket.close()
                        self.udpServer.timer.cancel()
                        break
                    else:
                        self.tcpClientSocket.close()
                        break
                #   SEARCH  #
                elif message[0] == "SEARCH":
                    # checks if an account with the username exists
                    if db.is_account_exist(message[1]):
                        # checks if the account is online
                        # and sends the related response to peer
                        if db.is_account_online(message[1]):
                            peer_info = db.get_peer_ip_port(message[1])
                            response = "search-success " + peer_info[0] + ":" + peer_info[1]
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                            self.tcpClientSocket.send(response.encode())
                        else:
                            response = "search-user-not-online"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                            self.tcpClientSocket.send(response.encode())
                    # enters if username does not exist 
                    else:
                        response = "search-user-not-found"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "CREATE":
                    # CREATE-exist is sent to peer,
                    # if an room with this username already exists
                    if db.is_room_exist(message[1]):
                        response = "room-exist"
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)  
                        self.tcpClientSocket.send(response.encode())
                    else:
                        db.register_room(message[1])
                        response = "creation-success"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())
                elif message[0] == "JOINROOM":
                    # checks if an account with the username exists
                    if db.is_room_exist(message[1]):
                        # checks if the room exists
                        # and sends the related response to peer
                        id, peers = db.get_room_peers(message[1])
                        peers.append(message[2])
                        peers = list(set(peers))
                        db.update_room(id, peers)
                        response = "success " + str(peers)
                        print(response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())
                    # enters if username does not exist 
                    else:
                        response = "search-fail"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "UPDATE":
                        id, peers = db.get_room_peers(message[1])
                        response = "updated " + str(peers)
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "EXIT":
                        db.remove_peer(message[1], message[2])
                        response = "SUCCESS"
                        self.tcpClientSocket.send(response.encode())
                
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr)) 


    # function for resettin the timeout for the udp timer thread
    def resetTimeout(self):
        self.udpServer.resetTimer()




# Implementation of the UDP server thread for clients
class UDPServer(threading.Thread):
    """
    This class represents a UDP server thread for handling communication with clients.

    Attributes:
    - username: The username associated with the client.
    - timer: Timer object for tracking the timeout period.
    - tcpClientSocket: The associated TCP client socket.
    """

    # UDP server thread initializations
    def __init__(self, username, clientSocket):
        """
        Constructor for the UDPServer class.

        :param username: The username associated with the client.
        :param clientSocket: The associated TCP client socket.
        """
        threading.Thread.__init__(self)
        self.username = username
        # Timer thread for the UDP server is initialized with a timeout of 3 seconds
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.tcpClientSocket = clientSocket

    # If a hello message is not received before the timeout,
    # then the peer is considered disconnected
    def waitHelloMessage(self):
        """
        Handles the case when a hello message is not received before the timeout.
        Disconnects the peer, logs them out, and removes them from the online peers list.
        """
        if self.username is not None:
            # Log out the user in the database
            db.user_logout(self.username)

            # Remove the user from the online peers list
            if self.username in tcpThreads:
                del tcpThreads[self.username]

        # Close the associated TCP client socket
        self.tcpClientSocket.close()
        print("Removed " + self.username + " from online peers")

    # Resets the timer for the UDP server
    def resetTimer(self):
        """
        Resets the timer for the UDP server to the initial timeout period (3 seconds).
        """
        self.timer.cancel()
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.timer.start()

#-------------------------------Helper Functions--------------------------------------------#
def initialize_sockets(host, tcp_port, udp_port,max_of_users):
    """
    Initialize TCP and UDP sockets and bind them to the specified host and ports.

    Parameters:
    - host (str): The host address to bind the sockets.
    - tcp_port (int): The port for TCP communication.
    - udp_port (int): The port for UDP communication.

    Returns:
    - tcp_socket (socket): The initialized and bound TCP socket.
    - udp_socket (socket): The initialized and bound UDP socket.
    """
    # TCP Socket Initialization:
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    # UDP Socket Initialization:
    udp_socket = socket(AF_INET, SOCK_DGRAM)

    # Bind TCP and UDP Sockets:
    tcp_socket.bind((host, tcp_port))
    udp_socket.bind((host, udp_port))

    # Start TCP Listening:
    # - Listens for incoming TCP connections with a maximum queue size of 5.
    tcp_socket.listen(max_of_users)
    # Return initialized sockets
    return tcp_socket, udp_socket


def main():
    # tcp and udp server port initializations
    print("Registy started...")
    tcp_port = 15600
    udp_port = 15500

    # db testing if is working or not
    db_cursor = db.DB()

    hostname = gethostname()
    try:
        host = gethostbyname(hostname)
    except gaierror:
        import netifaces as ni
        host = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

    # main.load_dotenv()
    # host = os.getenv('REGISTRY_HOSTNAME_IP')
    print("Registry IP address: " + host)
    print("Registry port number: " + str(tcp_port))


    # creating the sockets
    tcpSocket, udpSocket = initialize_sockets(host,udp_port,tcp_port,5)

    # input sockets that are listened
    inputs = [tcpSocket, udpSocket]

    # log file initialization
    logging.basicConfig(filename="logs/registry.log", level=logging.INFO, filemode='w')


    # as long as at least a socket exists to listen registry runs
    while inputs:
        print("Listening for incoming connections...")
        # monitors for the incoming connections
        readable, writable, exceptional = select.select(inputs, [], [])
        for s in readable:
            # if the message received comes to the tcp socket
            # the connection is accepted and a thread is created for it, and that thread is started
            if s is tcpSocket:
                tcpClientSocket, addr = tcpSocket.accept()
                newThread = ClientThread(addr[0], addr[1], tcpClientSocket)
                newThread.start()
            # if the message received comes to the udp socket
            elif s is udpSocket:
                # received the incoming udp message and parses it
                message, clientAddress = s.recvfrom(1024)
                message = message.decode().split()
                # checks if it is a hello message
                if message[0] == "HELLO":
                    # checks if the account that this hello message
                    # is sent from is online
                    if message[1] in tcpThreads:
                        # resets the timeout for that peer since the hello message is received
                        tcpThreads[message[1]].resetTimeout()
                        print("Hello is received from " + message[1])
                        logging.info("Received from " + clientAddress[0] + ":" + str(clientAddress[1]) + " -> " + " ".join(message))

    # Closing the connection after finishing
    tcpSocket.close()


if __name__ == "__main__":
    main()


