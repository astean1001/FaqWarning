#!/usr/bin/env python2
import socket, sys
from thread import *
import logging

listening_port = 4485 # Using Random Listening Port :: 4485

max_conn = 300 # Max Connection
buffer_size = 4096 # Max Socket Buffer Size
# TODO : Make Settings To Be Able To Change Buffer Size

def start_proxy():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket Initiation
		print "[*] Initializing Sockets ... Done"
		s.bind(('',listening_port)) # Bind Socket For Listen
		print "[*] Sockets Binded Successfully ..."
		s.listen(max_conn) # Start Listening For Incoming Connections
		print "[*] Server Started Succesfully [ %d ]\n" % (listening_port)
	except Exception, e:
		print "[*] Unable To Initialize Socket"
		sys.exit(2)

	while True:
		try:
			conn, addr = s.accept() # Accept Connection From Client Browser
			data = conn.recv(buffer_size) # Recieve Client Data
			start_new_thread(conn_string, (conn, data, addr)) # Start A Thread
		except KeyboardInterrupt:
			s.close()
			print "\n[*] Proxy Server Shutting Down ... "
			print "[*] Have A Nice Day ... Commander !!!"
			sys.exit(1)
	s.close()

def isHTTP(url):
	if(url.find("https") != -1): # Remember, No HTTPS
		return False
	if (url.find("http") == -1):
		return False
	return True

def conn_string(conn, data, addr):
	first_line = data.split('\n')[0]
	try:
		print "first line : ",first_line
		url = first_line.split(' ')[1]
		print "url : ", url
		http_pos = url.find("://") # Find The Position of ://
		if (http_pos==-1):
			temp = url
		else:
			temp = url[(http_pos+3):] # Get Url (Http Removed)

		port_pos = temp.find(":") # Find Port (If Any)
		webserver_pos = temp.find("/") # Find The End of The Web Server

		if webserver_pos == -1:
			webserver_pos = len(temp)
		webserver = ""
		port = -1

		if(port_pos == -1 or webserver_pos < port_pos): # default port
			port = 80
			webserver = temp[:webserver_pos]
		else:
			port = int((temp[(port_pos+1):])[:webserver_pos - port_pos - 1])
			webserver = temp[:port_pos]

		proxy_server(webserver, port, conn, data, addr)
	except Exception, e:
		logging.error(e, exc_info=True)
		print first_line
		print "[*] Some Error Occured ... But We're in Control Now\n"
		pass

def proxy_server(webserver, port, conn, data, addr):
	dummy_stream = "GET http://test.gilgil.net HTTP/1.1\r\n"
	dummy_stream = dummy_stream +"Host: test.gilgil.net\r\n\r\n"
	data = dummy_stream + data

	try:
		# print str(webserver), str(port), str(conn), str(data), str(addr)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((webserver, port))
		print "data : ", data, "\n"
		s.send(data)

		while True:
			# Read Reply or Data to From End Web Server
			reply = s.recv(buffer_size)
			print "real_reply : ",reply
			if (reply.find('<title>test.gilgil.net</title>') != -1):
				replys = reply.split('HTTP')
				temp_reply = 'HTTP' + replys[2]

			elif (reply.find('HTTP/1.1 404 Not Found') != -1):
				temp_reply = ""

			else :
				temp_reply = reply

			

			if (len(reply) > 0):
				print "reply : ", temp_reply, "\n"
				conn.send(temp_reply) # Send Reply to Client
				# Send Notification To Proxy Server [ That's Us ]
				dar = float(len(reply))
				dar = float(dar / 1024)
				dar = "%.3s" % (str(dar))
				dar = "%s KB" % (dar)
				'Print A Custom Message For Request Complete'
				print "[*] Request Done: %s => %s <=" % (str(addr[0]),str(dar))
			else:
				# Break the connection if receiving data failed
				break
		# Sending Compelete. Socket Down.
		s.close()
		# Client Sock Down.
		conn.close()
	except socket.error, (value, message):
		s.close()
		conn.close()
		sys.exit(1)

if __name__ == "__main__":
	start_proxy()