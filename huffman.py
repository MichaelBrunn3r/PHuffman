# -*- coding: UTF-8

import math, re, ast
from fractions import Fraction

COLUMN_OCCURRENCES = 'o'
COLUMN_REL_PROBS = 'p'
COLUMN_CODES = 'c'
COLUMN_CODE_LENGTHS = 'l'
COLUMNS = sorted([COLUMN_OCCURRENCES, COLUMN_REL_PROBS, COLUMN_CODES, COLUMN_CODE_LENGTHS])
DEFAULT_COLUMN_HEADERS = {
	COLUMN_OCCURRENCES: 'n',
	COLUMN_REL_PROBS: 'P',
	COLUMN_CODES: 'Huffman Code',
	COLUMN_CODE_LENGTHS: 'Code length'
}

class HuffmanTree:
	def __init__(self, cases, probability, left=None, right=None):
		self.cases = cases
		self.probability = probability
		self.left = left
		self.right = right

	def __repr__(self):
		cases_str = '['
		for i,case in enumerate(self.cases):
			if i > 0: cases_str += '|'
			cases_str += case
		cases_str += ']'
		return "({},[{},{}],{})".format(self.left, cases_str, self.probability, self.right)

	def __str__(self,level=0):
		cases_str = '['
		for i,case in enumerate(self.cases):
			if i > 0: cases_str += '|'
			cases_str += case
		cases_str += ']'

		ret = ""
		if self.right:
			ret += self.right.__str__(level+1)
		ret += "{}({}, {})\n".format(' '*level, cases_str, self.probability)
		if self.left:
			ret += self.left.__str__(level+1)
		return ret 

	@staticmethod
	def from_char_probabilities(char_probs):
		nodes = sorted([HuffmanTree(char, char_probs[char]) for char in sorted(char_probs)], key=lambda x: x.probability)
		while len(nodes) > 1:
			node_left_idx = 0
			for i in range(len(nodes)):
				if(nodes[i].probability < nodes[node_left_idx].probability):
					node_left_idx = i
			node_left = nodes.pop(node_left_idx)

			node_right_idx = 0
			for i in range(len(nodes)):
				if(nodes[i].probability < nodes[node_right_idx].probability):
					node_right_idx = i
			node_right = nodes.pop(node_right_idx)

			if node_right_idx < node_left_idx:
				tmp = node_right
				node_right = node_left
				node_left = tmp

			cases = node_left.cases + node_right.cases
			probability = node_left.probability + node_right.probability
			parent = HuffmanTree(cases, probability, left=node_left, right=node_right)
			nodes.insert(min(node_left_idx, node_right_idx), parent)
		return nodes[0]

	def get_huffman_codewords(self, prefix_code=''):
		""" Returns a list of pairs, each consisting out of a char and its huffman code """
		if len(self.cases) == 1:
			if prefix_code == '': prefix_code = '0'
			return {self.cases[0]: prefix_code}
		else:
			return {**self.left.get_huffman_codewords(prefix_code+"1"), **self.right.get_huffman_codewords(prefix_code+"0")}

def char_occurrences_in(string):
	""" Returns a list of pairs, each consisting out of a char and its number of occurrences in the string """
	probs = dict()
	for char in string:
		if not char in probs:
			probs[char] = 1
		else:
			probs[char] = probs[char] + 1	
	return probs

def char_probabilities_in(string, char_occurrences=None):
	""" Returns a list of pairs, each consisting out of a char and its probability in the string """
	if not char_occurrences:
		char_occurrences = char_occurrences_in(string)
	return {char: Fraction(char_occurrences[char], len(string)) for char in char_occurrences}

def encode(string, codewords=None, format_hex=False):
	""" Encodes string with the passed codewords. Codewords are generated if not present """
	if not codewords:
		ht = HuffmanTree.from_char_probabilities(char_probabilities_in(string))
		codewords = ht.get_huffman_codewords()
	encoded = ""
	for char in string:
		encoded += codewords[char]
	if format_hex: 
		encoded = bin_str_to_hex_str(encoded)
	return encoded

