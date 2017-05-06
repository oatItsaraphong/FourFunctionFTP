# *******************************************************************
# This file illustrates how to send a file using an
# application-level protocol where the first 10 bytes
# of the message from client to server contain the file
# size and the rest contain the file data.
# *******************************************************************
import socket
import os
import sys

SIZE_HEAD = 10


#-----Connection Port ------------------------
# Server address
serverAddr = "localhost"
# Server port
serverPort = 1234
# Create a TCP socket
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Connect to the server
connSock.connect((serverAddr, serverPort))


#-------------------------------------------------------

# **************************************************
# To send an Item back to server base one the input
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

# ********************************************************
# Display what one the local directory
# **********************************************************
def llsCommand():
	import commands
	temp = ""
	for line in commands.getstatusoutput('ls -l'):
		if (line != 0):
			temp = temp + line
	print temp

# ********************************************************
# Show the way to use the program
# **********************************************************
def helpMessage():
	print "All command avaliable: "
	print "   get <filename>   	- to download file from server"
	print "   put <filename>   	- to upload file from server"
	print "   ls            	- to list all the file in the server"
	print "   lls   			- to list all the file in the client"
	print "   help   			- to list all the file in the client"


#*************************************************************
#Show ls command from the server side
#***********************************************************
def lsCommand():
	#print "back from server"
	result = listenForPort()
	print result
	#while True:
	#	test = readPacket(connSock, SIZE_HEAD)
	#	print test


#*************************************************************
#listen for the new port and retrive the data from the new
#	port and send back only the data
# @return - retrived data
#***********************************************************
def listenForPort():
	newPort = readPacket(connSock, SIZE_HEAD)
	#print newPort
	newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	newSocket.connect((serverAddr, int(newPort)))
	
	data = ""
	temp = ""
	while True:
		temp = readPacket(newSocket, SIZE_HEAD)

		#break when donot have any message
		if(temp == ''):
			break
		data = data + temp

	newSocket.close()
	return data


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
	
	#print recvBuff
	return recvBuff



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
def readPacket(clientIn, numBytes):
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

	#detect empty message
	if(fileSizeBuff == ''):
		return fileData

	newSize = int(fileSizeBuff)
	fileData = recvAll(clientIn, newSize)
		
	return fileData

def getOneItem(fileName):
	result = listenForPort()
	if(result == ''):
		print "File not exist"
	else:	
		fileObj = open(fileName, "w")
		fileObj.write(result)

		fileObj.close()
		print "Downloaded " + fileName

# ******************************************************
# listen for a new port number and send the file to the server
# @param - sendData - data that need to be send to the server
# @return - none
# *******************************************************
def listenForPortSend(sendData):
	newPort = readPacket(connSock, SIZE_HEAD)
	#print newPort
	newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	newSocket.connect((serverAddr, int(newPort)))

	#this just need to run once because 
	# sendOneItem is already looping
	sendOneItem(newSocket,sendData ,SIZE_HEAD)

	newSocket.close()


#*********************************************************
# read the file from local address and retrive all the fiel
# @param - fileName - file to open
# @return - none
# ************************************************************
def putOneItem(fileName):
	if(os.path.isfile(fileName)):
		fileObj = open(fileName, "r")
		if(fileObj):
			size = os.stat(fileName).st_size
			fileData = fileObj.read(size)
			listenForPortSend(fileData)
			fileObj.close()
			print "Uploaded " + fileName
		else:
			print "Error reading File"
	else:
		print "No such file in the directory"

# Keep sending until all is sent
while True:

	#connect to server with connection channel
	print "ftp> ",
	commandR = raw_input()
	command = str.split(commandR)

	if(command[0] == 'get' and len(command) > 1):
		sendOneItem(connSock, commandR, SIZE_HEAD)
		getOneItem(command[1])	
	elif(command[0] == 'put' and len(command) > 1):
		sendOneItem(connSock, commandR, SIZE_HEAD)
		putOneItem(command[1])	
	elif(command[0] == 'ls'):
		sendOneItem(connSock, command[0], SIZE_HEAD)	
		lsCommand()
	elif(command[0] == 'quit'):
		sendOneItem(connSock, command[0], SIZE_HEAD)
		break;
	elif(command[0] == 'lls'):
		llsCommand()
	elif(command[0] == '-h'):
		helpMessage()
	else:
		print "Unknow command. Type help for more information"

	
# Close the socket and the file
connSock.close()

	


