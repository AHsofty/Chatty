import socket
import threading as t
import time
import pickle
import time
from Crypto.Cipher import AES

"""
Do I regret not making a class? YES

I kept adding stuff and things kept adding up, and now I have this :(

"""

#IP = '85.214.165.121'
IP = "localhost"
PORT = 6969
MaxAllowedInSingleRoom = 2

rooms = {}

s = socket.socket()
s.bind((IP, PORT))
s.listen(5)


"""
When encrypting, we want it to automatically change the encoding too
So bytes <--> string

We're using AES encryption

NOTE: Currently the connection isn't end-to-end. Fuck
"""
def encrypt(txt):
	obj = AES.new('You are a tosser'.encode("utf8"), AES.MODE_CFB, 'Aipom piplup 420'.encode("utf8"))
	ciphertext = obj.encrypt(pickle.dumps(txt))    
	return ciphertext

def decrypt(ciphertext):
	obj = AES.new('You are a tosser'.encode("utf8"), AES.MODE_CFB, 'Aipom piplup 420'.encode("utf8"))
	text = obj.decrypt(ciphertext)    
	txt = pickle.loads(text)
	return txt



def listen(conn, CurrentRoom):
	global rooms
	while True:
		try:
			data = conn.recv(1024)
		except Exception:
			print("A client has been disconnected")
			"""
			Before we start removing the inactive user
			And we need to notify the active user(s) with additional information

			I'll admit, this bit is a little messy. 
			I could've done this more efficiently by creating another function that does stuff
			But I didn't because I'm lazy, please don't kill me

			This bit needs optimization, but I CBA
			"""

			# First we need to figure out who the inactive user is

			clients_in_room = []
			for i in rooms.items():
				if i[1] == CurrentRoom:
					clients_in_room.append(i[0])		
							
			for idx, x in enumerate(clients_in_room):
				if x == conn:
					user = idx+1

			# Now that we have got the active user, let's remove him from the room
			del rooms[conn]

			# Now that we have kicked the inactive user, let's notify all of the active users that somebody disconnected
			# We now need to notify our current users' new name

			# Ok now that there are only active users left, we need to notify them that somebody has disconnected
			# We also need to notify them their new username
			clients_in_room = []
			for i in rooms.items():
				if i[1] == CurrentRoom:
					clients_in_room.append(i[0])		
							

			for UwU in rooms.items():
				if UwU[1] == CurrentRoom:
					UwU[0].sendall(encrypt([f"User {user} has disconnected", None, 0]))

			for idx, x in enumerate(clients_in_room):
				x.sendall(encrypt([f"Your updated name is: {idx+1}", None, 0]))
			return

		# ------------------------------------------------------------------------
		
		# If there is no error, we can continue
		data = decrypt(data) # Current this is not end-to-end. Make it so the messages are in the form of a list. [0] = message; [1] = author

		# Ok we've got the data, cool, but now we need to find which room is has to go to
		# We can do this by checking which room belongs to the client, and sending the message 
		# to all the clients in the same room

		# Q: Wouldn't it be better if we made a server class? A: Yes
		# Q: Then why aren't you doing that? A: LOL

		# We'll first get the room that matches the client that sent the message
		for i in rooms.items():
			if i[0] == conn:
				TargetRoom = i[1]
				break

		# Now that we know which room the message originated from
		# We can send the message to all of the other clients in the same room as well.

		clients_in_room = []
		for i in rooms.items():
			if i[1] == TargetRoom:
				clients_in_room.append(i[0])		
						

		for idx, x in enumerate(clients_in_room):
			x.sendall(encrypt((data[0], idx+1, data[1]))) 


def assign_room(conn, RoomNumber):
	global rooms
	global MaxAllowedInSingleRoom
	our_dick = {conn : int(RoomNumber[0])} # Yeah you read that variable name right
	num = 0
	for i in rooms.items():
		if i[1] == int(RoomNumber[0]):
			num += 1
			if num == MaxAllowedInSingleRoom:
				# So if the max amount of people in a single room has been reached, we want to send an error back
				# And disconnect the client from the server
				print("max amount in a room has been reached")
				conn.sendall(encrypt(["max_room", -1, 1])) # For some reason pickle decides to kill itself when I try to send back a tuple, not sure why
				conn.close() # We close the connection to our client
				return


	# So if the room we'r trying to enter is not full, we can enter the room
	rooms.update(our_dick)

	conn.sendall(encrypt([f"Succesfully joined room {RoomNumber[0]}", None, 0])) # The only reason the last argument is 0 is because we want this message to actuall show
	ListeningThread = t.Thread(target=listen, args=(conn, int(RoomNumber[0])))
	ListeningThread.start()



	


while True:
	conn, addr = s.accept()
	print(f"Got connected from {addr[0]} from port {addr}")

	x = conn.recv(1024)
	RM = decrypt(x)
	print(RM)
	
	assign_room(conn, RM)




