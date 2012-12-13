import asyncore
import collections
import socket
import random
import getpass
import hashlib

MAX_MESSAGE_LENGTH = 1024
#MY_CHANNEL_PASS    = "a60657539c531b1202cf4f085e5f919b308c3ab621dac55b87da826c9d20d3e9374c9c11217fdb16d9757880bf871ba499b6b493a6f23dda0677e0cae3350ae1"
MY_CHANNEL_PASS    ="b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86"
class Host(asyncore.dispatcher):
    def __init__(self, address=('127.0.0.1', 12581)):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.listen(1)
        self.remote_clients = []

    def handle_accept(self):
        salting = random.randint(1,1000)
        socket, addr = self.accept() # For the remote client.
        print 'New Client at ', addr
        #strr = 'New Client at : [' + str(addr[0])+":" + str(addr[1])+"]\n\n"
        #self.broadcast(strr)
        self.remote_clients.append(RemoteClient(self, socket, addr,salting))

    def broadcast(self, message):
        for remote_client in self.remote_clients:
            remote_client.say(message)


class RemoteClient(asyncore.dispatcher):
    def __init__(self, host, socket, address,salting):
        asyncore.dispatcher.__init__(self, socket)
        self.salting=salting
        self.host = host
        self.outbox = collections.deque()
        is_salted=False
        self.salter()

    def salter(self):
        self.send("[+]"+str(self.salting))

    def say(self, message):
        self.outbox.append(message)

    def handle_read(self):
        global MY_CHANNEL_PASS
        client_message = self.recv(MAX_MESSAGE_LENGTH)
        display = True

        if "[+]" in client_message :
            display = False
            client_message=client_message.split("[+]")[1]
            client_message_salted=str(hashlib.sha512(MY_CHANNEL_PASS+str(self.salting)).hexdigest())
            if client_message!=client_message_salted:
                self.close()

        if display == True:
            self.host.broadcast(client_message)

    def handle_write(self):
        if not self.outbox:
            return
        message = self.outbox.popleft()
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError('Message too long')
        self.send(message)

if __name__ == '__main__':
    host = Host()
    asyncore.loop()
