"""
So first off, I want to say that I'm not very familiar with socket programming.
This is my first actual project I've worked on using sockets
"""


import socket
import threading as t
import pickle
from Crypto.Cipher import AES

class Server():
	def __init__(self, ip, port, maximum):
		self.IP = ip
		self.PORT = port
		self.MaxAllowedInSingleRoom = maximum
		self.rooms = {}
		self.s = socket.socket()
		self.s.bind((self.IP, self.PORT))
		self.s.listen(5)


	def main(self):
		conn, addr = self.s.accept()
		print(f"Got connected from {addr[0]} from port {addr}")
		x = conn.recv(1024)
		RM = self.decrypt(x)
		print(RM)
		self.assign_room(conn, RM)


	"""
	When encrypting, we want it to automatically change the encoding too
	So bytes <--> string
	We're using AES encryption
	NOTE: Currently the connection isn't end-to-end.
	I really should change this, but I cba.
	"""
	def encrypt(self, txt):
		obj = AES.new('gjdkflaprptlyfgk'.encode("utf8"), AES.MODE_CFB, 'aajfkgmfndkfpowe'.encode("utf8")) 
		ciphertext = obj.encrypt(pickle.dumps(txt))    
		return ciphertext

	def decrypt(self, ciphertext):
		try:
			obj = AES.new('gjdkflaprptlyfgk'.encode("utf8"), AES.MODE_CFB, 'aajfkgmfndkfpowe'.encode("utf8"))
			text = obj.decrypt(ciphertext)    
			txt = pickle.loads(text)
			return txt
		except Exception:
			return None


	def remove(self, conn, CurrentRoom):
		"""
		Before we start removing the inactive user
		we need to notify the active user(s) with additional information
		"""

		# First we need to figure out who the inactive user is
		clients_in_room = []
		for i in self.rooms.items():
			if i[1] == CurrentRoom:
				clients_in_room.append(i[0])		
						
		for idx, x in enumerate(clients_in_room):
			if x == conn:
				user = idx+1

		# Now that we have got the active user, let's remove him from the room
		del self.rooms[conn]


		# Ok now that there are only active users left, we need to notify them that somebody has disconnected
		# We also need to notify them their new username
		clients_in_room = []
		for i in self.rooms.items():
			if i[1] == CurrentRoom:
				clients_in_room.append(i[0])		
						

		for a in self.rooms.items():
			if a[1] == CurrentRoom:
				a[0].sendall(self.encrypt([f"User {user} has disconnected", None, 0]))

		for idx, x in enumerate(clients_in_room):
			x.sendall(self.encrypt([f"Your updated name is: {idx+1}", None, 0]))


	def listen(self, conn, CurrentRoom):
		while True:
			try:
				data = conn.recv(1024)
			except Exception:
				print("A client has been disconnected")
				self.remove(conn, CurrentRoom)
				return
				

			data = self.decrypt(data) # Current this is not end-to-end.
			if data == None:
				self.remove(conn, CurrentRoom)
				return

			# Ok we've got the data, cool, but now we need to find which room it has to go to
			# We can do this by checking which room belongs to the client, and sending the message 
			# to all the clients in the same room

			# We'll first get the room that matches the client that sent the message
			for idx, i in enumerate(self.rooms.items()):
				if i[0] == conn:
					ussr = idx+1 # This is the user our message originates from
					TargetRoom = i[1]
					break

			# Now that we know which room the message originated from
			# We can send the message to all of the other clients in the same room as well.
			clients_in_room = []
			for i in self.rooms.items():
				if i[1] == TargetRoom:
					clients_in_room.append(i[0])		
							

			# Here we send the actual messages
			for idx, x in enumerate(clients_in_room):
				x.sendall(self.encrypt((data[0], ussr, data[1]))) 


	def assign_room(self, conn, RoomNumber):
		dic = {conn : int(RoomNumber[0])} 
		num = 0
		for i in self.rooms.items():
			if i[1] == int(RoomNumber[0]):
				num += 1
				if num == self.MaxAllowedInSingleRoom:
					# So if the max amount of people in a single room has been reached, we want to send an "error" back
					# And disconnect the client from the server
					print("max amount in a room has been reached")
					conn.sendall(self.encrypt(["max_room", -1, 1])) # For some reason pickle decides to kill itself when I try to send back a tuple, not sure why
					conn.close() # We close the connection to our client
					return


		# So if the room we'r trying to enter is not full, we can enter the room
		self.rooms.update(dic)

		conn.sendall(self.encrypt([f"Succesfully joined room {RoomNumber[0]}", None, 0])) # The only reason the last argument is 0 is because we want this message to actuall show
		ListeningThread = t.Thread(target=self.listen, args=(conn, int(RoomNumber[0])))
		ListeningThread.start()



	

server = Server("localhost", 6969, 3)
while True:
	server.main()



