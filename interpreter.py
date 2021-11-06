from lexer import Lexer, Token
from formats import Format
from binascii import hexlify
import random, os
import importlib, json
import time, re, sys


sys.path.insert(1, 'lib')

class BinOp:
	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right

	def __repr__(self):
		return f'({self.left} {self.op} {self.right})'

class Num:
	def __init__(self, token):
		self.value = token

	def __repr__(self):
		return f'{self.value}'

class Traceback_:
	def __init__(self, line, file, module):
		self.line = line
		self.file = file
		self.module = module

	def __repr__(self):
		return f'{self.line}: {self.file} -> {self.module}'

class Pparser:
	def __init__(self, code, bin, args, bolt='true', mode='function', name='__main__', obj='function', file_='stdin'):
		self.code = code
		self.bin = bin
		self.args = args
		self.pos = -1
		self.evaled = ''
		self.bolt = bolt
		self.obj = obj
		self.file = file_
		self.traceback = []
		self.count = 0
		self.tok = None
		self.tokens = self.code
		self.return_value = 0
		self.result = ['true', 'false', self.return_value]
		self.bool_ = 'false'
		self.mode = mode
		self.name = name
		self.libs()
		self.toks()
		self.next()
		self.parse()
		self.objector()

	def toks(self):
		if type(self.code) == list:
			self.tokens = self.code
		else:
			self.tokens = Lexer(self.code, self.file).tokens

	def libs(self):
		self.scope = self.bin[0]
		self.scopekeys = list(self.scope.keys())

		if type(self.args) == list:
			self.var_set = {'null'}
			self.var_dict = {'null': None}
			self.fn_set = {'episode_'}
			self.fn_dict = {}
			self.const_set = {'Jesus is Lord.', 'null'}
			self.imports = {}

			self.const_set = self.const_set.union(self.bin[5])
			self.imports.update(self.bin[6])

			self.thisvar_set = {'null'}
			self.thisvar_dict = {'null': None}
			self.thisfn_set = {'episode_'}
			self.thisfn_dict = {}

			count = -1
			for i in self.args[1]:
				count += 1
				self.var_set.add(i)
				self.var_dict[i] = self.args[0][count]

			self.var_set = self.var_set.union(self.bin[1])
			self.var_dict.update(self.bin[2])
			self.fn_set = self.fn_set.union(self.bin[3])
			self.fn_dict.update(self.bin[4])
		else:
			self.var_set = self.bin[1]
			self.var_dict = self.bin[2]
			self.fn_set = self.bin[3]
			self.fn_dict = self.bin[4]
			self.const_set = self.bin[5]
			self.imports = self.bin[6]

			self.thisvar_set = self.bin[7]
			self.thisvar_dict = self.bin[8]
			self.thisfn_set = self.bin[9]
			self.thisfn_dict = self.bin[10]

		try:
			self.traceback.extend(self.bin[11])
		except:
			pass

	# errors
	def NameError(self, char, line, file):
		
		print('Traceback (most recent call last):')
		file_ = file.split('/')[-1]
		print(f'  File "{file_}", line {line}, in <{self.name}>')
		if os.path.exists(file):
			data = open(file, 'r').readlines()[line-1].rstrip('\n')
			data = data.lstrip(' ')
			data = data.lstrip('\t')
			print(f'      {data}\n')
		print(f"NameError: '{char}' is not defined")

		for i in self.traceback:
			print(f'   at {i.module} "{i.file}" -> {i.line})')
			data = open(i.file, 'r').readlines()[i.line-1].rstrip('\n')

			data = data.lstrip(' ')
			data = data.lstrip('\t')
			print(f'      {data}')

		quit()

	def InvalidSyntaxError(self, char, line, file):
		print('Traceback (most recent call last):')
		file_ = file.split('/')[-1]
		print(f'  File "{file_}", line {line}, in <{self.name}>')
		if os.path.exists(file):
			data = open(file, 'r').readlines()[line-1].rstrip('\n')
			data = data.lstrip(' ')
			data = data.lstrip('\t')
			print(f'      {data}\n')
		else:
			data = self.code.lstrip(' ')
			data = data.lstrip('\t')
			print(f'      {data}\n')
		print(f"SyntaxError: given invalid syntax.")

		for i in self.traceback:
			print(f'   at {i.module} "{i.file}" -> {i.line})')
			data = open(i.file, 'r').readlines()[i.line-1].rstrip('\n')

			data = data.lstrip(' ')
			data = data.lstrip('\t')
			print(f'      {data}')
		quit()

	def ArgumentError(self, char, line, file, exp, got, attr, args):
		print('Traceback (most recent call last):')
		file_ = file.split('/')[-1]
		print(f'  File "{file_}", line {line}, in <{self.name}>')
		if os.path.exists(file):
			data = open(file, 'r').readlines()[line-1].rstrip('\n')
			data = data.lstrip(' ')
			data = data.lstrip('\t')
			print(f'ls      {data}\n')

		if exp > got:
			index = attr[-(exp - got):]
			attr_ = ''
			for i in index:
				attr_ += f'{i}, '

			print(f"ArgumentError: expected {exp} arguments but given {got}")
			print(f'    missing arguments: {attr_}')
		else:
			print(f'ArgumentError: method takes {exp} arguments but given {got}')

		for i in self.traceback:
			print(f'  at {i.module} "{i.file}" -> {i.line})')
			data = open(i.file, 'r').readlines()[i.line-1].rstrip('\n')

			data = data.lstrip(' ')
			data = data.lstrip('\t')
			print(f'      {data}')
		quit()

	# end errors
	def drawft(self):
		atrs = ['__attr__', '__className__', '__obj__'] + list(self.thisvar_set)
		self.thissave('__attr__', atrs)
		self.thissave('__className__', self.name)
		contents = {}
		contents['__className__'] = self.name
		tis = list(self.thisvar_set)
		
		for i in tis:
			try: contents[i] = self.thisfn_dict[i]
			except:
				if i == '__attr__':
					contents[i] = self.thisvar_dict[i][:2]
				else:
					contents[i] = self.thisvar_dict[i]
		self.thissave('__obj__', contents)

	def thissave(self, name, value):
		self.thisvar_set.add(name)
		self.thisvar_dict[name] = value

	def Objthissave(self, name, value):
		self.obj.var_set.add(name)
		self.obj.var_dict[name] = value

	def thissaveDICT(self, name, value):
		self.thisfn_set.add(name)
		self.thisfn_dict[name] = value

	def syntaxerror(self, description):
		print(f'\n  File "stdin.dr", line {self.tok.line} FUNCTION <{self.bin[-1]}>')
		quit()

	# creates the objects
	def Elements(self, name_, var_set_, var_dict_, fn_set_, fn_dict_, mode='func'):
		class Base:
			def __init__(self, name, var_set, var_dict, fn_set, fn_dict, mode_):
				self.name = name
				self.var_set = var_set
				self.var_dict = var_dict
				self.fn_set = fn_set
				self.fn_dict = fn_dict
				self.mode = mode_

			def __repr__(self):
				ans = self.name.split(' ')[1]
				return f'<__object__ {ans} at 0x{str(hexlify(os.urandom(14)).decode())[:12]}>'

		return Base(name_, var_set_, var_dict_, fn_set_, fn_dict_, mode)

	# Importing file
	def Importer(self, name_, var_set_, var_dict_, fn_set_, fn_dict_, const):
		class Base:
			def __init__(self, name, var_set, var_dict, fn_set, fn_dict, const_):
				self.name = name
				self.var_set = var_set
				self.var_dict = var_dict
				self.fn_set = fn_set
				self.fn_dict = fn_dict
				self.const_set = const_

			def __repr__(self):
				return f'<Import {self.name} at 0x{str(hexlify(os.urandom(14)).decode())[:12]}>'

		return Base(name_, var_set_, var_dict_, fn_set_, fn_dict_, const)

	def save(self, name, value):
		if name in self.const_set:
			print('Identifier already assigned as a variable'); quit()
		else:
			self.var_set.add(name)
			self.var_dict[name] = value

	def classsave(self, name, value):
		if name in self.const_set:
			print('Identifier already assigned as a variable'); quit()
		else:
			self.class_var_set.add(name)
			self.class_var_dict[name] = value

	def classDICT(self, name, value):
		if name in self.const_set:
			print('Identifier already assigned as a variable'); quit()
		else:
			self.class_fn_set.add(name)
			self.class_fn_dict[name] = value

	# clearing memory
	def gabbage(self, name):
		if name in self.var_set:
			try:
				self.var_set.remove(name)
				vault = self.var_dict.pop(name)

				if vault in self.fn_set:
					self.fn_set.remove(vault)
					self.fn_dict.pop(vault)
			except:
				pass

		elif name in self.fn_set:
			try:
				if name in self.fn_set:
					self.fn_set.remove(name)
					self.fn_dict.pop(name)
			except:
				pass

	# saving functions
	def saveDICT(self, name, value):
		if name in self.const_set:
			print('Identifier already assigned as a variable'); quit()
		else:
			self.fn_set.add(name)
			self.fn_dict[name] = value

	# collect function in scope or objects
	def thismethod(self, name='var'):
		if self.tok.type == 'LEFT_PAREN':
			self.next()
			dicti = {}

			while self.tok.type != 'RIGHT_PAREN':
				if self.tok.type == 'IDENTIFIER':
					key = self.tok.value
					self.next()

					if self.tok.type in ['COMMA', 'RIGHT_PAREN']:
						dicti[key] = f'empty__'
						if self.tok.type == 'COMMA':
							self.next()

					elif self.tok.type == 'ASSIGN':
						self.next()
						value = self.Collect2(['COMMA', 'RIGHT_PAREN'])
						dicti[key] = value
						
						if self.tok.type in ['COMMA', 'NEWLINE']:
							self.next()
			self.next()

			while self.tok.type == 'NEWLINE':
				self.next()
			
			if self.tok.type == 'LEFT_BRACKET':
				self.next()
				count = 1
				code = []

				while count != 0:
					if self.tok.type == 'LEFT_BRACKET':
						count += 1
					elif self.tok.type == 'RIGHT_BRACKET':
						count -= 1
						if count == 0:
							break
					code.append(self.tok)
					self.next()
			self.next()

			ans = self.name.split(' ')[1]
			location = f'<function {name} at __{ans}__>'

			self.thissave(name, location)
			self.thissaveDICT(location, [dicti, code])
			return location	

	# collects the scope to a datatable
	def bins(self):
		# sharing the scopes
		return [self.scope, self.var_set, self.var_dict, self.fn_set, self.fn_dict, self.const_set, self.imports, self.thisvar_set, self.thisvar_dict, self.thisfn_set, self.thisfn_dict, self.traceback]

	# library scope
	def Importbins(self, obj):
		# giving back scope
		return [obj.var_set, obj.var_dict, obj.fn_set, obj.fn_dict, obj.const_set, self.imports, self.thisvar_set, self.thisvar_dict, self.thisfn_set, self.thisfn_dict]

	# importing from direct or python
	def imported(self):
		if self.tok.type == 'IDENTIFIER':
			module = self.tok.value
			self.next()
			if self.tok.type == 'FROM':
				self.next()
			else:
				mod = importlib.import_module(module)

				while self.tok.type == 'DOT':
					self.next()
					if self.tok.type == 'IDENTIFIER':
						module += f'.{self.tok.value}'
						mod = getattr(mod, self.tok.value)
						self.next()
					else:
						print('expected and Identifer')
						quit()

				if self.tok.type == 'AS':
					self.next()
					new_name = self.tok.value
					self.next()
				else:
					new_name = module

				lib = f'<__lib__.{module} id 0x{str(hexlify(os.urandom(12)).decode()[:12])}>'
				self.save(new_name, lib)
				self.saveDICT(lib, mod)

		elif self.tok.type == 'LEFT_BRACKET':
			self.next()
			imt = []
			while self.tok.type != 'RIGHT_BRACKET':
				if self.tok.type == 'IDENTIFIER':
					imt.append(self.tok.value)
				self.next()
			self.next()

			if self.tok.type in ['FROM', 'LOCATE']:
				self.next()
				path = self.Collect(['NEWLINE', 'END_STAT'])
				
				if not path.endswith('.dr'):
					path = path+'.dr'

				src_code = Lexer(open(path, 'r').read(), path).tokens
				lib_ = Pparser(src_code, self.bins(), [[], []], 'true', 'import', path).return_value

				for i in imt:
					self.save(i, lib_.var_dict[i])
			else:
				print('please enter file path')
				quit()
		
		elif self.tok.type == 'STRING':
			file = self.tok.value + '.dr'
			self.next()

			if self.tok.type in ['FROM', 'LOCATE']:
				self.next()
				catch = self.Collect(['NEWLINE', 'END_STAT'])
				path = os.path.join(catch, file)
			else:
				path = file

			code = open(path, 'r').read()
			Pparser(code, self.bins(), 'includes', bolt='true', mode='function', name='__main__', obj='function', file_=path)
		
		else:
			print('import not found'); quit()

	def exec(self, codes, cidic):
		class Eparser(Pparser):
			def __init__(self, *args, **kwargs):
			    super(Eparser, self).__init__(*args, **kwargs)

			def libs(self):
				self.var_set = self.bin[0]
				self.var_dict = self.bin[1]
				self.fn_set = self.bin[2]
				self.fn_dict = self.bin[3]
				self.const_set = self.bin[4]
				self.imports = self.bin[5]
		return Eparser(codes, cidic, []).bool_

	def execloop(self, codes, cidic):
		class Eparser(Pparser):
			def __init__(self, *args, **kwargs):
			    super(Eparser, self).__init__(*args, **kwargs)

			def libs(self):
				self.var_set = self.bin[0]
				self.var_dict = self.bin[1]
				self.fn_set = self.bin[2]
				self.fn_dict = self.bin[3]
				self.const_set = self.bin[4]
				self.imports = self.bin[5]

				self.thisvar_set = self.bin[6]
				self.thisvar_dict = self.bin[7]
				self.thisfn_set = self.bin[8]
				self.thisfn_dict = self.bin[9]

		return Eparser(codes, cidic, []).result

	def execval(self, codes, cidic):
		class Eparser(Pparser):
			def __init__(self, *args, **kwargs):
			    super(Eparser, self).__init__(*args, **kwargs)

			def libs(self):
				self.var_set = self.bin[0]
				self.var_dict = self.bin[1]
				self.fn_set = self.bin[2]
				self.fn_dict = self.bin[3]
				self.const_set = self.bin[4]
				self.imports = self.bin[5]

				self.thisvar_set = self.bin[6]
				self.thisvar_dict = self.bin[7]
				self.thisfn_set = self.bin[8]
				self.thisfn_dict = self.bin[9]
		return Eparser(codes, cidic, [])

	def next(self):
		self.pos += 1
		if self.pos < len(self.tokens):
			self.tok = self.tokens[self.pos]
		else:
			self.tok = None

	def pre(self):
		self.pos -= 1
		self.tok = self.tokens[self.pos]

	# saving constant variables 
	def saveconst(self, name, value):
		if name in self.const_set:
			print('Identifier already assigned as a variable'); quit()
		else:
			self.const_set.add(name)
			self.var_set.add(name)
			self.var_dict[name] = value

	def handleModule(self, module, idn):
		self.next()
		if self.tok.type in ['NEWLINE', 'END_STAT']:
			self.pre()
			return f'<module {imports[module]} "lib/builtins/drandom.py">'
		elif self.tok.type == 'DOT':
			self.next()
			attr = self.tok.value
			self.next()

			if self.tok.type == 'LEFT_PAREN':
				self.next()
				args = []

				while self.tok.type != 'RIGHT_PAREN':
					collect = self.Collect2(['COMMA', 'RIGHT_PAREN'])
					args.append(collect)
					if self.tok.type == 'COMMA':
						self.next()
					elif self.tok.type == 'RIGHT_PAREN':
						pass
			else:
				self.pre()
				args = []

			ans = Sort(self.imports[module], [attr, args], idn, self.bins).return_value
			return ans

	def modulize(self, attr, idn):
		attribute = self.tok.value; self.next()
		module = attr.split(" ")
		locate = module[-1].strip('>')
		module = module[0].split("<module*")[-1]

		if self.tok.type == 'LEFT_PAREN':
			self.next(); args = []

			while self.tok.type != 'RIGHT_PAREN':
				collect = self.Collect2(['COMMA', 'RIGHT_PAREN'])
				args.append(collect)

				if self.tok.type == 'COMMA':
					self.next()
				elif self.tok.type == 'RIGHT_PAREN':
					pass
			self.next()
		else:
			self.pre()
			args = []

		ans = Sort(module, [locate, [attribute, args]], idn).return_value

		if type(ans) == tuple:
			ans = list(ans) 
		return ans

	# sorting class code
	def classic(self):
		cl_name = self.tok.value
		self.next()

		if self.tok.type == 'EXTENDS':
			self.next()
			class_name = self.tok.value
			cl_ = self.Collect2(['NEWLINE', 'LEFT_BRACKET', 'END_STAT'])
			value = cl_.split(' ')[1]
			code = self.fn_dict[self.var_dict[value]]
			object1 = Pparser(code, self.bins(), [[], []], 'true', 'class', value).return_value
			
			while self.tok.type == 'NEWLINE': self.next()

			if self.tok.type == 'LEFT_BRACKET': self.next()

			count = 1; code = []
			while count != 0:
				if self.tok.type == 'LEFT_BRACKET':
					count += 1
				elif self.tok.type == 'RIGHT_BRACKET':
					count -= 1
					if count == 0:
						break

				code.append(self.tok); self.next()
			self.next()

			object2 = Pparser(code, self.bins(), [[], []], 'true', 'class', value).return_value

			var_set = set(); var_dict = {}; fn_set=set(); fn_dict = {}

			var_set = var_set.union(object1.var_set); var_dict.update(object1.var_dict)
			fn_set = fn_set.union(object1.fn_set); fn_dict.update(object1.fn_dict)

			var_set = var_set.union(object2.var_set); var_dict.update(object2.var_dict)
			fn_set = fn_set.union(object2.fn_set); fn_dict.update(object2.fn_dict)

			object2.var_set.clear(); object2.var_dict.clear()
			object2.fn_set.clear(); object2.fn_dict.clear()

			object2.var_set = object2.var_set.union(var_set); object2.var_dict.update(var_dict)
			object2.fn_set = object2.fn_set.union(fn_set); object2.fn_dict.update(fn_dict)

			locate = f'<Ext.extends {class_name}~{cl_name} at 0x{hexlify(os.urandom(4)).decode()}>'
			self.save(cl_name, locate)
			self.saveDICT(locate, object2)

		else:
			while self.tok.type == 'NEWLINE':
				self.next()

			if self.tok.type == 'LEFT_BRACKET':
				self.next()
			else:
				self.InvalidSyntaxError(self.tok.value, self.tok.line, self.tok.file)

			count = 1
			code = []
			while count != 0:
				if self.tok.type == 'LEFT_BRACKET':
					count += 1
				elif self.tok.type == 'RIGHT_BRACKET':
					count -= 1
					if count == 0:
						break

				code.append(self.tok); self.next()
			self.next()

			nim = f'<class {cl_name} at 0x{str(hexlify(os.urandom(14)).decode()[:12])}>'
			while nim in self.scopekeys:
				nim = f'<class {cl_name} at 0x{str(hexlify(os.urandom(14)).decode()[:12])}>'

			self.save(cl_name, nim)
			self.saveDICT(nim, code)
			self.scope[nim] = [code, self.bins()]

	def extreme(self, value, inherit=False):
		args = {}; count = 1

		if inherit == True:
			act = self.fn_dict[value]
		else:
			code = self.fn_dict[self.var_dict[value]]
			act = Pparser(code, self.bins(), [[], []], 'true', 'class', value).return_value

		while self.tok.type != 'RIGHT_PAREN':
			if self.tok.type == 'IDENTIFIER' and self.tok.value not in self.var_set:
				key = self.tok.value; self.next()

				if self.tok.type in ['COMMA', 'RIGHT_PAREN']:
					args[key] = f'empty__'
					if self.tok.type == 'COMMA': self.next()

				elif self.tok.type == 'ASSIGN':
					self.next()
					value = self.Collect2(['COMMA', 'RIGHT_PAREN'])
					args[key] = value
						
					if self.tok.type in ['COMMA', 'NEWLINE']: self.next()
			else:
				val = self.Collect2(['COMMA', 'NEWLINE', 'RIGHT_PAREN'])
				args[f'null_{count}'] = val

				if self.tok.type in ['COMMA', 'NEWLINE']:
					self.next()
				count += 1

		self.next()
		obj = act
		public = obj.fn_set

		fn = 'notfound notfound'

		for i in public:
			if i.startswith('<function public'):
				fn = obj.fn_dict[i]
				break

		if fn == 'notfound notfound':
			saves = str(obj).split(' ')
			new = saves[0] + '.'; saves.pop(0); saves.insert(0, new); saves = ' '.join(saves)
			self.fn_set.add(saves)
			self.fn_dict[saves] = obj
			return saves
		else:
			ments = fn[0]; count = 0
			for i in ments:
				if i in args.keys(): ments[i] = args[i]
				elif count < len(args) and list(args.keys())[count].startswith('null_'):
					ments[i] = args[list(args.keys())[count]]; count += 1

			for i in ments:
				if ments[i] == 'empty__': print(f' Expected {len(ments)} arguments given {len(args)}\n  at function {value}'); quit()
				else: pass

			code = fn[1]
			final = Pcparser(obj, code, self.bins(), [list(ments.values()), list(ments.keys())]).obj
			saves = str(final).split(' ')

			new = saves[0] + '.'; saves.pop(0); saves.insert(0, new); saves = ' '.join(saves)
			self.saveDICT(saves, final)
			return saves

	def formator(self, value):
		new_ = ''; l = Format(value).parse()
		
		for i in l:
			if type(i) == list:
				lexed = Lexer(i[0]).tokens
				lexed.insert(0, Token('GETBACK', self.tok.line))
				lexed.append(Token('NEWLINE', self.tok.line))
				ans = Pparser(lexed, self.bins(), 'formatted string').evaled
				new_ += f'{ans}'
			else:
				new_ += i

		return new_

	def lambdaa(self):
		self.next()
		if self.tok.type in ['ARROW', 'COLON']:
			self.next()
		else:
			print('wrong snytax expected ->'); quit()
		
		value = self.tok.value
		self.next()
		if self.tok.type == 'LEFT_PAREN':
			self.next()

		locate = self.var_dict[value]
		args = {}
		count = 1

		while self.tok.type != 'RIGHT_PAREN':
			if self.tok.type == 'IDENTIFIER' and self.tok.value not in var_set:
				key = self.tok.value
				self.next()

				if self.tok.type in ['COMMA', 'RIGHT_PAREN']:
					args[key] = f'empty__'
					if self.tok.type == 'COMMA': self.next()

				elif self.tok.type == 'ASSIGN':
					self.next()
					value = self.Collect2(['COMMA', 'RIGHT_PAREN'])
					args[key] = value
						
					if self.tok.type in ['COMMA', 'NEWLINE']: self.next()
			else:
				val = self.Collect2(['COMMA', 'NEWLINE', 'RIGHT_PAREN'])
				args[f'null_{count}'] = val
				if self.tok.type in ['COMMA', 'NEWLINE']: self.next()
				count += 1

		self.next();

		ments = {}
		ments.update(self.scope[locate][0])

		count = 0
		for i in ments:
			if i in args.keys(): ments[i] = args[i]
			elif count < len(args) and list(args.keys())[count].startswith('null_'):
				ments[i] = args[list(args.keys())[count]]; count += 1

		for i in ments:
			if ments[i] == 'empty__': print(f' Expected {len(ments)} arguments given {len(args)}\n  at function {value}'); quit()
			else: pass

		code = self.scope[locate][1]
		self.pre()
		return lambda:Pparser(code, self.bins() + [value], [list(ments.values()), list(ments.keys())])

	def evalor(self):
		self.next()
		if self.tok.type == 'LEFT_PAREN': self.next()
		codes = self.Collect(['RIGHT_PAREN'])
		lexed = Lexer(codes).tokens
		lexed.insert(0, Token('GETBACK', self.tok.line)); lexed.append(Token('NEWLINE', self.tok.line))
		return Pparser(lexed, self.bins(), [[], []]).evaled

	# creating a lambda function from variable
	def lambdaFunc(self):
		self.next()
		if self.tok.type == 'LEFT_PAREN': self.next(); self.next()
		
		if self.tok.type == 'ARROW':
			self.next()

			if self.tok.type == 'LEFT_BRACKET':
				self.next(); count = 1; code = []
				while count != 0:
					if self.tok.type == 'LEFT_BRACKET': count += 1
					elif self.tok.type == 'RIGHT_BRACKET':
						count -= 1
						if count == 0: break
					code.append(self.tok)
					self.next()
				self.next()
			else:
				print('function code name')
				quit()
			return lambda:Pparser(code, self.bins()+['lambda'], [[], []]).return_value

		else:
			print('point to task code with and arrow')
			quit()

	def enter(self):
		self.next()
		if self.tok.type == 'LEFT_PAREN': self.next()
		if self.tok.type == 'RIGHT_PAREN': pass
		else: pre = self.Collect(['RIGHT_PAREN']); print(pre, end='')
		value = input()
		return value

	def execu(self, value):
		self.next()
		return value()

	def getargs(self):
		self.next()
		arguments = []; count = 1

		while self.tok.type != 'RIGHT_PAREN':
			arguments.append(self.Collect(['COMMA', 'RIGHT_PAREN']))
			if self.tok.type == 'RIGHT_PAREN': pass
			else: self.next()
			if self.tok.type == 'COMMA': self.next()

		self.next();

		return tuple(arguments)


	# FUNCTION CALLING AND DEFINING
	def method(self, name='var'):
		if self.tok.type == 'LEFT_PAREN':
			self.next()
			dicti = {}

			while self.tok.type != 'RIGHT_PAREN':
				if self.tok.type == 'IDENTIFIER':
					key = self.tok.value; self.next()
					if self.tok.type in ['COMMA', 'RIGHT_PAREN']:
						dicti[key] = f'empty__'
						if self.tok.type == 'COMMA': self.next()
					elif self.tok.type == 'ASSIGN':
						self.next()
						value = self.Collect2(['COMMA', 'RIGHT_PAREN'])
						dicti[key] = value
						
						if self.tok.type in ['COMMA', 'NEWLINE']: self.next()
			self.next()
			
			if self.tok.type == 'LEFT_BRACKET':
				self.next()
				count = 1
				code = []

				while count != 0:
					if self.tok.type == 'LEFT_BRACKET':
						count += 1
					elif self.tok.type == 'RIGHT_BRACKET':
						count -= 1
						if count == 0:
							break

					code.append(self.tok)
					self.next()

			self.next()
			location = f'<function {name} at 0x{str(hexlify(os.urandom(14)).decode()[1:12])}>'
			self.save(name, location)
			self.scope[location] = [dicti, code, self.bins()]
			return location

	def called(self, value, args):
		code_ = self.scope[value]
		ments = {}
		ments.update(code_[0])

		ments = self.checker(ments, args, value)
		code = code_[1]
		module = value.split(' ')[1]

		return Pparser(code, code_[2], [list(ments.values()), list(ments.keys())], bolt='true', mode='function', name=module).return_value


	def checkself(self):
		self.next()
		if self.tok.type == 'DOT':
			self.next()
			capt = self.tok.value

			if capt in self.obj.var_set:
				value = self.obj.var_dict[capt]

				if str(value).startswith('<function '):
					self.next()

					if self.tok.type == 'LEFT_PAREN':
						self.next()
						ans = self.selfMethod(value)
						self.pre()
						return ans
					else:
						locate = f'<local method {capt} of {self.obj}>'
						self.scope[locate] = [self.obj, self.bins(), value]
						self.pre()
						return locate
				else:
					return value
			else:
				pass
		else:
			self.InvalidSyntaxError(self.tok.value, self.tok.line, self.tok.file)

	def calledClassfunc(self, value, cur):
		codes_ = self.scope[value]
		obj = codes_[0]
		
		if self.tok.type != 'LEFT_PAREN':
			if cur in obj.var_set:
				ans = obj.var_dict[cur]
				
				if self.tok.type == 'ASSIGN':
					self.next()
					val = self.Collect(['NEWLINE', 'END_STAT'])
					obj.var_dict[cur] = val
					return None

				elif self.tok.type == 'DOT':
					return self.handleDot(ans)

				else:
					if type(ans) == str and ans in obj.fn_set:
						call = value.split(' ')[1]
						locate = f'<method {call}.{cur} of {value}>'
						self.scope[locate] = [ans, obj, codes_[1]]
						return locate
					else:
						return ans
			else:
				pass
		else:
			cur = obj.var_dict[cur]
			if cur in obj.fn_dict.keys():
				self.next()

				args = self.callargs()
				fn = obj.fn_dict[cur]

				ments = fn[0]
				ments = self.checker(ments, args, value)
				
				code = fn[1]
				module = value.split(' ')[1] + '.' + cur.split(' ')[1]

				arg_ = [list(ments.values()), list(ments.keys())]
				return Pparser(code, codes_[1], arg_, 'true', 'function', module, obj, True).return_value
			else:
				return self.callfunction(cur)

	def calledClassMethod(self, value, args):
		codes_ = self.scope[value]
		obj = codes_[1]
		fn = obj.fn_dict[codes_[0]]

		ments = fn[0]
		ments = self.checker(ments, args, value)

		code = fn[1]
		arg_ = [list(ments.values()), list(ments.keys())]
		return Pparser(code, codes_[2], arg_, 'true', 'function', '__main__', obj, True).return_value

	def selfMethod(self, value):
		args = self.callargs()
		obj = self.obj
		fn = obj.fn_dict[value]

		ments = fn[0]
		ments = self.checker(ments, args, value)

		code = fn[1]
		arg_ = [list(ments.values()), list(ments.keys())]

		final = Pparser(code, self.bins(), arg_, 'true', 'function', '__main__', obj, True).return_value
		return final

	def selfScopeMethod(self, value, args):
		codes_ = self.scope[value]
		obj = codes_[0]
		fn = obj.fn_dict[codes_[2]]

		ments = fn[0]
		ments = self.checker(ments, args, value)

		code = fn[1]
		arg_ = [list(ments.values()), list(ments.keys())]

		final = Pparser(code, codes_[1], arg_, 'true', 'function', '__main__', obj, True).return_value
		return final


	def structer(self):
		name = self.tok.value
		self.next()

		while self.tok.type == 'NEWLINE': self.next()

		if self.tok.type == 'LEFT_BRACKET':
			self.next()
			tokens = []
			COUNT=1

			while COUNT != 0:
				if self.tok.type == 'LEFT_BRACKET':
					COUNT+=1
				elif self.tok.type == 'RIGHT_BRACKET':
					COUNT-=1
					if COUNT == 0:
						break

				tokens.append(self.tok)
				self.next()

			tokens.insert(0, Token('STRU', self.tok.line))
			tokens.append(Token('RIGHT_BRACKET', self.tok.line, '}'))
			self.next()

			locate = str(hexlify(os.urandom(14)).decode()[:12])
			saved = f'<Struct {name} at 0x{locate}>'
			self.save(name, saved)
			self.scope[saved] = [tokens, self.bins()]
		
		elif self.tok.type == 'IDENTIFIER':
			label = self.tok.value
			codes_ = self.scope[self.var_dict[name]]
			code = codes_[0]
			scope = codes_[1]

			locate = str(hexlify(os.urandom(12)).decode()[:12])
			ans = Pparser(code, scope, [[],[]], 'true', 'function', '__main__', 'struct', True).evaled
			
			class Struct:
				def __init__(self):
					self.arg = ans

				def __repr__(self):
					return f'<__struct__.{name}.{label} at 0x{locate}>'

			cl = Struct()
			self.save(label, str(cl))
			self.scope[str(cl)] = [cl]

		elif self.tok.type == 'LEFT_PAREN':
			self.next()
			lit = []

			while self.tok.type != 'RIGHT_PAREN':
				while self.tok.type == 'NEWLINE': self.next()

				args = self.Collect(['COMMA', 'NEWLINE', 'RIGHT_PAREN'])
				lit.append(args)

				if self.tok.type in ['NEWLINE', 'COMMA']:
					self.next()

				while self.tok.type == 'NEWLINE': self.next()

			label = tuple(lit)
			codes_ = self.scope[self.var_dict[name]]

			code = codes_[0]
			scope = codes_[1]

			nim = f'<__struct__.{name} at 0x{str(hexlify(os.urandom(12)).decode()[:12])}>'


			while nim in self.scope.keys():
				nim = f'<__struct__.{name} at 0x{str(hexlify(os.urandom(12)).decode()[:12])}>'
			
			ans = Pparser(code, scope, [[],[]], 'true', 'function', '__main__', 'struct', True).evaled

			class Struct:
				def __init__(self):
					self.arg = ans

				def __repr__(self):
					return nim

			cl = Struct()

			for i in range(len(lit)):
				cl.arg[list(cl.arg.keys())[i]] = lit[i]

			self.save(label, str(cl))
			self.scope[str(cl)] = [cl]
			return str(cl)

	def parserStruct(self, value, cur):
		struct = self.scope[value][0]

		if cur in struct.arg.keys():
			if self.tok.type == 'ASSIGN':
				self.next()
				val = self.Collect(['NEWLINE', 'END_STAT'])
				struct.arg[cur] = val
			else:
				return struct.arg[cur]
		else:
			print('No a struct attribute')
			quit()





	# calling library objects
	def calledLibrary(self, value, cur):
		obj = self.fn_dict[value][0]
		scope = self.fn_dict[value][1]
		
		if self.tok.type != 'LEFT_PAREN':
			if cur in obj.var_set:
				ans = obj.var_dict[cur]
				
				if self.tok.type == 'ASSIGN':
					self.next(); val = self.Collect(['NEWLINE', 'END_STAT'])
					obj.var_dict[cur] = val
					return None
				elif self.tok.type == 'DOT':
					return self.handleDot(ans)
				else:
					if type(ans) == str and ans in obj.fn_set:
						call = value.split(' ')[1]
						self.saveDICT(f'<callback cflibrary {call}.{cur} {value}>', [obj, ans, scope])
						return f'<callback cflibrary {call}.{cur} {value}>'
					else: return ans
			else:
				pass
		else:
			self.next()
			args = self.callargs()

			cur = obj.var_dict[cur]

			if cur in obj.fn_dict.keys():
				fn = obj.fn_dict[cur]
			else:
				fn = scope[3][cur]

			if type(fn[0]) != dict:
				ments = {}
			else:
				ments = fn[0]

			count = 0

			for i in ments:
				if i in args.keys():
					ments[i] = args[i]
				elif count < len(args) and list(args.keys())[count].startswith('null_'):
					ments[i] = args[list(args.keys())[count]]
					count += 1

			for i in ments:
				if ments[i] == 'empty__':
					print(f' Expected {len(ments)} arguments given {len(args)}\n  at function {value}')
					quit()
				else:
					pass
			
			code = fn[1]
			arg_ = [list(ments.values()), list(ments.keys())]
			return Pparser(code, scope, arg_, 'true', 'library', '__main__', obj, True).return_value

	# cheching for negative numbers
	def negative(self):
		operator = self.tok.type
		self.next()
		number = self.Collect(['PLUS', 'MINUS', 'MULTI', 'DIVIDE', 'MODULUS', 'RIGHT_PAREN', 'NEWLINE', 'END_STAT'])
		self.pre()
		if operator == 'MINUS':
			return 0-number
		else:
			return number
		
	# calling imported module
	def calledModule(self, value, cur, mode=False):
		if not mode:
			module = self.fn_dict[value]
		else:
			module = value

		if self.tok.type == 'LEFT_PAREN':
			args = self.getargs()
			if len(args) != 0:
				tmp = getattr(module, cur)(*args)
			else:
				tmp = getattr(module, cur)()
			return tmp
		else:
			return getattr(module, cur)

	# python module of function calling
	def calledMODULE(self, value):
		self.pre()
		args = self.getargs()
		module = self.fn_dict[value]
		if len(args) != 0:
			return module(*args)
		else:
			return module()

	# calling sub functions and attributes
	def handleDot(self, value):
		tmp = value
		
		while self.tok.type == 'DOT':
			self.next()
			cur = self.tok.value
			self.next()

			if type(tmp) == str and tmp.startswith('<__lib__.'):
				tmp = self.calledModule(tmp, cur)
			elif type(tmp) == str and tmp.startswith('<__object__.'):
				tmp = self.calledClassfunc(tmp, cur)
			elif type(tmp) == str and tmp.startswith('<__struct__.'):
				tmp = self.parserStruct(tmp, cur)
			elif self.tok.type == 'LEFT_PAREN':
				args = self.getargs()
				if len(args) != 0: tmp = getattr(tmp, cur)(*args)
				else: tmp = getattr(tmp, cur)()
			elif type(tmp) not in [str, int, float, dict, set, list, tuple]:
				tmp = self.calledModule(tmp, cur, True)
		
		return tmp

	# calling sub functions and attributes
	def handleIndex(self, value):
		tmp = value
		
		if type(tmp) in [str, list, dict, tuple, set]:
			if self.tok.type == 'LEFT_CURL':
				self.next()
				index = self.Collect(['RIGHT_CURL'])
				self.next()
			
				if self.tok.type == 'ASSIGN':
					self.next()
					value[index] = self.Collect(['NEWLINE', 'END_STAT'])
				else:
					tmp = value[index]
		else:
			print('Expected and iterable item'); quit()

		return tmp

	# list set, tuple, dict, assign
	def datatype(self, type):
		if type == '{':
			type = 'Object'
		else:
			self.next()

		if type == 'Array':
			if self.tok.type == 'LEFT_CURL':
				self.next(); array = []
				while self.tok.type != 'RIGHT_CURL':
					while self.tok.type == 'NEWLINE': self.next()

					value = self.Collect(['COMMA', 'RIGHT_CURL', 'NEWLINE'])
					array.append(value)

					if self.tok.type == 'RIGHT_CURL': pass
					else: self.next()

					while self.tok.type in ['COMMA', 'NEWLINE']: self.next()
				return array

		elif type == 'Tuple':
			if self.tok.type == 'LEFT_PAREN':
				self.next(); array = []
				while self.tok.type != 'RIGHT_PAREN':
					while self.tok.type == 'NEWLINE': self.next()

					value = self.Collect(['COMMA', 'RIGHT_PAREN', 'NEWLINE'])
					array.append(value)

					if self.tok.type == 'RIGHT_PAREN': pass
					else: self.next()

					while self.tok.type in ['COMMA', 'NEWLINE']: self.next()
				return tuple(array)

		elif type == 'Set':
			if self.tok.type == 'LEFT_PAREN':
				self.next()
				array = {'Jesus is my savior, and I shall Not worry all in any time and no no no time I will do. Amen.'}
				while self.tok.type != 'RIGHT_PAREN':
					while self.tok.type == 'NEWLINE': self.next()

					value = self.Collect(['COMMA', 'RIGHT_PAREN', 'NEWLINE'])
					array.add(value)

					if self.tok.type == 'RIGHT_PAREN': pass
					else: self.next()

					while self.tok.type in ['COMMA', 'NEWLINE']: self.next()
				array.remove('Jesus is my savior, and I shall Not worry all in any time and no no no time I will do. Amen.')
				return array

		elif type == 'Object':
			if self.tok.type == 'LEFT_BRACKET':
				self.next(); array = {}

				while self.tok.type != 'RIGHT_BRACKET':
					while self.tok.type in ['NEWLINE', 'COMMA']: self.next()

					key = self.Collect(['COMMA', 'COLON']); self.next()
					value = self.Collect(['COMMA', 'RIGHT_BRACKET', 'NEWLINE'])
					array[key] = value
					if self.tok.type == 'RIGHT_BRACKET': pass
					else: self.next()

					while self.tok.type in ['NEWLINE', 'COMMA']: self.next()

				return array

		elif type == 'Assign':
			if self.tok.type == 'LEFT_PAREN':
				self.next(); assign = {}

				while self.tok.type != 'RIGHT_PAREN':
					while self.tok.type in ['NEWLINE', 'COMMA']: self.next()

					key = self.tok.value; self.next()
					
					if self.tok.type == 'ASSIGN':
						self.next(); val = self.Collect2(['NEWLINE', 'COMMA']); assign[key] = val
					
					if self.tok.type == 'RIGHT_PAREN': pass
					else: self.next()

					while self.tok.type in ['NEWLINE', 'COMMA']: self.next()

				return assign

	# FUNCTIONS
	def callargs(self):
		args = {}; count=1
		while self.tok.type != 'RIGHT_PAREN':
			if self.tok.type == 'IDENTIFIER' and self.tok.value not in self.var_set:
				key = self.tok.value; self.next()

				if self.tok.type in ['COMMA', 'RIGHT_PAREN']:
					args[key] = f'empty__'
					if self.tok.type == 'COMMA': self.next()

				elif self.tok.type == 'ASSIGN':
					self.next(); value = self.Collect2(['COMMA', 'RIGHT_PAREN'])
					args[key] = value
						
					if self.tok.type in ['COMMA', 'NEWLINE']: self.next()
			else:
				val = self.Collect2(['COMMA', 'NEWLINE', 'RIGHT_PAREN'])
				args[f'null_{count}'] = val
				if self.tok.type in ['COMMA', 'NEWLINE']: self.next()
				count += 1
		self.next();
		return args
	

	# calling function
	def ImportFunction(self, value, args):
		codes = self.fn_dict[value]
		ments = {}
		ments.update(codes[0][0])
		count = 0

		for i in ments:
			if i in args.keys():
				ments[i] = args[i]
			elif count < len(args) and list(args.keys())[count].startswith('null_'):
				ments[i] = args[list(args.keys())[count]]
				count += 1

		for i in ments:
			if ments[i] == 'empty__':
				print(f' Expected {len(ments)} arguments given {len(args)}\n  at function {value}'); quit()
			else:
				pass

		code = codes[0][1]
		return Pparser(code, self.Importbins(codes[1]) + [value], [list(ments.values()), list(ments.keys())]).return_value

	# calling a class
	def calledClass(self, value, args):
		code_ = self.scope[value]
		code = code_[0]
		obj = Pparser(code, code_[1], [[], []], 'true', 'class', value).return_value

		public = obj.fn_set
		fn = 'notfound notfound'

		for i in public:
			if i.startswith('<function public'):
				fn = obj.fn_dict[i]
				break

		if fn == 'notfound notfound':
			saves = str(obj).split(' ')
			new = saves[0] + '.'; saves.pop(0); saves.insert(0, new); saves = ' '.join(saves)
			self.saveDICT(saves, obj)
			return saves
		else:
			ments = fn[0]
			ments = self.checker(ments, args, value)
			code = fn[1]
			arg_ = [list(ments.values()), list(ments.keys())]

			final = Pparser(code, code_[1], arg_, 'true', 'function', f'object {value.split(" ")[1]}', obj, True).obj
			saves = str(final).split(' '); saves.pop(0)
			saves.insert(0, '<__object__.'); saves = ' '.join(saves)
			self.saveDICT(saves, final)
			self.scope[saves] = [final, code_[1]]
			return saves

	# checking args
	def checker(self, ments, args, value):
		count = 0
		for i in ments:
			if i in args.keys():
				ments[i] = args[i]
			elif count < len(args) and list(args.keys())[count].startswith('null_'):
				ments[i] = args[list(args.keys())[count]]
				count += 1

		for i in ments:
			if ments[i] == 'empty__':
				self.ArgumentError(self.tok.value, self.tok.line, self.tok.file, len(ments), len(args), list(ments.keys()), list(args.keys()))
			else:
				pass

		if self.count == 0:
			self.traceback.append(Traceback_(self.tok.line, self.tok.file, self.name))
			self.count += 1
		else:
			popped = self.traceback.pop()
			self.traceback.append(Traceback_(self.tok.line, self.tok.file, self.name))
			self.count -= 1

		return ments


	# calling function from python or direct 
	def callfunction(self, value):
		tmp = value
		self.next()

		if type(value) == str and value.startswith('<function '):
			return self.called(value, self.callargs())
		elif type(value) == str and value.startswith('<Import '):
			return self.ImportFunction(value, self.callargs())
		
		elif type(value) == str and value.startswith('<__lib__.'):
			return self.calledMODULE(value)
		elif type(value) == str and value.startswith('<class '):
			return self.calledClass(value, self.callargs())

		elif type(value) == str and value.startswith('<method '):
			return self.calledClassMethod(value, self.callargs())
		elif type(value) == str and value.startswith('<local method'):
			return self.selfScopeMethod(value, self.callargs())

		elif '<class' in str(type(value)) and 'function' in str(type(value)):
			args = self.callargs()
			if len(args) == 0:
				return value()
			else:
				return value(*args)
			
	# geting true value
	def Bool(self):
		if self.tok.type == 'BOOL_TRUE':
			return True
		else:
			return False

	def Boolean(self):
		self.next()
		self.next()
		return self.Condition()

	# incase its from imported function
	def getfromlibrary(self):
		capt = self.tok.value

		if capt in self.obj.var_set:
			value = self.obj.var_dict[capt]
			if str(value).startswith('<function '):
				self.next()
				if self.tok.type == 'LEFT_PAREN':
					self.next()
					ans = self.thisFUNCTION(capt)
					self.pre()
					return ans
			else:
				return value
		else:
			return self.var_dict[self.tok.value]

	def factor(self, idn=''):
		if self.tok.type in ['INTEGER', 'FLOAT', 'STRING', 'IDENTIFIER', 'ENTER', 'FORMAT', 'ARRAY', 'TUPLE', 'ASSIGNMENT', 'SET', 'SELF', 'LEFT_BRACKET', 'BOOL_FALSE', 'BOOL_TRUE', 'EVAL', 'LAMBDA', 'STRUCT', 'MINUS', 'PLUS', 'BOOLEAN', 'FUNCTION']:

			if self.tok.type == 'IDENTIFIER':
				if self.tok.value in self.var_set:
					value = self.var_dict[self.tok.value]
				else:
					self.NameError(self.tok.value, self.tok.line, self.tok.file)
			elif self.tok.type == 'FORMAT':
				value = self.formator(self.tok.value)
			elif self.tok.type == 'SELF':
				value = self.checkself()
			elif self.tok.type == 'ENTER':
				value = self.enter()
			elif self.tok.type in ['ARRAY', 'TUPLE', 'SET', 'ASSIGNMENT', 'LEFT_BRACKET']:
				value = self.datatype(self.tok.value)
			elif self.tok.type == 'LAMBDA':
				value = self.lambdaa()
			elif self.tok.type in ['MINUS', 'PLUS']:
				value = self.negative()
			elif self.tok.type == 'FUNCTION':
				value = self.lambdaFunc()
			elif self.tok.type in ['BOOL_TRUE', 'BOOL_FALSE']:
				value = self.Bool()
			elif self.tok.type == 'BOOLEAN':
				value = self.Boolean()
			elif self.tok.type == 'STRUCT':
				self.next()
				value = self.structer()
			elif self.tok.type == 'EVAL':
				value = self.evalor()
			else:
				value = self.tok.value

			self.next()

			while self.tok.type in ['DOT', 'LEFT_PAREN', 'LEFT_CURL']:
				if self.tok.type == 'LEFT_PAREN':
					value = self.callfunction(value)

				if self.tok.type == 'DOT':
					value = self.handleDot(value)

				if self.tok.type == 'LEFT_CURL':
					value = self.handleIndex(value)

			return Num(value)

		elif self.tok.type == 'LEFT_PAREN':
			self.next(); node = self.expr(); self.next()
			return node

	def term(self, idn):
		node = self.factor(idn)
		
		while self.tok != None and self.tok.type in ['MULTI', 'DIVIDE', 'MODULUS']:
			op = self.tok.value
			self.next()
			right = self.factor(idn)
			node = BinOp(node, op, right)
		return node

	def expr(self, end='HELLOWORLDCODIN_G', idn='__main__'):
		node = self.term(idn)
		while self.tok.type not in end and self.tok.type in ('PLUS', 'MINUS'):
			op = self.tok.value
			self.next()
			right = self.term(idn)
			node = BinOp(node, op, right)
		return node

	def visit(self, node):
		if 'BinOp' in str(node.__class__):
			while 'BinOp' in str(node.__class__):
				left = node.left
				op = node.op
				right = node.right
				if op == '/': return self.visit(left) / self.visit(right)
				elif op == '*': return self.visit(left) * self.visit(right)
				elif op == '%': return self.visit(left) % self.visit(right)
				if op == '-': return self.visit(left) - self.visit(right)
				elif op == '+': return self.visit(left) + self.visit(right)
		else:
			return node.value

	def ans(self, node):
		try:
			if node.op == '+': return self.visit(node.left) + self.visit(node.right)
			elif node.op == '-': return self.visit(node.left) - self.visit(node.right)
			elif node.op == '*': return self.visit(node.left) * self.visit(node.right)
			elif node.op == '/': return self.visit(node.left) / self.visit(node.right)
			elif node.op == '%': return self.visit(node.left) % self.visit(node.right)
		except:
			return node.value

	def Collect(self, end, idn="__main__"):
		out = self.ans(self.expr(end, idn))
		return out

	def Collect2(self, end, idn="__main__"):
		val = r''
		out = self.ans(self.expr(end))
		return out

	def Condition(self):
		value = 'true'
		found = 'false'
		ext = []
		keep = []

		while self.tok.type != 'RIGHT_PAREN':
			if self.tok.type == 'NOT':
				left = 'Jesus is our survior.'

			elif self.tok.type == 'BOOL_TRUE':
				left = 'true'
				self.next()

			elif self.tok.type == 'BOOL_FALSE':
				left = 'false'
				self.next()

			elif self.tok.type == 'NULL':
				left = None
				self.next()
			else:
				left = self.Collect(['RIGHT_PAREN', 'EQUALS_TO', 'NOT_EQUAL', 'GREATER_THAN', 'LESS_THAN', 'GREATER_OR_EQUALS_TO', 'LESS_OR_EQUALS_TO', 'IN', 'ASSIGN', 'NOT_IN', 'NOT', 'EQUALS_EQUALS_TO', 'AND', 'OR'])

			if self.tok.type in ['RIGHT_PAREN', 'AND', 'OR']:
				check = 'STOPPED'
			else:
				check = self.tok.type
				self.next()
				right = self.Collect(['RIGHT_PAREN', 'OR', 'AND'])

			if check == 'EQUALS_TO':
				if left == right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'NOT_EQUAL':
				if left != right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'GREATER_THAN':
				if left > right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'LESS_THAN':
				if left < right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'EQUALS_EQUALS_TO':
				if type(left) != type(right):
					left = type(right)(left)

				if left == right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'ASSIGN':
				if str(left).lower() == str(right).lower():
					found = 'true'
				else:
					found = 'false'

			elif check == 'GREATER_OR_EQUALS_TO':
				if left >= right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'LESS_OR_EQUALS_TO':
				if left <= right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'IN':
				if left in right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'NOT_IN':
				if left not in right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'NOT':
				if not right:
					found = 'true'
				else:
					found = 'false'

			elif check == 'STOPPED':
				if left == 'true':
					found = 'true'
				elif left == 'false':
					found = 'false'
				else:
					if left:
						found = 'true'
					else:
						found = 'false'

			if self.tok.type == 'OR':
				ext.append('or')
				keep.append(found)
				self.next()

			elif self.tok.type == 'AND':
				ext.append('and')
				keep.append(found)
				self.next()

		keep.append(found)

		if 'or' in ext:
			if 'true' in keep:
				return True
			else:
				return False
		elif 'and' in ext:
			if 'false' in keep:
				return False
			else:
				return True
		else:
			if keep[0] == 'true':
				return True
			else:
				return False

	def parse(self):
		while self.tok != None:

			if self.tok.type == 'REUSE':
				self.next()
				self.next()
				cont = self.Condition()
				self.next()

				self.result[0] = cont
				if cont == False:
					break

			elif self.tok.type == 'NEWLINE': self.next()	

			elif self.tok.type == 'PRINTF':
				self.next()
				self.next()
				coll = []
				while self.tok.type != 'RIGHT_PAREN':
					coll.append(self.Collect(['RIGHT_PAREN, COMMA']))
					if self.tok.type == 'COMMA':
						self.next()
				print(*coll)
				self.next()

			elif self.tok.type == 'IDENTIFIER':
				name = self.tok.value; self.next()

				if self.tok.type == 'LEFT_PAREN':
					self.pre()
					call = self.Collect(['NEWLINE', 'END_STAT'])

				elif self.tok.type == 'ASSIGN':
					self.next()
					valut = []
					while self.tok.type not in ['NEWLINE', 'END_STAT']:
						value = self.Collect(['NEWLINE', 'COMMA', 'END_STAT'], name)
						valut.append(value)
						if self.tok.type == 'COMMA': self.next()

					if len(valut) > 1:
						self.save(name, tuple(valut))
					else:
						self.save(name, value)

				elif self.tok.type == 'COMMA':
					self.next(); varis = [name]
					while self.tok.type not in ['ASSIGN', 'NEWLINE', 'END_STAT']:
						if self.tok.type == 'COMMA': self.next()
						elif self.tok.type == 'IDENTIFIER': 
							varis.append(self.tok.value); self.next()
						else:
							self.error('Invalid syntax on variable assignment.')

					if self.tok.type == 'ASSIGN':
						self.next()
						valut = []
						while self.tok.type not in ['NEWLINE', 'END_STAT']:
							value = self.Collect(['NEWLINE', 'COMMA', 'END_STAT'], name)
							valut.append(value)
							if self.tok.type == 'COMMA': self.next()


						if len(varis) == len(valut):
							count = 0
							for i in valut: self.save(varis[count], i); count += 1
						elif type(valut[0]) in [tuple, list, set, dict] and len(valut[0]) == len(varis):
							count = 0
							for i in valut[0]: self.save(varis[count], i); count += 1
						else:
							self.error('variable assignment is not equal.')

				elif self.tok.type == 'ADD_ADD':
					self.next()
					self.save(name, self.var_dict[name] + 1)

				elif self.tok.type == 'MINUS_MINUS':
					self.next()
					self.save(name, self.var_dict[name] - 1)

				elif self.tok.type == 'ADD_TO':
					self.next()
					if name in self.var_set: value = self.var_dict[name]
					else: print(f'{name} is not defined'); quit()
					value = value + self.Collect(['NEWLINE', 'END_STAT'])
					self.save(name, value)

				elif self.tok.type == 'SUBTRACT_FROM':
					self.next()
					if name in self.var_set: value = self.var_dict[name]
					else: print(f'{name} is not defined'); quit()
					value = value - self.Collect(['NEWLINE', 'END_STAT'])
					self.save(name, value)

				elif self.tok.type == 'MULTIPLYBY':
					self.next()
					if name in self.var_set: value = self.var_dict[name]
					else: print(f'{name} is not defined'); quit()
					value = value * self.Collect(['NEWLINE', 'END_STAT'])
					self.save(name, value)

				elif self.tok.type == 'DIVIDEBY':
					self.next()
					if name in self.var_set: value = self.var_dict[name]
					else: print(f'{name} is not defined'); quit()
					value = value / self.Collect(['NEWLINE', 'END_STAT'])
					self.save(name, value)

				elif self.tok.type in ['DOT', 'LEFT_CURL']:
					self.pre()
					value = self.Collect(['NEWLINE', 'END_STAT'])

			elif self.tok.type == 'SELF':
				self.next(); self.next()
				name = self.tok.value; self.next()

				if self.tok.type == 'LEFT_PAREN':
					self.next()
					self.thisFUNCTION(name)

				elif self.tok.type == 'ASSIGN':
					self.next()
					value = self.Collect(['NEWLINE', 'END_STAT'], name)
					self.Objthissave(name, value)

				elif self.tok.type == 'ADD_TO':
					self.next()
					if name in self.obj.var_set: value = self.obj.var_dict[name]
					else: print(f'{name} is not defined'); quit()
					value = value + self.Collect(['NEWLINE', 'END_STAT'])
					self.Objthissave(name, value)

				elif self.tok.type == 'SUBTRACT_FROM':
					self.next()
					if name in self.var_set: value = self.var_dict[name]
					else: print(f'{name} is not defined'); quit()
					value = value - self.Collect(['NEWLINE', 'END_STAT'])
					self.Objthissave(name, value)

				elif self.tok.type == 'MULTIPLYBY':
					self.next()
					if name in self.var_set: value = self.var_dict[name]
					else: print(f'{name} is not defined'); quit()
					value = value * self.Collect(['NEWLINE', 'END_STAT'])
					self.Objthissave(name, value)

				elif self.tok.type == 'DIVIDEBY':
					self.next()
					if name in self.var_set: value = self.var_dict[name]
					else: print(f'{name} is not defined'); quit()
					value = value / self.Collect(['NEWLINE', 'END_STAT'])
					self.Objthissave(name, value)

				elif self.tok.type == 'DOT':
					while self.tok.type != 'SELF':
						self.pre()
					value = self.Collect(['NEWLINE', 'END_STAT'])
					if type(value) in [list, tuple, set, dict]:
						self.Objthissave(name, value)
					else:
						pass

			elif self.tok.type == 'GETBACK':
				self.next()
				valut = []

				while self.tok.type not in ['NEWLINE']:
					value = self.Collect(['NEWLINE', 'COMMA'])
					valut.append(value)

					if self.tok.type == 'COMMA':
						self.next()

				if len(valut) > 1:
					self.evaled = tuple(valut)
				else:
					self.evaled = valut[0]

				break

			elif self.tok.type == 'BREAK':
				self.result[1] = 'break'
				self.result[2] = self.return_value
				break

			elif self.tok.type == 'IF':
				self.next()
				self.next()
				bool_ = self.Condition()
				self.next()
				code = []
				count = 1
				homiz = 'false'

				while self.tok.type == 'NEWLINE': self.next()
				
				if self.tok.type == 'LEFT_BRACKET':	
					self.next()
					while count != 0:
						if self.tok.type == 'LEFT_BRACKET':
							count += 1
						elif self.tok.type == 'RIGHT_BRACKET': 
							count -= 1
							if count == 0:
								break
						code.append(self.tok)
						self.next()
					self.next()

					while self.tok.type == 'NEWLINE': self.next()
				else:
					while self.tok.type != 'NEWLINE':
						code.append(self.tok)
						self.next()
					code.append(self.tok)
					self.next()

				if bool_:
					count = 1

					while count != 0:
						if self.tok.type == 'IF':
							count += 1
						elif self.tok.type == 'END': 
							count -= 1
							if count == 0:
								break
						self.next()
					self.next()

					ans = Pparser(code, self.bins(), 'if statement').result
					self.result[1] = ans[1]
					self.return_value = ans[2]
					self.result[2] = ans[2]

					if self.result[1] == 'break':
						break
				else:
					countup = 1
					while countup != 0:
						while self.tok.type == 'NEWLINE': self.next()
						
						if bool_:
							pass

						elif self.tok.type == 'ELIF':
							self.next()
							self.next()
							bool_ = self.Condition()
							self.next()
							code = []
							count = 1

							while self.tok.type == 'NEWLINE': self.next()
							
							if self.tok.type == 'LEFT_BRACKET':
								self.next()
								while count != 0:
									if self.tok.type == 'LEFT_BRACKET':
										count += 1
									elif self.tok.type == 'RIGHT_BRACKET': 
										count -= 1
										if count == 0:
											break
									code.append(self.tok)
									self.next()
								self.next()
							else:
								while self.tok.type != 'NEWLINE':
									code.append(self.tok)
									self.next()
								code.append(self.tok)

							if bool_:
								count = 1
								while count != 0:
									if self.tok.type == 'IF':
										count += 1
									elif self.tok.type == 'END': 
										count -= 1
										if count == 0:
											break
									self.next()

								ans = Pparser(code, self.bins(), 'if statement').result
								self.result[1] = ans[1]
								self.return_value = ans[2]

								if self.result[1] == 'break':
									break

						elif self.tok.type == 'ELSE':
							self.next()
							code = []
							count = 1

							while self.tok.type == 'NEWLINE': self.next()
							
							
							if self.tok.type == 'LEFT_BRACKET':
								self.next()
								while count != 0:
									if self.tok.type == 'LEFT_BRACKET':
										count += 1
									elif self.tok.type == 'RIGHT_BRACKET': 
										count -= 1
										if count == 0:
											break
									code.append(self.tok)
									self.next()
								self.next()
							else:
								while self.tok.type != 'NEWLINE':
									code.append(self.tok)
									self.next()
								code.append(self.tok)

							while self.tok.type != 'END': self.next()


							ans = Pparser(code, self.bins(), 'if statement').result
							self.result[1] = ans[1]
							self.return_value = ans[2]
							self.result[2] = ans[2]

							if self.result[1] =='break':
								break

						if self.tok.type == 'IF':
							countup += 1
						elif self.tok.type == 'END':
							countup -= 1
							if countup == 0:
								break

					if self.result[1] == 'break':
						self.result[2] = ans[2]
						self.return_value = self.result[2]
						break

				self.return_value = self.result[2]

			elif self.tok.type == 'FOR':
				self.next(); self.next()

				register = []
				while self.tok.type != 'IN':
					if self.tok.type == 'IDENTIFIER':
						register.append(self.tok.value)
					self.next()

				# for the in keyword
				self.next()

				loop_element = self.Collect(['LEFT_PAREN'])
				self.next()
				count = 1
				code = []
				
				while self.tok.type != 'LEFT_BRACKET':
					self.next()
				self.next()
				
				while count != 0:
					if self.tok.type == 'LEFT_BRACKET':
						count += 1
					elif self.tok.type == 'RIGHT_BRACKET': 
						count -= 1
						if count == 0:
							break
					code.append(self.tok)
					self.next()
				self.next()
				
				if len(register) == 1:
					main = register[0]
					for i in loop_element:
						self.save(main, i)
						if Pparser(code, self.bins(), 'for loop').result[1] == 'break':
							break
				elif len(register) == 2:
					main = register[0]; main2 = register[1]
					for a, b in loop_element:
						self.save(main, a); self.save(main2, b)
						if Pparser(code, self.bins(), 'for loop').result[1] == 'break':
							break
				elif len(register) == 3:
					main = register[0]; main2 = register[1]; main3 = register[2]
					for a, b, c in loop_element:
						self.save(main, a); self.save(main2, b); self.save(main3, c)
						if Pparser(code, self.bins(), 'for loop').result[1] == 'break':
							break
				elif len(register) == 4:
					main = register[0]; main2 = register[1]; main3 = register[2]; main4 = register[3]
					for a, b, c, d in loop_element:
						self.save(main, a); self.save(main2, b); self.save(main3, c); self.save(main4, d)
						if Pparser(code, self.bins(), 'for loop').result[1] == 'break':
							break
				elif len(register) == 5:
					main = register[0]; main2 = register[1]; main3 = register[2]; main4 = register[3]; main5 = register[4]
					for a, b, c, d, e in loop_element:
						self.save(main, a); self.save(main2, b); self.save(main3, c); self.save(main4, d); self.save(main5, e)
						if Pparser(code, self.bins(), 'for loop').result[1] == 'break':
							break

			elif self.tok.type == 'WHILE':
				self.next()
				self.next()
				bool_ = self.Condition()
				resuse = [];

				while self.tok.type != 'WHILE':
					resuse.insert(0, self.tok)
					self.pre()

				resuse.insert(0, Token('REUSE', self.tok.line))

				count = len(resuse)
				while count != 0:
					self.next()
					count-=1
		
				while self.tok.type != 'LEFT_BRACKET': self.next()

				self.next()

				code = []; count = 1
				while count != 0:
					if self.tok.type == 'LEFT_BRACKET':
						count += 1
					elif self.tok.type == 'RIGHT_BRACKET': 
						count -= 1
						if count == 0:
							break

					code.append(self.tok)
					self.next()

				self.next()
				mix = resuse + code
				
				brakes = 'false'
				if bool_ == True:
					while bool_ == True and brakes != 'break':
						work = Pparser(mix, self.bins(), 'while loop').result
						bool_ = work[0]
						brakes = work[1]

			elif self.tok.type == 'SWITCH':
				self.next()
				if self.tok.type == 'LEFT_PAREN':
					self.next()
					query = self.Collect(['RIGHT_PAREN'])
					self.next()
					while self.tok.type == 'NEWLINE': self.next()

					if self.tok.type == 'LEFT_BRACKET':
						self.next()
						while self.tok.type != 'RIGHT_BRACKET':
							if self.tok.type == 'CASE':
								self.next()
								value = self.Collect(['LEFT_BRACKET', 'NEWLINE'])
								while self.tok.type == 'NEWLINE': self.next()

								if self.tok.type == 'LEFT_BRACKET':
									self.next()
									count = 1
									code = []
									count_switch = 0
									broke = False
									while count != 0:
										if self.tok.type == 'LEFT_BRACKET':
											count += 1
										elif self.tok.type == 'RIGHT_BRACKET':
											count -= 1
											if count == 0:
												break

										code.append(self.tok)
										self.next()
									self.next()

									if query == value:
										check = code.copy()
										check.reverse()
										
										index_break = -1
										for i in check:
											index_break += 1
											if i.type not in  ['NEWLINE', 'END_STAT']:
												if i.type == 'BREAK':
													broke = True
												break

										if broke == True:
											code.pop(-1-index_break)
										
										code.append(Token('NEWLINE', self.tok.line))
										self.execloop(code, self.bins())

										if broke:
											count = 1
											while count != 0:
												if self.tok.type == 'LEFT_BRACKET':
													count += 1
												elif self.tok.type == 'RIGHT_BRACKET':
													count -= 1
													if count == 0:
														self.pre()
														break
												self.next()
								else:
									pass
							elif self.tok.type == 'DEFAULT':
								self.next()
								while self.tok.type == 'NEWLINE': self.next()

								if self.tok.type == 'LEFT_BRACKET':
									self.next()
									code = []
									count = 1
									while count != 0:
										if self.tok.type == 'LEFT_BRACKET':
											count += 1
										elif self.tok.type == 'RIGHT_BRACKET':
											count -= 1
											if count == 0:
												break
										code.append(self.tok)
										self.next()

									self.execloop(code, self.bins())
								else:
									pass

							self.next()
						self.next()
					else:
						pass

					# quit()
				else:
					print('Open paranthesis for switch statement')
					quit()

			elif self.tok.type == 'STRU':
				self.next()
				dictor = {}

				while self.tok.type != 'RIGHT_BRACKET':
					if self.tok.type == 'IDENTIFIER':
						idd = self.tok.value
						self.next()

						if self.tok.type == 'ARROW':
							self.next()
							val = self.Collect(['NEWLINE', 'END_STAT', 'COMMA'])
							dictor[idd] = val

						else:
							dictor[idd] = ''
					self.next()
				self.evaled = dictor
				break

			elif self.tok.type == 'EVAL':
				self.next()

				if self.tok.type == 'LEFT_PAREN':
					self.next()

				codes = self.Collect(['RIGHT_PAREN'])
				self.next()
				lexed = Lexer(codes).tokens
				lexed.insert(0, Token('GETBACK', self.tok.line)); lexed.append(Token('NEWLINE', self.tok.line))
				self.next()

				ans = Pparser(lexed, self.bins(), [[], []]).evaled

			elif self.tok.type == 'FUNCTION':
				self.next()
				fn_name = self.tok.value
				self.next()

				if self.mode in ['function', 'normal', 'import']:
					self.method(fn_name)
				elif self.mode == 'class':
					self.thismethod(fn_name)

			elif self.tok.type == 'RETURN':
				self.next()
				self.return_value = self.Collect(['NEWLINE', 'END_STAT'])
				self.result[1] = 'break'
				self.result[2] = self.return_value
				break

			elif self.tok.type == 'CLASS':
				self.next()
				self.classic()

			elif self.tok.type == 'IMPORT':
				self.next()
				self.imported()

			elif self.tok.type == 'CONST':
				self.next()
				name = self.tok.value; self.next()

				if self.tok.type == 'ASSIGN':
					self.next()
					value = self.Collect(['NEWLINE', 'END_STAT'], name)
					self.saveconst(name, value)
				elif self.tok.type in ['NEWLINE', 'END_STAT']:
					self.saveconst(name, '')

			elif self.tok.type == 'STRUCT':
				self.next()
				self.structer()

			elif self.tok.type == 'STRING': self.next()

			elif self.tok.type == 'DEL':
				self.next()
				identifers = []

				while self.tok.type not in ['NEWLINE', 'END_STAT']:
					if self.tok.type == 'COMMA': pass
					else: identifers.append(self.tok.value)
					self.next()

				for i in identifers:
					self.gabbage(i)

			elif self.tok.type == 'STOP':
				self.next()
				if self.tok.type == 'LEFT_PAREN':
					self.next()
					quit()
				else:
					self.InvalidSyntaxError(self.tok.value, self.tok.line, self.tok.file)

			elif self.tok.type == 'MULTI_COMMENTS_START':
				self.next()
				while self.tok.type != 'MULTI_COMMENTS_END': self.next()
				self.next()

			else:
				if self.tok.type in ['NEWLINE', 'END_STAT', 'END', 'CONTINUE']: self.next()
				else:
					self.InvalidSyntaxError(self.tok.value, self.tok.line, self.tok.file)

	def objector(self):
		self.drawft()
		if self.mode == 'class':
			self.return_value = self.Elements(self.name, self.thisvar_set, self.thisvar_dict, self.thisfn_set, self.thisfn_dict)
		elif self.mode == 'import':
			self.return_value = self.Importer(self.name, self.var_set, self.var_dict, self.fn_set, self.fn_dict, self.const_set)

def scope():
	scope = {}
	var_set = {'null'}
	const_set = {'null'}
	var_dict = {'null': None}
	fn_set = {'episode_'}
	fn_dict = {}
	imports = {}
	return [scope, var_set, var_dict, fn_set, fn_dict, const_set, imports]

