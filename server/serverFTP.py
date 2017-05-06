# This file implements a server for receiving the file
# sent using sendfile(). The server receives a file and
# prints it's contents.
# *****************************************************

import socket
import os


SIZE_HEAD = 10;

# The port on which to listen
listenPort = 1234
# Create a welcome socket. 
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
welcomeSock.bind(('', listenPort))
# Start listening on the socket
welcomeSock.listen(1)

# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param sock - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(sock, numBytes):
	# The buffer
	recvBuff = ""
	# The temporary buffer
	tmpBuff = ""
	
	# Keep receiving till all is received
	while len(recvBuff) < numBytes:
		
		# Attempt to receive bytes
		tmpBuff =  sock.recv(numBytes)
		
		# The other side has closed the socket
		if not tmpBuff:
			break
		
		# Add the received bytes to the buffer
		recvBuff += tmpBuff
	
	return recvBuff

# **************************************************
# To send an Item back to client base one the input
# @param client - is the connection to the client
# @param  item - item that want to sent out
# @param numBytes - number of byte to specify the 
#					size of the file
# @return - none
# ****************************************************
def sendOneItem(client, item, numBytes):
	itemSize = str(len(item))
	while len(itemSize) < numBytes:
		itemSize = "0" + itemSize

	itemSend = itemSize + item;
	
	numSent = 0
	while len(itemSend) > numSent:
			numSent += client.send(itemSend[numSent:])






# ************************************************
# Receives the entitle packet and parse it 
# 	by seperate the first section as the size of file
# 	the second is the actual data
# @param client - is the connection to the client
# @param  item - item that want to sent out
# @param numBytes - number of byte to specify the 
#					size of the file
# @return - the receieved data
# ****************************************************
def readCommand(clientIn, numBytes):
	# The buffer to all data received from the
	# the client.
	fileData = ""
	
	# The temporary buffer to store the received
	# data.
	recvBuff = ""
	
	# The size of the incoming file
	fileSize = 0	
	
	# The buffer containing the file size
	fileSizeBuff = ""
	
	# Receive the first 10 bytes indicating the
	# size of the file
	fileSizeBuff = recvAll(clientIn, numBytes)
	if(fileSizeBuff == ''):
		return fileData
		
	# Get the file size
	newSize = int(fileSizeBuff)

	# Get the file data
	fileData = recvAll(clientIn, newSize)

	return fileData

# **********************************************
# Handle ls command from client
# @param clientIn - Control connection
# @return  none
# *********************************************
def listCommand(clientIn):
	import commands
	temp = "";
	# Run ls command, get output, and print it
	for line in commands.getstatusoutput('ls -l'):
		if (line != 0):
			temp = temp + line


	createSocket(clientIn, temp)

def createSocketIn(clientIn):
	newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Bind the socket to port 0
	newSocket.bind(('',0))
	newPortNumber = newSocket.getsockname()[1]

	#send new port number back
	sendOneItem(clientIn, str(newPortNumber), SIZE_HEAD)
	newSocket.listen(1)

	print "Waiting for incoming connections..."
	#send the data to client
	newClientSock, addr = newSocket.accept()
	print "Accepted connection from client: ", addr
	newData = readCommand(newClientSock, SIZE_HEAD)

	newSocket.close()
	print "close side connection"

	return newData



def createSocket(clientIn, item):
	newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Bind the socket to port 0
	newSocket.bind(('',0))
	newPortNumber = newSocket.getsockname()[1]

	#send new port number back
	sendOneItem(clientIn, str(newPortNumber), SIZE_HEAD)
	newSocket.listen(1)
	
	print "Waiting for side connections..."
	#send the data to client
	newClientSock, addr = newSocket.accept()
	print "Accepted connection from client: ", addr
	sendOneItem(newClientSock, item,SIZE_HEAD)

	newSocket.close()
	print "close side connection"


def sendFileOut(clientIn, fileName):
	if(os.path.isfile(fileName)):
		fileObj = open(fileName, "r")
		fileData = fileObj.read(100)
		createSocket(clientIn, fileData)
		fileObj.close()
	else:
		createSocket(clientIn, '')
		

def receiveFileIn(clientIn, fileName):
	result = createSocketIn(clientIn)
	print result
	fileObj = open(fileName, "w")
	fileObj.write(result)

	fileObj.close()
	print "Downloaded " + fileName

# Accept connections forever
while True:
	
	print "Waiting for connections..."
		
	# Accept connections
	clientSock, addr = welcomeSock.accept()
	
	print "Accepted connection from client: ", addr
	print "\n"
	while True:
		command = readCommand(clientSock, SIZE_HEAD)
		#print str(len(command)) + " == one"
		command = str.split(command)
		#print str(len(command)) + " == tqo"
		if(command[0] == 'get'):
			print command[0] + "-- " + command[1]
			sendFileOut(clientSock, command[1])
		elif(command[0] == 'put'):
			print command[0] + "-- "+  command[1]
			receiveFileIn(clientSock, command[1])
		elif(command[0] == 'ls'):
			listCommand(clientSock)
			print command[0] + "-- success"
		elif(command[0] == 'quit'):
			print command[0] + " by client "
			break


	
	# Close our side
	clientSock.close()


welcomeSock.close()

	
	
