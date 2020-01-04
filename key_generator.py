def key_generator(key):
		
		if key == 'яяя' or len(key)>3:
			raise StopAsyncIteration
		
		value = ''
		changed = False
		
		for number, symbol in enumerate(key[::-1], 1):
			if not changed:
				if symbol == 'я':
					if number == len(key):				
						if number == 3:
							#raise StopIteration
							raise StopAsyncIteration
						else:
							symbol = 'аа'
							changed = True
					else:
						symbol = 'а'
				else:	
					symbol = chr(ord(symbol)+1)
					changed = True
			value += symbol
		result = value[::-1]
		yield result
			