def entropy(string):
	H = 0
	for char,prob in char_probabilities_in(string).items():
		H += prob * math.log2(1/prob)
	return H

def avrg_codelen(string):
	char_probs = char_probabilities_in(string)
	ht = HuffmanTree.from_char_probabilities(char_probs)
	codes = ht.get_huffman_codewords()
	L = 0
	for char,prob in char_probs.items():
		L += prob * len(codes[char])
	return L

#############
# CLI Utils #
#############

def bin_str_to_hex_str(bin_str):
	hex_str = ''
	nibble = bin_str[-4::]
	while nibble != '':
		bin_str = bin_str[:-4]
		hex_str = hex(int(nibble,2))[2:] + hex_str
		nibble = bin_str[-4::]
	return hex_str

def generate_table_rows(string, columns_with_options, sortby=None, reverse=False):
	# Generate data required by default
	char_occurrences = char_occurrences_in(string)
	char_probs = char_probabilities_in(string, char_occurrences=char_occurrences)
	ht = HuffmanTree.from_char_probabilities(char_probs)
	codes = ht.get_huffman_codewords()

	# Sort rows
	chars = sorted(char_occurrences)
	if sortby == COLUMN_CODES: chars = sorted(chars, key=lambda char: (len(codes[char]), int(codes[char],2)))
	elif sortby == COLUMN_OCCURRENCES: chars = sorted(chars, key=lambda char: char_occurrences[char])
	elif sortby == COLUMN_REL_PROBS: chars = sorted(chars, key=lambda char: char_probs[char])
	elif sortby == COLUMN_CODE_LENGTHS: chars = sorted(chars, key=lambda char: len(codes[char]))

	# Reverse rows
	if reverse: chars = reversed(chars)

	# Generate rows
	for i,char in enumerate(chars):
		row = [char]
		for column, options in columns_with_options:
			if column == COLUMN_CODES:
				code = codes[char]
				if options and options.get('hex', False): code = bin_str_to_hex_str(code) 
				row.append(code)
			elif column == COLUMN_OCCURRENCES:
				row.append(str(char_occurrences[char]))
			elif column == COLUMN_REL_PROBS:
				prob = char_probs[char]
				if options and 'f' in options: prob = "{{{}}}".format(options['f']).format(float(prob))
				row.append(str(prob))
			elif column == COLUMN_CODE_LENGTHS:
				row.append(str(len(codes[char])))
		yield row

def create_table(rows, columns_with_options):
	from prettytable import PrettyTable

	# Create Table Headers
	headers = ['Chars']
	for column, options in columns_with_options:
		if options and 'name' in options: headers.append(options['name'])
		else: headers.append(DEFAULT_COLUMN_HEADERS[column])

	# Create Table
	table = PrettyTable(headers)
	for row in rows: table.add_row(row)
	return table

def handle_input(input, func):
	""" Executes func with input, uses stdin as a fallback """
	if input:
		func(input)
	else:
		line = sys.stdin.readline().rstrip()
		while line != '':
			func(line)
			line = sys.stdin.readline().rstrip()

################
# CLI Commands #
################

def cmd_encode(argv):
	parser = argparse.ArgumentParser(description='Encode string using Huffman codes', usage='%(prog)s {} [-h] [string] [-x]'.format(CMD_ENCODE))
	parser.add_argument('string', nargs='?', type=str, default=None, help='The string to encode. Omit to use stdin'),
	parser.add_argument('-x', '--hex', action='store_true', help='Output in hex')
	args = parser.parse_args(argv)

	def execute(input):
		encoded = encode(input, format_hex=args.hex)
		print(encoded)

	handle_input(args.string, execute)
		

