class Node ( object ):
	def __init__ ( self, data ):
		self.data = data;
		self.prev = None;
		self.next = None;

class LinkedList ( object ):
	def __init__ ( self ):
		self.__head = None;
		self.__tail = None;
		self.__length = 0;

	def __searchNodeAt ( self, position ):

		if self.__length == 0 or position < 0 or position > self.__length - 1:
			raise IndexError;

		count = 0;
		node = self.__head;

		while count < position:
			node = node.next;
			count = count + 1;

		return node;

	def __insertAt ( self, position, data ):

		if position < 0 or position > self.__length:
			raise IndexError;

		node = Node( data );

		if position == 0:
			if self.__length == 0:
				self.__head = node;
				self.__tail = node;
			else:
				node.next = self.__head;
				self.__head.prev = node; 
				self.__head = node;

		elif position == self.__length:
			self.__tail.next = node;
			node.prev = self.__tail;
			self.__tail = node;

		else:
			prev = self.__searchNodeAt( position - 1 );
			node.next = prev.next;
			prev.next = node;
			node.next.prev = node;
			node.prev = prev;

		self.__length = self.__length + 1;

		return self.__length;

	def __removeAt ( self, position ):

		if self.__length == 0 or position < 0 or position > self.__length - 1:
			raise IndexError;

		node = self.__head;

		if position == 0:
			self.__head = self.__head.next;
			if self.__length == 1:
				self.__tail = None;
			else:
				self.__head.prev = None;

		elif position == self.__length - 1:
			node = self.__tail;
			self.__tail = self.__tail.prev;
			self.__tail.next = None;

		else:
			node = self.__searchNodeAt( position );
			node.prev.next = node.next;
			node.next.prev = node.prev;

		self.__length = self.__length - 1;

		return node;

	def size ( self ):
		return self.__length;

	def getHead ( self ):
		return self.__head;

	def getTail ( self ):
		return self.__tail;

	def push ( self, data ):
		return self.__insertAt( self.__length, data );

	def unshift ( self, data ):
		return self.__insertAt( 0, data );

	def pop ( self ):
		return self.__removeAt( self.__length - 1 );

	def shift ( self ):
		return self.__removeAt( 0 );

	def listPrint ( self ):
		count = 0;
		node = self.__head;

		if self.__length == 0:
			return None;

		else:
			while count < self.__length:
				print( node.data );
				node = node.next;
				count = count + 1;

	def tolist ( self ):
		array = [];
		count = 0;
		node = self.__head;

		while count < self.__length:
			array.append( node.data );
			node = node.next;
			count = count + 1;

		return array;
