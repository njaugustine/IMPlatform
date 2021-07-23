import select, socket, sys, queue
from pip._vendor.distlib.compat import raw_input

#Author: Dave Ogle
#Author: Nick Augustine

user_name = []
socket_list = []
online_list = []
connections = 0
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind(('localhost', 5001))
server.listen(5)
inputs = [server, sys.stdin]
newData = 0
outputs = queue.Queue()
user_connection = {}
clients = {}

def readClients():
    try:
        f = open('clients.txt', 'r')
        f1 = f.readlines()
        i = 0
        username = ''
        for x in f1:
            if i % 2 == 0:
                username = x.strip()
            else:
                clients[username] = x.strip()
            i +=1
    finally:
        f.close()

#attempts to login client
def login(user, pwd):
    if user in clients:
        if clients.get(user) == pwd:
            return 1
        return 0

#adds a new client and appends them to clients.txt
def register(user, pwd):
    if user in clients:
        return 0
    else:
        clients[user] = pwd
        try:
            f = open('clients.txt', 'a')
            f.write(user + '\n')
            f.write(pwd + '\n')
        finally:
            f.close()
        return 1

#boolean function determining if a user is logged in
def isLoggedIn(socket, user_connection, username):
    for key in user_connection.keys():
        if user_connection[key]==socket or key == username:
            print(key)
            return 1

    print('user not logged in')
    return 0

#retireves message sender and returns it
def getSender(socket, user_connection):
    for key in user_connection.keys():
        if user_connection[key]==socket:
            return key

#signs a user out and removes them from user_connection
def signout(socket, user_connection):
    for key in user_connection.keys():
        if user_connection[key] == socket:
            del user_connection[key]
            return

readClients()
while inputs:
    readable, writable, exceptional = select.select(inputs, inputs, inputs)
    for s in readable:
        if s is server:         # this stanza handles connection requests.
            print ("received a connect request from a client ")
            print
            connection, client_address = s.accept()
            if connections == 0:
                connections = 1
                connection1 = connection
            else:
                connection2 = connection
            print ("connection is {}".format (connection))
            connection.setblocking(0)
            inputs.append(connection)
        elif s is sys.stdin: #handles server side input
            newData = 1;
            command_string = raw_input()
            print ("received:::: " + command_string)
        else:
            # this stanza handles already connected sockets (data from clients)
            data = s.recv(1024)
            data = data.decode('utf-8')

            if data:
                print('read', data)
                words = data.split()
                print("received '", data, "'")
                for i,word in enumerate(words):

                    if word.lower() == 'login':
                        if len(words) > 2: #login takes two parameters
                            username = words[i+1]
                            password = words[i+2]
                            if not isLoggedIn(s, user_connection, username): #makes sure current socket is not already signed in and user is not already signed in
                                msg = ''
                                if(login(username, password)): #true if username/password is valid
                                    user_connection[username] = s
                                    msg = bytes('Server: logged in as ' + username, 'utf-8')
                                    s.send(msg)
                                else:
                                    msg = bytes('Server: username and/or password not found', 'utf-8')
                                    s.send(msg)
                            else:
                                msg = bytes('Server: Please ensure you and/or ' + username + ' is not already signed in', 'utf-8')
                                s.send(msg)
                        else:
                            msg = bytes('Server: login takes two paramters', 'utf-8')
                            s.send(msg)

                    elif word.lower() == 'register':
                        if len(words) > 2: #register takes two parameters
                            username = words[i+1]
                            password = words[i+2]
                            if register(username, password): #checks to see if username is unqique
                                msg = ('Server: registered and logged in as ' + username)
                                user_connection[username] = s
                            else:
                                msg = ('Server: user ' + username + ' is already taken')
                            msg = bytes(msg, 'utf-8')
                            s.send(msg)
                        else:
                            msg = bytes('Server: register takes two paramters', 'utf-8')
                            s.send(msg)

                    elif word.lower() == 'list':
                        msg = 'Server: '
                        for key in user_connection:
                            msg += key + ' '
                        msg = bytes(msg, 'utf-8')
                        s.send(msg)

                    #These commans require a user to be logged in
                    elif word.lower() == 'message' or word.lower() == 'logout': #verify that user is logged in
                        if isLoggedIn(s, user_connection, None): #verify that user is logged in
                            if word.lower() == 'message':
                                if len(words) > 1: #message takes 1 parameter
                                    username = words[i + 1]
                                    msg = words[i + 2]
                                    if username in user_connection: #verifies message receiver is logged in
                                        for i, word in enumerate(words):
                                            if i > 2:
                                                msg += ' ' + words[i]
                                        sender = getSender(s, user_connection)
                                        send_sock = user_connection[username]
                                        msg = bytes(sender + ': ' + msg, 'utf-8')
                                        send_sock.send(msg)
                                    else:
                                        msg = bytes('Server: user not found', 'utf-8')
                                        s.send(msg)
                                else:
                                    msg = bytes('Server: register takes one paramter', 'utf-8')
                                    s.send(msg)


                            elif word.lower() == 'logout' or word.lower() == 'quit':
                                signout(s, user_connection)
                                msg = bytes('Server: signed out', 'utf-8')
                                if(word.lower() != 'quit'):
                                    s.send(msg)
                        else:
                            msg = bytes('Server: must be logged in to use these features', 'utf-8')
                            if (word.lower() != 'quit'):
                                s.send(msg)

                if connection not in socket_list:
                    socket_list.append(connection)
                    # data = bytes(data, encoding='utf8')
                    outputs.put(data)
                    # if this is the first time i've seen this socket
                    # i want to add it to an array called 'outputs',
                    # i use outputs to allow me to queue data to send
    #                s.send ("echo response => " + data)
                print ("read " + data)
                if newData == 1:
                    data = command_string
                    newData = 0

    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()