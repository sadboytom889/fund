from linkedList import LinkedList;

class Queue ( LinkedList ):
	def __init__ ( self, size ):
		super().__init__();
		self.size = size;

	def enqueue ( self, data ):
		size = super().push( data );

		if size > self.size:
			super().shift();
