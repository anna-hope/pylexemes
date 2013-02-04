#!/usr/bin/env python3
"""
@author Anton Osten
"""

import argparse, re, os
from phonemeparser import PhonemeParser

argparser = argparse.ArgumentParser()
group = argparser.add_mutually_exclusive_group()
group.add_argument('-p', '--phoneme', type=str, help='phoneme symbol, name, or feature(s)')
group.add_argument('-l', '--list', type=str, choices=['s', 'n', 'f'], help='list avaliable symbols (s), names (n), or features')
args = argparser.parse_args()

pp = PhonemeParser()

def main():
	if args.phoneme:
		print(lookup(args.phoneme))
	elif args.list:
		print(list_opts(args.list))
	# interactive
	else:
		query = input("Please enter a phoneme name, symbol, or feature(s). Enter 'list' for a list of queries, 'help' for help,  or 'quit' to quit.\n")
		while (query != 'quit'):
			if query == 'l' or query == 'list':
				list_query = input("Enter 's' to see all available symbols, 'n' to see all available phoneme names, or 'f' to see all possible feature keys.\n")
				print(list_opts(list_query))
			elif re.match('l|list [snf]', query):
				list_query = re.search('(?<= )[snf]', query).group(0)
				print(list_opts(list_query))
			elif query == 'help' or query == 'h':
				help()
			else:
				print(lookup(query))
			main()
		quit('Have a nice day!')

def lookup(query):
	if query in pp.symbols:
		index = pp.symbols.index(query)
		name = pp.names[index]
		features = pp.features[index]
		return ('Name: {}\nFeatures: {}'.format(name, features))
	elif query in pp.names:
		index = pp.names.index(query)
		symbol = pp.symbols[index]
		features = pp.features[index]
		return (('Symbol: {}\nFeatures: {}').format(symbol, features))
	# if it matches a regexp for feature notation
	elif re.match("\w+ [\+-0]", query):
		fs_query = re.findall("\w+ [\+-0]", query)
		fs = []
		for f in fs_query:
			fs.append(parse_feature(f))
		indexes = []
		for phoneme in pp.features:
			if all(f in phoneme for f in fs):
				indexes.append(pp.features.index(phoneme))
		if indexes == []:
			return ('No match found')
		output = ''
		for i in indexes:
			symbol = pp.symbols[i]
			name = pp.names[i]
			features = pp.features[i]
			output += 'Symbol: {}\nName: {}\nFeatures: {}\n-----\n'.format(symbol, name, features)
		return output
	else:
		return ('No match found')

def parse_feature(feature):
	prop = re.search('\w+', feature).group(0)
	value = re.search('[\+-0]', feature).group(0)
	if value == '+':
		value = True
	elif value == '-':
		value = False
	else:
		value = 0
	return (prop, value)

def list_opts(query):
	if query == 's':
		return pp.symbols
	elif query == 'n':
		return pp.names
	elif query == 'f':
		return list(pp.phonemes[0]['features'].keys())

def help():
	os.system('cls' if os.name == 'nt' else 'clear')
	print("""This is an interface for the phoneme database used in pylexemes.
You can search for an IPA symbol of a phoneme (for example, 's'), its name (like 'voiced dental fricative'), or features (like 'cons +' or 'cont -').
Features can be combined to see all the phonemes who share all the features listed (like 'cons +, cont -').
You can enter 'l' or 'list' to see all the available options for each query.\n""")
	input('press any key to return to main menu\n')

if __name__ == '__main__':
	main()	