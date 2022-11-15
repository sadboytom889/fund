from enum import Enum, auto;

class Url ( object ):
	def __init__ ( self ):
		self.scheme = "";
		self.username = "";
		self.password = "";
		self.hostname = "";
		self.port = "";
		self.path = "";
		self.query = "";
		self.frag = "";

class State( Enum ):
	Scheme = auto();
	SlashAfterScheme1 = auto();
	SlashAfterScheme2 = auto();
	UsernameOrHostname = auto();
	PortOrPassword = auto();
	Hostname = auto();
	Password = auto();
	Port = auto();
	Path = auto();
	Query = auto();
	Fragment = auto();

class UrlParser ( object ):
	''' 解析: <scheme>://<username>:<password>@<host>:<port>/<path>?<query>#<frag>
		url = "http://username:password@host:80/path?query#frag";
		urlParser = UrlParser();
		urlParser.parse( url );
		print( "valid: ", urlParser.isValid() );
		print( "scheme: ", urlParser.scheme() );
		print( "username: ", urlParser.username() );
		print( "password: ", urlParser.password() );
		print( "hostname: ", urlParser.hostname() );
		print( "port: ", urlParser.port() );
		print( "path: ", urlParser.path() );
		print( "query: ", urlParser.query() );
		print( "fragment: ", urlParser.fragment() );
	'''
	def __init__ ( self ):
		self.__url = Url();
		self.__valid = False;

	def isValid ( self ):
		return self.__valid;

	def scheme ( self ):
		return self.__url.scheme;

	def username ( self ):
		return self.__url.username;

	def password ( self ):
		return self.__url.password;

	def hostname ( self ):
		return self.__url.hostname;

	def port ( self ):
		return self.__url.port;

	def path ( self ):
		return self.__url.path;

	def query ( self ):
		return self.__url.query;

	def fragment ( self ):
		return self.__url.frag;

	def parse ( self, url ):
		self.__parse( url );
		return self.isValid();

	def __isalnum ( self, char ):
		return char >= "a" and char <= "z" or char >= "A" and char <= "Z" or char >= "0" and char <= "9";

	def __isValidSchemeChar ( self, char ):
		return self.__isalnum( char ) or char == "+" or char == "-" or char == ".";

	def __isValidUsernameOrHostnameChar ( self, char ):
		return self.__isalnum( char ) or char == "-" or char == "." or char == "_" or char == "~" or char == "%";

	def __isValidPasswordChar ( self, char ):
		return self.__isalnum( char ) or char == "%";

	def __isValidPortChar ( self, char ):
		return char >= "0" and char <= "9";

	def __swap ( self, a, b ):
		return b, a;

	def __empty ( self, string ):
		return len( string ) == 0;

	def __parse( self, url ):
		
		self.__valid = True;
		self.__url.path = "/";

		schemeOrInvalidChar = "";
		passwordOrInvalidChar = "";
		usernameOrHostname = "";
		portOrPassword = "";

		i = 0;
		state = State.Scheme;

		while self.__valid == True and i < len( url ):

			if state == State.Scheme:
				if self.__isValidSchemeChar( url[ i ] ):
					schemeOrInvalidChar = schemeOrInvalidChar + url[ i ];

				elif url[ i ] == ":":
					state = State.SlashAfterScheme1;

				else:
					self.__valid = False;

			elif state == State.SlashAfterScheme1:
				if url[ i ] == "/":
					state = State.SlashAfterScheme2;

				elif self.__isalnum( url[ i ] ):
					state = State.UsernameOrHostname;
					usernameOrHostname = usernameOrHostname + url[ i ];
					self.__url.scheme, schemeOrInvalidChar = self.__swap( self.__url.scheme, schemeOrInvalidChar );

				else:
					self.__valid = False;

			elif state == State.SlashAfterScheme2:
				if url[ i ] == "/":
					state = State.UsernameOrHostname;
					self.__url.scheme, schemeOrInvalidChar = self.__swap( self.__url.scheme, schemeOrInvalidChar );

				else:
					self.__valid = False;

			elif state == State.UsernameOrHostname:
				if self.__isValidUsernameOrHostnameChar( url[ i ] ):
					usernameOrHostname = usernameOrHostname + url[ i ];

				elif url[ i ] == ":":
					state = State.PortOrPassword;

				elif url[ i ] == "@":
					state = State.Hostname;
					self.__url.username, usernameOrHostname = self.__swap( self.__url.username, usernameOrHostname );

				elif url[ i ] == "/":
					state = State.Path;
					self.__url.hostname, usernameOrHostname = self.__swap( self.__url.hostname, usernameOrHostname );

				elif url[ i ] == "?":
					state = State.Query;
					self.__url.hostname, usernameOrHostname = self.__swap( self.__url.hostname, usernameOrHostname );

				elif url[ i ] == "#":
					state = State.Fragment;
					self.__url.hostname, usernameOrHostname = self.__swap( self.__url.hostname, usernameOrHostname );

				else:
					self.__valid = False;

			elif state == State.PortOrPassword:
				if self.__isValidPortChar( url[ i ] ):
					portOrPassword = portOrPassword + url[ i ];

				elif self.__isValidPasswordChar( url[ i ] ):
					state = State.Password;
					portOrPassword = portOrPassword + url[ i ];
					self.__url.username, usernameOrHostname = self.__swap( self.__url.username, usernameOrHostname );
					passwordOrInvalidChar, portOrPassword = self.__swap( passwordOrInvalidChar, portOrPassword );

				elif url[ i ] == "/":
					state = State.Path;
					self.__url.hostname, usernameOrHostname = self.__swap( self.__url.hostname, usernameOrHostname );
					self.__url.port, portOrPassword = self.__swap( self.__url.port, portOrPassword );

				elif url[ i ] == "@":
					state = State.Hostname;
					self.__url.username, usernameOrHostname = self.__swap( self.__url.username, usernameOrHostname );
					self.__url.password, portOrPassword = self.__swap( self.__url.password, portOrPassword );

				else:
					self.__valid = False;

			elif state == State.Password:
				if self.__isValidPasswordChar( url[ i ] ):
					passwordOrInvalidChar = passwordOrInvalidChar + url[ i ];

				elif url[ i ] == "@":
					state = State.Hostname;
					self.__url.password, passwordOrInvalidChar = self.__swap( self.__url.password, passwordOrInvalidChar );

				else:
					self.__valid = False;

			elif state == State.Hostname:
				if self.__isValidUsernameOrHostnameChar( url[ i ] ):
					self.__url.hostname += url[ i ];

				elif url[ i ] == ":":
					state = State.Port;

				elif url[ i ] == "/":
					state = State.Path;

				else:
					self.__valid = False;

			elif state == State.Port:
				if self.__isValidPortChar( url[ i ] ):
					portOrPassword = portOrPassword + url[ i ];

				elif url[ i ] == "/":
				
					state = State.Path;
					self.__url.port, portOrPassword = self.__swap( self.__url.port, portOrPassword );

				else:
					self.__valid = False;

			elif state == State.Path:
				if url[ i ] == "#":
					state = State.Fragment;

				elif url[ i ] == "?":
					state = State.Query;

				else:
					self.__url.path = self.__url.path + url[ i ];

			elif state == State.Query:
				if url[ i ] == "#":
					state = State.Fragment;

				else:
					self.__url.query = self.__url.query + url[ i ];

			elif state == State.Fragment:
				self.__url.frag = self.__url.frag + url[ i ];

			else:
				self.__valid = False;

			i = i + 1;

		if not self.__empty( usernameOrHostname ):
			self.__url.hostname = usernameOrHostname;

		if not self.__empty( passwordOrInvalidChar ):
			self.__url.password = passwordOrInvalidChar;

		if not self.__empty( portOrPassword ):
			self.__url.port = portOrPassword;

		if self.__empty( self.__url.scheme ) or self.__empty( self.__url.hostname ) or self.__empty( self.__url.username ) and not self.__empty( self.__url.password ):
			self.__valid = False;
