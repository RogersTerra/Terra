from interpreter import Pparser
from lexer import Lexer
import sys

def scope():
	scope = {}
	var_set = {'null'}
	const_set = {'null'}
	var_dict = {'null': None}
	fn_set = {'episode_'}
	fn_dict = {}
	imports = {}
	return [scope, var_set, var_dict, fn_set, fn_dict, const_set, imports]


arv = sys.argv

if len(arv) > 1:
	if arv[1] == 'pkg':
		print('creating executable file')
	else:
		with open(arv[1], 'r') as file:
			syn = file.read()
		Pparser(syn, scope()+[arv[1]], [[], []], bolt=1, mode='function', name='__main__', obj='function', file_=arv[1])
else:
	print('Terra 0.0.1 2021')
	try:
		syn = input('> ')
		if syn[0] in '0123456789':
			syn = 'echo(eval(' + r'%r' %syn + '))'
		
		syn = Lexer(syn).tokens
		compiler = Pparser(syn, scope()+['stdin'], [[], []], bolt=1, mode='function', name='__main__', obj='function', file_='stdin')
		while True:
			syn = input('> ')
			if syn[0] in '0123456789':
				syn = 'echo(eval(' + r'%r' %syn + '))'
			
			syn = Lexer(syn).tokens
			compiler = Pparser(syn, compiler.bins(), [[], []], bolt=1, mode='function', name='__main__', obj='function', file_='stdin')

	except KeyboardInterrupt as e:
		print(e)
