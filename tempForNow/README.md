# P2P Chat
It is a p2p chat application that uses centralized index approach. It consists of two parts a registry application and a chat application. Registry application keeps track of the peers, and chat application allows peers to communicate with each other.
* Registry application can achieve following operations:
  
    * If the user chooses to create an account (choice 1), the code prompts for a username and password, and then calls the createAccount method to send a join message to the registry for account creation.

    * If the user chooses to log in (choice 2), the code prompts for a username, password, and port numbers for the peer server and room server. It then calls the login method to send a login message to the registry and performs actions based on the response.
      
    * If the user chooses to log out (choice 3), the code calls the logout method to send a logout message to the registry and performs necessary cleanup.
      
    * If the user chooses to search for a user (choice 4), the code prompts for a username and calls the searchUser method to send a search message to the registry and retrieve the IP address of the user if found.
      
    * If the user chooses to start a chat (choice 5), the code prompts for the username of the user to chat with. It then calls the searchUser method to retrieve the IP address and port number of the user and creates a client thread (PeerClient) to handle the chat.
      
    * If the user chooses to create a chatroom (choice 6), the code prompts for a room ID and calls the create_room method to send a create room message to the registry.
  
    * If the user chooses to join a chatroom (choice 7), the code prompts for a room ID, searches for the room using the search_room method, and creates a client thread (PeerClient) to handle the room communication

* Chat application can achieve following operations:
    * **Communication with Registry**<br/>
    Chat application sends messages to registry to achieve account creation, login, logout, search, start chat, create chat room and join a room operations.
    * **Chat**<br/>
    When a user wants to chat with another user, a chat request is sent to the other user. User should send an 'OK' message to accept or a 'REJECT' message to reject. However, if user is already chatting with someone else, then a 'BUSY' message will be sent automatically.
The sendHelloMessage method is responsible for sending periodic "HELLO" messages to the registry using a timer thread.

## How to Use It?
* Clone the repo.
* Run 'registry.py' and get your ip address.
* Run 'peer.py' and use your ip address to choose from following services:
     * create account
     * login
     * logout
     * search
     * start a chat
     * create a room
     * join a room
