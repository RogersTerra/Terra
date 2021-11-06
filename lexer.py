import re
import os


class Token:
	def __init__(self, type, line, value=None, file='stdin'):
		self.type = type
		self.line = line
		self.value = value
		if file == 'stdin':
			self.file = file
		else:
			self.file = os.path.abspath(file)

	def __repr__(self):
		return f'({self.type}->{self.value}->{self.line})'


class Lexer:
	def __init__(self, code, file='stdin'):
		self.code = code
		self.file = file
		self.tokenizer()

	def tokenizer(self):
		expr = [r'\d+(.d*)?']
		exe = iter(expr)

		# \$"(.*?)"
		pattern = r'\d+(\.d*)?\d+|@|"""|\?"(.*?)"|#|b"(.*?)"|r"(.*?)"|"(.*?)"|\.|else if|->|\[|\]|//(.*?)\n|{|}|' + r"'''|b'(.*?)'|r'(.*?)'|\?'(.*?)'|'(.*?)'|" + r'\w+|~|\+\+|--|\+=|-=|\*=|/=|\||&&|/\*|\*/|[/\*\+-]|%|\^|===|==|!in|!=|!|<=|>=|<|>|=|,|\(|\)|[\t]+|:|[ ]+|[\n]|;'
		DIGITS = '0123456789'
		line_num = 1
		tokens = []
		couter = -1
		coms = ''
		stock = 'false'
		count = 0
		for tok in re.finditer(pattern, self.code):
			couter+=1
			value = tok.group()

			if stock == 'false':
				if value == '\n':
					tokens.append(Token('NEWLINE', line_num, value, self.file))
					line_num += 1

				elif re.match(r'[\t]+', value):
					pass
				
				elif re.match(r'//(.*?)\n',value):
					tokens.append(Token('NEWLINE', line_num, value, self.file))
					line_num += 1

				elif re.match(r'~',value):
					tokens.append(Token('NEWLINE', line_num, value, self.file))
					

				elif re.match(r'[ ]+',value):
					pass

				elif re.match(r'/\*', value):
					tokens.append(Token('MULTI_COMMENTS_START', line_num, value, self.file))

				elif re.match(r'\*/', value):
					tokens.append(Token('MULTI_COMMENTS_END', line_num, value, self.file))



				elif re.match(r'"""', value) or re.match(r"'''", value):
					stock = 'true'

				elif re.match(r'#', value):
					tokens.append(Token('HASH', line_num, value, self.file))

				# END OF A STRING
				elif value == ';':
					tokens.append(Token('END_STAT', line_num, value, self.file))
				elif value == ':':
					tokens.append(Token('COLON', line_num, value, self.file))

				# data types
				elif re.match(r'\.', value):
					tokens.append(Token('DOT', line_num, value, self.file))

				# arrow
				elif re.match(r'->', value):
					tokens.append(Token('ARROW', line_num, value, self.file))

				# getting validators
				elif re.match(r'\|', value):
					tokens.append(Token('OR', line_num, value, self.file))
				elif re.match(r'&&', value):
					tokens.append(Token('AND', line_num, value, self.file))

				# update operators
				elif re.match(r'\+=', value):
					tokens.append(Token('ADD_TO', line_num, value, self.file))

				elif re.match(r'\+\+', value):
					tokens.append(Token('ADD_ADD', line_num, value, self.file))

				elif re.match(r'--', value):
					tokens.append(Token('MINUS_MINUS', line_num, value, self.file))

				elif re.match(r'-=', value):
					tokens.append(Token('SUBTRACT_FROM', line_num, value, self.file))
				elif re.match(r'\*=', value):
					tokens.append(Token('MULTIPLYBY', line_num, value, self.file))
				elif re.match(r'/=', value):
					tokens.append(Token('DIVIDEBY', line_num, value, self.file))

				# expressions
				elif re.match(r'===', value):
					tokens.append(Token('EQUALS_EQUALS_TO', line_num, value, self.file))
				elif re.match(r'==', value):
					tokens.append(Token('EQUALS_TO', line_num, value, self.file))
				elif re.match(r'!=', value):
					tokens.append(Token('NOT_EQUAL', line_num, value, self.file))
				elif re.match(r'!in', value):
					tokens.append(Token('NOT_IN', line_num, value, self.file))
				elif re.match(r'!', value):
					tokens.append(Token('NOT', line_num, value, self.file))
				elif re.match(r'<=', value):
					tokens.append(Token('LESS_OR_EQUALS_TO', line_num, value, self.file))
				elif re.match(r'>=', value):
					tokens.append(Token('GREATER_OR_EQUALS_TO', line_num, value, self.file))
				elif re.match(r'<', value):
					tokens.append(Token('LESS_THAN', line_num, value, self.file))
				elif re.match(r'>', value):
					tokens.append(Token('GREATER_THAN', line_num, value, self.file))

				# tokens for operators [/*+-]
				elif value == '+':
					tokens.append(Token('PLUS', line_num, value, self.file))
				elif value == '-':
					tokens.append(Token('MINUS', line_num, value, self.file))
				elif value == '*':
					tokens.append(Token('MULTI', line_num, value, self.file))
				elif value == '/':
					tokens.append(Token('DIVIDE', line_num, value, self.file))
				elif value == '%':
					tokens.append(Token('MODULUS', line_num, value, self.file))
				elif value == '^':
					tokens.append(Token('POW', line_num, value, self.file))
				elif value == '=':
					tokens.append(Token('ASSIGN', line_num, value, self.file))

				# PARENTHESIS
				elif value == '(':
					tokens.append(Token('LEFT_PAREN', line_num, value, self.file))
				elif value == ')':
					tokens.append(Token('RIGHT_PAREN', line_num, value, self.file))

				# CURL BRACKETS
				elif value == '{':
					tokens.append(Token('LEFT_BRACKET', line_num, value, self.file))
				elif value == '}':
					tokens.append(Token('RIGHT_BRACKET', line_num, value, self.file))

				# BRACKETS
				elif value == '[':
					tokens.append(Token('LEFT_CURL', line_num, value, self.file))
				elif value == ']':
					tokens.append(Token('RIGHT_CURL', line_num, value, self.file))

				# getting numbers
				elif re.match(r'\d+(\.d*)?\d+', value) or value in '0123456789':
					if '.' in value:
						tokens.append(Token('FLOAT', line_num, float(value), self.file))
					else:
						tokens.append(Token('INTEGER', line_num, int(value), self.file))

				elif re.match(r'b"(.*?)"', value):
					tokens.append(Token('STRING', line_num, eval(value), self.file))
				elif re.match(r"b'(.*?)'", value):
					tokens.append(Token('STRING', line_num, eval(value), self.file))

				elif re.match(r'r"(.*?)"', value):
					tokens.append(Token('STRING', line_num, eval(value), self.file))
				elif re.match(r"r'(.*?)'", value):
					tokens.append(Token('STRING', line_num, eval(value), self.file))

				elif re.match(r'\?"(.*?)"', value):
					tokens.append(Token('FORMAT', line_num, eval(value.lstrip('?')), self.file))
				elif re.match(r"\?'(.*?)'", value):
					tokens.append(Token('FORMAT', line_num, eval(value.lstrip('?')), self.file))

				elif re.match(r'"(.*?)"', value):
					tokens.append(Token('STRING', line_num, eval(value), self.file))
				elif re.match(r"'(.*?)'", value):
					tokens.append(Token('STRING', line_num, eval(value), self.file))


				#datatypes
				elif value == 'Array':
					tokens.append(Token('ARRAY', line_num, value, self.file))
				elif value == 'Tuple':
					tokens.append(Token('TUPLE', line_num, value, self.file))
				elif value == 'Assign':
					tokens.append(Token('ASSIGNMENT', line_num, value, self.file))
				elif value == 'Set':
					tokens.append(Token('SET', line_num, value, self.file))
				elif value == 'const':
					tokens.append(Token('CONST', line_num, value, self.file))
				elif value == 'default':
					tokens.append(Token('DEFAULT', line_num, value, self.file))


				## importing files
				elif value == 'import':
					tokens.append(Token('IMPORT', line_num, value, self.file))
				elif value == 'from':
					tokens.append(Token('FROM', line_num, value, self.file))
				elif value == 'loc_':
					tokens.append(Token('LOCATE', line_num, value, self.file))

				# getting a COMMAND
				elif value == ',':
					tokens.append(Token('COMMA', line_num, value, self.file))
				elif value == 'break':
					tokens.append(Token('BREAK', line_num, value, self.file))
				elif value == 'if':
					tokens.append(Token('IF', line_num, value, self.file))
				elif re.match(r'else if', value):
					tokens.append(Token('ELIF', line_num, value, self.file))
				elif value == 'else':
					tokens.append(Token('ELSE', line_num, value, self.file))
				elif value == 'switch':
					tokens.append(Token('SWITCH', line_num, value, self.file))
				elif value == 'case':
					tokens.append(Token('CASE', line_num, value, self.file))


				elif re.match(r'@',value):
					tokens.append(Token('EACH', line_num))

				elif value == 'Func':
					tokens.append(Token('FUNCTION', line_num, value, self.file))
				elif value == 'trash':
					tokens.append(Token('DEL', line_num, value, self.file))
				elif value == 'Object':
					tokens.append(Token('CLASS', line_num, value, self.file))
				elif value == 'extends':
					tokens.append(Token('EXTENDS', line_num, value, self.file))
				elif value == 'public':
					tokens.append(Token('PUBLIC', line_num, value, self.file))
				elif value == 'self':
					tokens.append(Token('SELF', line_num, value, self.file))
				elif value == 'return':
					tokens.append(Token('RETURN', line_num, value, self.file))
				elif value == 'as':
					tokens.append(Token('AS', line_num, value, self.file))
				elif value == 'lambda':
					tokens.append(Token('LAMBDA', line_num, value, self.file))
				elif value == 'stop':
					tokens.append(Token('STOP', line_num, value, self.file))
					
				elif value == 'while':
					tokens.append(Token('WHILE', line_num, value, self.file))
				elif value == 'struct':
					tokens.append(Token('STRUCT', line_num, value, self.file))
				elif value == 'end':
					tokens.append(Token('END', line_num, value, self.file))
				elif value == 'cmp':
					tokens.append(Token('BOOLEAN', line_num, value, self.file))

				#for loop
				elif value == 'for':
					tokens.append(Token('FOR', line_num, value, self.file))
				elif value == 'in':
					tokens.append(Token('IN', line_num, value, self.file))

				elif value == 'true':
					tokens.append(Token('BOOL_TRUE', line_num, value, self.file))
				elif value == 'false':
					tokens.append(Token('BOOL_FALSE', line_num, value, self.file))
				elif value == 'none':
					tokens.append(Token('NONE_VAL', line_num, value, self.file))

				# standing input and output
				elif value == 'echo':
					tokens.append(Token('PRINTF', line_num, value, self.file))
				elif value == 'eval':
					tokens.append(Token('EVAL', line_num, value, self.file))
				elif value == 'continue':
					tokens.append(Token('CONTINUE', line_num, value, self.file))
				elif value == 'enter':
					tokens.append(Token('ENTER', line_num, value, self.file))

				elif value == 'try':
					tokens.append(Token('TRY', line_num, value, self.file))
				elif value == 'catch':
					tokens.append(Token('CATCH', line_num, value, self.file))
				elif value == 'finally':
					tokens.append(Token('FINALLY', line_num, value, self.file))
				else:
					tokens.append(Token('IDENTIFIER', line_num, value, self.file))
			else:
				if re.match(r'"""', value) or re.match(r"'''", value):
					tokens.append(Token('STRING', line_num, coms, self.file))
					stock = 'false'; coms = ''
				else:
					coms += value
		tokens.append(Token('NEWLINE', line_num, '\n', self.file))
		self.tokens = tokens
		