def cmd_table(argv):
	parser = argparse.ArgumentParser(description='Outputs table with Huffman Codes related data', usage='%(prog)s {} [-h] [string] [-c] [-s] [-r] [-p]'.format(CMD_TABLE))
	parser.add_argument('string', nargs='?', type=str, default=None, help='String Huffman Codes are generated from. Omit to use stdin'),
	parser.add_argument('-c', '--columns', type=str, help='Included Columns in that order: [{}].'.format('|'.join(COLUMNS)))
	parser.add_argument('-s', '--sort', type=str, help='Sort rows by column: [{}]'.format('|'.join(COLUMNS)))
	parser.add_argument('-r', '--reversed', action='store_true', help='Sort rows in reversed order')
	parser.add_argument('-p', '--pretty-print', action='store_true', help='Pretty prints table')
	args = parser.parse_args(argv)

	# Defaults
	if not args.columns: args.columns = COLUMN_CODES

	# Parse args.columns
	columns_with_options = []
	for param in re.findall("(.(?:\{[^\{\}]*\})?)", args.columns):
		# Extract column and options 
		column_option_pair = list(re.findall("(.)(\{[^\{\}]*\})?",param)[0])
		if not column_option_pair[0] in COLUMNS:
			 raise Exception("Unknown column: '{}'. Valid columns are: [{}]".format(column_option_pair[0], '|'.join(COLUMNS)))
		if column_option_pair[1]:
			column_option_pair[1] = ast.literal_eval(column_option_pair[1])
		columns_with_options.append(column_option_pair)

	def execute(input):
		rows = generate_table_rows(input, columns_with_options, args.sort, args.reversed)
		if args.pretty_print:
			table = create_table(rows, columns_with_options)
			print(table)
		else: 
			for row in rows: print(';'.join(row))

	handle_input(args.string, execute)
	
def cmd_entropy(argv):
	parser = argparse.ArgumentParser(description='Calculates the entropy of the input string', usage='%(prog)s {} [-h] [string]'.format(CMD_ENTROPY))
	parser.add_argument('string', nargs='?', type=str, default=None, help='String to calculate entropy for. Omit to use stdin'),
	args = parser.parse_args(argv)

	handle_input(args.string, lambda input: print(float(entropy(input))))

def cmd_avrg_codelen(argv):
	parser = argparse.ArgumentParser(description='Calculates the average Huffman code length', usage='%(prog)s {} [-h] [string]'.format(CMD_AVRG_CODE_LENGTH))
	parser.add_argument('string', nargs='?', type=str, default=None, help='String to calculate the average Huffman code length for. Omit to use stdin'),
	args = parser.parse_args(argv)

	handle_input(args.string, lambda input: print(float(avrg_codelen(input))))

def cmd_redundancy(argv):
	parser = argparse.ArgumentParser(description='Calculates redundancy of the Huffman encoding compared to theoretical optimal encoding (Entropy)', usage='%(prog)s {} [-h] [string]'.format(CMD_REDUNDANCY))
	parser.add_argument('string', nargs='?', type=str, default=None, help='String to calculate the redundancy of Huffman encoding for. Omit to use stdin'),
	args = parser.parse_args(argv)

	handle_input(args.string, lambda input: print(float(avrg_codelen(input) - entropy(input))))
		
########
# Main #
########

CMD_ENCODE = 'encode'
CMD_TABLE = 'table'
CMD_ENTROPY = 'entropy'
CMD_AVRG_CODE_LENGTH = 'avrg_codelen'
CMD_REDUNDANCY = 'redundancy'
COMMANDS = [CMD_ENCODE, CMD_TABLE, CMD_ENTROPY, CMD_AVRG_CODE_LENGTH, CMD_REDUNDANCY]

if __name__ == "__main__":
	import argparse, sys
	# Parse CLI Arguments
	parser = argparse.ArgumentParser(description='Huffman Code Utility')
	parser.add_argument('command', type=str, choices=COMMANDS, help='Subcommand to run')
	args = parser.parse_args(sys.argv[1:2])

	if args.command == CMD_ENCODE:
		cmd_encode(sys.argv[2:])
	elif args.command == CMD_TABLE:
		cmd_table(sys.argv[2:])
	elif args.command == CMD_ENTROPY:
		cmd_entropy(sys.argv[2:])
	elif args.command == CMD_AVRG_CODE_LENGTH:
		cmd_avrg_codelen(sys.argv[2:])
	elif args.command == CMD_REDUNDANCY:
		cmd_redundancy(sys.argv[2:])