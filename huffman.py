# -*- coding: UTF-8

import math
from fractions import Fraction

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
		nodes = sorted(list(map(lambda x: HuffmanTree(x[0], x[1]) , char_probs)), key=lambda x: x.probability)
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

	def get_huffman_codewords(self, prefix_code=""):
		""" Returns a list of pairs, each consisting out of a char and its huffman code """
		if len(self.cases) == 1:
			return {self.cases[0]: prefix_code}
		else:
			return {**self.left.get_huffman_codewords(prefix_code+"1"), **self.right.get_huffman_codewords(prefix_code+"0")}

def char_occurrences(string):
	""" Returns a list of pairs, each consisting out of a char and its number of occurences in the string """
	probs = dict()
	for char in string:
		if not char in probs:
			probs[char] = 1
		else:
			probs[char] = probs[char] + 1	
	return sorted(list(map(lambda c: (c,probs[c]), probs)))

def char_probabilities(string, abs_probs=None):
	""" Returns a list of pairs, each consisting out of a char and its probability in the string """
	if not abs_probs:
		abs_probs = char_occurrences(string)

	return list(map(lambda x: (x[0], Fraction(x[1],len(string))), abs_probs))

def encode(string, codewords=None):
	if not codewords:
		ht = HuffmanTree.from_char_probabilities(char_probabilities(string))
		codewords = ht.get_huffman_codewords()
	encoded = ""
	for char in string:
		encoded += codewords[char]
	return encoded

########
# Main #
########

column_names = {
	'chars': 'Chars',
	'probs': 'P',
	'codewords': 'Codewords',
	'code-lengths': 'Lengths',
	'occurences': 'n'
}

def print_table(format, chars, abs_probs = None, rel_probs = None, codewords = None):
	from prettytable import PrettyTable
	import re

	table = PrettyTable()

	columns = ['chars']
	sortby = column_names['chars']
	probs_format = None

	for segment in format.split(','):
		option, parameters = segment.split('=') if '=' in segment else (segment, '')
		parameters = list(filter(lambda x: x != '', re.split("(.(?:\{.*\})?)", parameters)))

		if option in ['c', 'columns']:
			for param in parameters:
				if param.startswith('p'): 
					columns.append('probs')
					format = list(filter(lambda x: x!='p' and x != '', re.split(".\{(.*)\}", param)))
					if format != []: probs_format = format[0]
				elif param.startswith('w'): columns.append('codewords')
				elif param.startswith('l'): columns.append('code-lengths')
				elif param.startswith('o'): columns.append('occurences')
		elif option in ['s', 'sortby']:
			for param in parameters:
				if param.startswith('p'): sortby = column_names['probs']
				elif param.startswith('w'): 
					sortby = column_names['codewords']
					table.sort_key = lambda x: [len(x[columns.index('codewords')+1]), int(x[columns.index('codewords')+1], 2)]
				elif param.startswith('l'): sortby = column_names['code-lengths']
				elif param.startswith('o'): sortby = column_names['occurences']
		elif option in ['r', 'reverse']:
			table.reversesort = True

	# Defaults
	if len(columns) == 1:
		columns.append('probs')

	# Add chars column
	table.add_column(column_names['chars'], chars)

	# Add optional columns
	for column in columns:
		if column == 'probs':
			probs = rel_probs
			if probs_format: probs = list(map(lambda x: "{{{}}}".format(probs_format).format(float(x)), rel_probs))
			
			table.add_column(column_names[column], probs)
		elif column == 'codewords':
			table.add_column(column_names[column], codewords)
		elif column == 'code-lengths':
			lengths = list(map(lambda x: len(x), codewords))
			table.add_column(column_names[column], lengths)
		elif column == 'occurences':
			table.add_column(column_names[column], abs_probs)
		
	table.sortby = sortby
	print(table)

if __name__ == "__main__":
	# Parse CL Arguments
	import argparse, sys
	parser = argparse.ArgumentParser(description='Calculate Huffman Codes')
	parser.add_argument('input', nargs='?', type=str, default=None, help='The string to encode')
	parser.add_argument('-e', '--show-encoded', action='store_true', help='Show the encoded string')
	parser.add_argument('-d', '--data', help="Shows generated data in formated table: columns=[p{<format>}|w|l|o]+,sortby=[p|w|l|o],reverse")
	parser.add_argument('-t', '--tree', help="Shows resulting huffman tree", action="store_true")
	args = parser.parse_args()

	input = args.input
	if input == None: 
		input = sys.stdin.read().rstrip()

	# Calculate Probabilites
	char_abs_probs_pairs = sorted(char_occurrences(input), key=lambda x : x[0])
	chars = list(map(lambda x: x[0], char_abs_probs_pairs))
	abs_probs = list(map(lambda x: x[1], char_abs_probs_pairs))

	char_prob_pairs = char_probabilities(input, char_abs_probs_pairs)
	rel_probs = list(map(lambda x: x[1], char_prob_pairs))

	# Calculate huffman codes
	huffman_tree = HuffmanTree.from_char_probabilities(char_prob_pairs)
	char_code_pairs = huffman_tree.get_huffman_codewords()
	codewords = list(map(lambda x: char_code_pairs[x], chars))	

	# Output requested data
	if not args.show_encoded and not args.data and not args.tree:
		args.show_encoded = True
	if args.data:
		print_table(args.data, chars, abs_probs, rel_probs, codewords)
	if args.tree:
		print(huffman_tree)
	if args.show_encoded:
		encoded = encode(input, char_code_pairs)
		print(encoded)