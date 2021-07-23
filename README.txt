Authors = [Nick Augustine]

This program is a client server chat application allowing multiple simultaneously connected clients to communicate with
each other. The program is divided into two main parts: server.py and client.py.

To run the server:
    Simply just enter python server.py on the terminal

To run the client:
    Enter python client.py on the terminal
    The client has access to the following commands:

        1. register [username] [password]
            adds a new client to the clients.txt file to be saved even when the client and/or server are terminated
        2. login [username] [password]
            logs in a client that is already registered and has a username and password assigned
        3. list
            list all connected online users avaialable for conversation
        4. message [username] [messageText]
            sends a message to the current user of your choice
        5. logout
            disconnects current client
        6. quit
            terminates client.py and disconnects from server