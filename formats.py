class Format:
	def __init__(self, value):
		self.tok = list(value)
		self.pos = -1
		self.cur = None
		self.next()

	def next(self):
		self.pos += 1
		if self.pos < len(self.tok):
			self.cur = self.tok[self.pos]
		else: self.cur = None

	def seive(self):
		count = 1; word = ''; self.next()
		while count != 0:
			if self.cur == '{': count+=1
			elif self.cur == '}':
				count-=1
				if count == 0: break
			word += self.cur
			self.next()
		return word

	def parse(self):
		sting = ''
		found = []
		while self.cur != None:
			if self.cur == '{':
				count = 0
				found.append(sting); sting = ''
				work = self.seive(); found.append([work])
			else:
				count = 1; sting += self.cur
			self.next()
		if count == 1: found.append(sting)

		return found

