import sys
import zmq
import threading
import time
import queue
import base64

buforOfMessages = queue.Queue()
lock = threading.Lock()
context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind("tcp://127.0.0.1:50000")

socket2 = context.socket(zmq.ROUTER)
#socket2.bind("tcp://127.0.0.1:50001") <- for running in localhost
socket2.bind("tcp://127.0.0.1:50001")

users = []
users_dictionary = {}
pubKeys = []
pubKeys_dictionary = {}

print("Hello on server of CrypText Beta 0.1.0 v, server will run forever, until die")

while True:
    #frist recv add person
    person = socket2.recv().decode('utf-8')
    message = socket2.recv().decode('utf-8')
    #second loop recive public key from this user
    person = socket2.recv().decode('utf-8')
    valueOfP = socket2.recv().decode('utf-8')

    person = socket2.recv().decode('utf-8')
    valueOfG = socket2.recv().decode('utf-8')

    person = socket2.recv().decode('utf-8')
    valueOfPub = socket2.recv().decode('utf-8')

    print('\n', valueOfP, valueOfG, valueOfPub)
    users.append(person)
    pubKeys.append(valueOfPub)
    print(len(users))
    if len(users) > 1:
        #send to user 0 name of user1
        socket2.send_multipart([bytes(users[0], 'utf-8'),bytes(users[1], 'utf-8')])
        #send to user 1 name of user0 
        socket2.send_multipart([bytes(users[1], 'utf-8'),bytes(users[0], 'utf-8')])
        #send to user0 public key of user1
        socket2.send_multipart([bytes(users[0], 'utf-8'),bytes(pubKeys[1], 'utf-8')])
        #send to user1 public key of user0
        socket2.send_multipart([bytes(users[1], 'utf-8'),bytes(pubKeys[0], 'utf-8')])
        socket2.close()
        break

users_dictionary = {bytes(users[0], 'utf-8'): bytes(users[1], 'utf-8'), bytes(users[1], 'utf-8'): bytes(users[0], 'utf-8')}

def reciveMessage():
    while True:
        global socket, lock, buforOfMessages
        person = socket.recv()
        message = socket.recv()
        print("Recived message")
        lock.acquire()
        buforOfMessages.put(person)
        buforOfMessages.put(message)
        lock.release()

def sendMessage():
    time.sleep(2)
    print("Started sending message!")
    while True:
        global socket, lock, buforOfMessages, users_dictionary
        if (buforOfMessages.empty() == False):
            lock.acquire()
            userToSend = buforOfMessages.get() 
            messageToSend = buforOfMessages.get()
            encodedMessage = base64.b64encode(messageToSend)
            print(encodedMessage, userToSend)
            lock.release()
            socket.send_multipart([users_dictionary[userToSend], messageToSend])


rcvMSG = threading.Thread(target=reciveMessage)
sndMSG = threading.Thread(target=sendMessage)
rcvMSG.start()
sndMSG.start()