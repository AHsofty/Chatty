import socket
import threading
import UI
import time
import random
import pickle
from Crypto.Cipher import AES


class Connection():
	def __init__(self, ui):
		self.connected = False
		self.ui = ui


	def connect(self, IP, PORT, ROOM):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((IP, PORT))
		self.connected = True

		# now that we are connected to the server, we need to check if the room we specified is still available.
		# If it's not available (because it's full), we need to kick the user off the server


		#self.s.sendall(pickle.dumps((str(ROOM), 1))) # 0 = controllable, 1 = non-controllable
		self.send_message([str(ROOM), 1])


	def send_message(self, message):
		"""
		This will always be a len2 list
		"""
		# First we encrypt our message, usually I would make a seperate functionf or this, but in this case there is no actual point in doing so. I did do it in the server script though
		obj = AES.new('You are a tosser'.encode("utf8"), AES.MODE_CFB, 'Aipom piplup 420'.encode("utf8")) # Gotta love pokemon
		ciphertext = obj.encrypt(pickle.dumps(message))
		self.s.sendall(ciphertext)


	def receive(self):
		while True:
			"""
			We'll always receive a list with len 3
			[0] = message
			[1] = User 
			[2] = code (0=sent from actual message, 1=actual message from server, may be an error or something)


			"""
			# We don't want to add [1]=1 to our messages list, it's ususally just passing information between client and server
			# There is no reason for the user to see this


			# So first before we do anything, we need to decrypt our ciphertext and convert it from bytes to an actual readable string
			self.encryped_message = self.s.recv(1024)
			self.obj = AES.new('You are a tosser'.encode("utf8"), AES.MODE_CFB, 'Aipom piplup 420'.encode("utf8"))
			self.cipher = self.obj.decrypt(self.encryped_message)
			self.data = pickle.loads(self.cipher)    

			if self.data[0] != "":
				if self.data[0] == "max_room" and self.data[2] == 1 and self.data[1] == -1: # This cannot be triggered by regular messages ([1] would be 0)
					self.connected = False
					self.ui.EditLabel("The room you tried to connect to is full\nplease try again\n")
					self.ui.connected = False # Changes the connection state to False in the UI class
					return;
				else:
					# HERE WE RECEIVE THE MESSAGES FROM THE SEVRER, THIS MESSAGE WILL BE ADDED TO A LIST ON THE CLINET
					# SO IT WONT BE STORED ON THE SERVER
				
					if self.data[2] == 0: # We only want to add mesasges sent my a client, not the system
						print(self.data[1])
						if self.data[1] != None:
							self.ui.EditLabel((f"User {self.data[1]}> {self.data[0]}\n"))
						else:
							self.ui.EditLabel((f"Server> {self.data[0]}\n"))



	def GetUiMessage(self, msg):
		global s
		global connection

		'''
		This bit here should absolutely be changed
		Now we connect to the server after sending the first message rather than immaidately after starting
		'''
		self.message = (f"{msg}")
		self.send_message((msg, 0))



