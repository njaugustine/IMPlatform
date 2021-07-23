import select, socket, sys
# Echo client program
import socket

#Author: Dave Ogle
#Author: Nick Augustine

from pip._vendor.distlib.compat import raw_input

count = 0
HOST = 'localhost'    # The remote host
PORT = 5001              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
msg = ''

inputs = [s, sys.stdin]
newData = 0

while inputs and msg.lower() != 'quit':
    readable, writable, exceptional = select.select(inputs, inputs, inputs)
    for socket in readable:
        if socket is s:
            print('got something from network')
            data = s.recv(1024)
            data = data.decode('utf-8')
            print(data)
        elif socket is sys.stdin:
            print('received something from cmd line')
            msg = raw_input()
            msgBytes = bytes(msg, 'utf-8')
            s.sendall(msgBytes)
            if msg.lower() == 'quit': #terminates on quit command
                break

s.close()