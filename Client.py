import zmq
import threading
import time
from PyQt6.QtWidgets import *
import sys
from datetime import datetime
from multiprocessing import Queue
from PyQt6 import QtCore
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
import re
from hashlib import sha256
from base64 import b64decode
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class welcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CrypText")
        self.setFixedSize(500,180)
        self.widgets()
        self.inputtedName = ""

    def widgets(self):
        self.taskName = QLabel("Please enter your name: ", self)
        self.taskName.setGeometry(180,20,200,60)
        self.nameInput = QLineEdit(self)
        self.nameInput.setGeometry(50,100,400,40)
        self.nameInput.returnPressed.connect(self.enteredInput)

    def enteredInput(self):
        self.inputtedName = self.nameInput.text()
        #self.nameInput.hide()
        #self.taskName.setText("Please wait to another user, and for establishing secure connection!")
        #self.taskName.setGeometry(70,70,360,40)
    def getInputtedName(self):
        return self.inputtedName  

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CrypText")
        self.setFixedSize(1280,720)
        self.widgets()
        
        # setupUi
    def widgets(self):
        pushButton = QPushButton("Send message",self)
        pushButton.clicked.connect(self.addMessageToList)
        pushButton.setGeometry(1080, 560, 171, 101)
        
        self.lineEdit = QTextEdit(self)
        self.lineEdit.setGeometry(70, 560, 991, 101)
        self.lineEdit.setPlaceholderText("Type your message...")

        self.label = QLabel(self)
        self.label.setGeometry(350, 0, 611, 41)

        self.plainTextEdit = QPlainTextEdit(self)
        self.plainTextEdit.setGeometry(70, 50, 1181, 501)
        self.plainTextEdit.setReadOnly(True)

    def setLabel(self, text):
        self.label.setText(f"Chatting with {text}")

    def addMessageToList(self):
        global main_buffor
        now = datetime.now()
        messageDate = str(now.strftime("%d/%m/%Y %H:%M:%S"))
        temp_msg = self.lineEdit.toPlainText() 
        self.plainTextEdit.appendPlainText(messageDate + " " + ownUserName + "\n" + temp_msg)
        self.lineEdit.clear()
        sendMessage(temp_msg)

    def addRecivedMessage(self,message):
        global main_buffor
        now = datetime.now()
        messageDate = str(now.strftime("%d/%m/%Y %H:%M:%S"))
        lock.acquire()
        main_buffor.put(messageDate + " " + secondUser + "\n" + message)
        lock.release()
    def updateMainWindow(self, message):
        print(type(message))
        self.plainTextEdit.appendPlainText(message)


