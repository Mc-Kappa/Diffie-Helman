How to run?

In Server.py set socket.bind("tcp://127.0.0.1:50000") to two different socket. 
In Client.py in def getSecureConnection in one instance set first port defined in server.py, in second instance, second port from server config. 
First Run server, then first instance and second instance. 
If any client disconnect, you have to shut down all system (it's prototype, so it doesnt work ideal).