class keyInput(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CrypText")
        self.setFixedSize(300,300)
        self.widgets()
        self.inputtedP = ""
        self.inputtedG = ""
        self.inputtedPriv = ""
        self.ready = False

    def widgets(self):
        self.taskName2 = QLabel("Please enter your DH parameters: ", self)
        self.taskName2.setGeometry(73,20,200,60)
        #p parameter label 
        self.pLabel = QLabel("p", self)
        self.pLabel.setGeometry(50,100,10,20)
        #g parameter label 
        self.gLabel = QLabel("g", self)
        self.gLabel.setGeometry(50,150,10,20)
        #Priv parameter label 
        self.privLabel = QLabel("Priv key value", self)
        self.privLabel.setGeometry(50,200,75,20)
        #p input area
        self.keyInputP = QLineEdit(self)
        self.keyInputP.setGeometry(70,100,200,20)
        self.keyInputP.returnPressed.connect(self.keyInputed)
        #g input area
        self.keyInputG = QLineEdit(self)
        self.keyInputG.setGeometry(70,150,200,20)
        self.keyInputG.returnPressed.connect(self.keyInputed)
        #Priv key area
        self.keyInputPriv = QLineEdit(self)
        self.keyInputPriv.setGeometry(130,200,140,20)
        self.keyInputPriv.returnPressed.connect(self.keyInputed)

    def keyInputed(self):
        self.inputtedP = self.keyInputP.text()
        self.inputtedG = self.keyInputG.text()
        self.inputtedPriv = self.keyInputPriv.text()
        if((re.search('^\\d+$', self.inputtedP) != None) and (re.search('^\\d+$', self.inputtedG) != None ) and (re.search('^\\d+$', self.inputtedPriv) != None)):
            if (self.inputtedP != "" and self.inputtedG != "" and self.inputtedPriv != ""):
                self.ready = True
                self.keyInputP.hide()
                self.keyInputG.hide()
                self.keyInputPriv.hide()
                self.pLabel.setHidden(True)
                self.gLabel.setHidden(True)
                self.privLabel.setHidden(True)
                self.taskName2.setText("Please wait to another user,\nand for establishing secure connection!")
                self.taskName2.setGeometry(60,120,360,40)
    def getInputtedKey(self):
        if (self.ready == True):
            return self.inputtedP, self.inputtedG, self.inputtedPriv



def updateMessage():
    global main_buffor
    while True:
        QtCore.QCoreApplication.processEvents()
        lock.acquire()
        if not main_buffor.empty():
            window.updateMainWindow(main_buffor.get())
        #60 fps
        lock.release()
        time.sleep((1/60))

def sendMessage(msg):
        global socket
        encryptedText = encryptMessage(msg)
        socket.send(encryptedText)

def reciveMessage():
    global socket, window
    while True:
        QtCore.QCoreApplication.processEvents()
        message = socket.recv()
        #add decryption to message:
        decryptedText = decryptMessage(message)
        window.addRecivedMessage(decryptedText.decode("utf-8"))

def getSecureConnection(name, valOfP, valOfG, valOfSecret):
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    port = 50001
    socket.setsockopt_string(zmq.IDENTITY, f"{name}")#_CONNECTION
    socket.connect("tcp://127.0.0.1:%s" %port)
    socket.send_string("Hello!")
    socket.send(valOfP.encode('utf-8'))
    socket.send(valOfG.encode('utf-8'))
    socket.send(valOfSecret.encode('utf-8'))
    secondUserName = ""
    #wait for server to recive second user name
    while True:
        QtCore.QCoreApplication.processEvents()
        try:
            secondUserName = socket.recv(flags=zmq.NOBLOCK)
        except zmq.Again as e:
            continue
        if secondUserName != "":break
    userPublicKey = ""
    #wait for server, to get second user public key, to encrypy messages
    while True:
        QtCore.QCoreApplication.processEvents()
        try:
            userPublicKey = socket.recv(flags=zmq.NOBLOCK)
        except zmq.Again as e:
            continue
        if userPublicKey != b'-':break
    socket.close()
    return secondUserName.decode('utf-8'), int(userPublicKey.decode('utf-8'))



def encryptMessage(message):
    global keyToCipher
    secret = sha256(str(keyToCipher).encode('utf8')).digest()
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(pad(message.encode('utf-8'),AES.block_size)))

def decryptMessage(encryptedMessage):
    global keyToCipher
    secret = sha256(str(keyToCipher).encode('utf8')).digest()
    raw = b64decode(encryptedMessage)
    cipher = AES.new(secret, AES.MODE_CBC, raw[:AES.block_size])
    return unpad(cipher.decrypt(raw[AES.block_size:]), AES.block_size)

lock = threading.Lock()
context = zmq.Context()
socket = context.socket(zmq.DEALER)
port = 50000
app = QApplication([])
window = Window()
welcomeScreen = welcomeWindow()
welcomeScreen.show()
keyScreen = keyInput()
paramP = 0
paramG = 0 
paramPriv = 0 

uniqe_id =  ""
while uniqe_id == "":
    QtCore.QCoreApplication.processEvents()
    uniqe_id = welcomeScreen.getInputtedName()
welcomeScreen.hide()
keyScreen.show()
setDHkey = False
while setDHkey == False:
    QtCore.QCoreApplication.processEvents()
    try:
        paramP, paramG, paramPriv = keyScreen.getInputtedKey()
    except:
        continue
    if (paramP != '' and paramG != '' and paramPriv != ''):
        paramP = int(paramP)
        paramG = int(paramG)
        paramPriv = int(paramPriv)
        setDHkey = True

uniqe_id = bytes(uniqe_id.encode('utf-8'))
ownUserName = uniqe_id.decode('utf-8')
secretValue = paramG ^ paramPriv % paramP

secondUser, sharedValue = getSecureConnection(ownUserName, str(paramP), str(paramG), str(secretValue))
keyToCipher = sharedValue ^ paramPriv % paramP 
print(keyToCipher)
window.setLabel(secondUser)

main_buffor = Queue()

def main():
    socket.setsockopt(zmq.IDENTITY, uniqe_id)
    socket.connect("tcp://127.0.0.1:%s" %port)
    rcvMSG = threading.Thread(target=reciveMessage)
    upMSG = threading.Thread(target=updateMessage)
    upMSG.start()
    rcvMSG.start()
    keyScreen.hide()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
