#!/usr/bin/env python3
"""
@author Anton Osten
"""

import argparse, re, os
from segmentparser import SegmentParser

argparser = argparse.ArgumentParser()
group = argparser.add_mutually_exclusive_group()
group.add_argument('-s', '--segment', type=str, help='segment symbol, name, or feature(s)')
group.add_argument('-ls', '--list', type=str, choices=['s', 'n', 'f'], help='list avaliable symbols (s), names (n), or features')
args = argparser.parse_args()

sp = SegmentParser()

def main():
	if args.segment:
		print(lookup(args.segment))
	elif args.list:
		print(list_opts(args.list))
	# interactive
	else:
		query = input("{} segments in the database.\nPlease enter a segment name, symbol, or feature(s). Enter 'list' for a list of queries, 'help' for help,  or 'quit' to quit.\n".format(len(sp.segments)))
		while (query != 'quit'):
			if query == 'list':
				list_query = input("Enter 's' to see all available symbols, 'n' to see all available segment names, or 'f' to see all possible feature keys.\n")
				print(list_opts(list_query))
			elif re.match('list [snf]', query):
				list_query = re.search('(?<= )[snf]', query).group(0)
				print(list_opts(list_query))
			elif query == 'help':
				help()
			else:
				print(lookup(query))
			main()
		quit('Have a nice day!')

def lookup(query):
	if query in sp.symbols:
		index = sp.symbols.index(query)
		name = sp.names[index]
		features = sp.features[index]
		return ('Name: {}\nFeatures: {}'.format(name, features))
	elif query in sp.names:
		index = sp.names.index(query)
		symbol = sp.symbols[index]
		features = sp.features[index]
		return (('Symbol: {}\nFeatures: {}').format(symbol, features))
	# if it matches a regexp for feature notation
	elif re.match("\w+ [\+-0]", query):
		fs_query = re.findall("\w+ [\+-0]", query)
		fs = [fs.append(parse_feature(f) for f in fs_query]
		indexes = []
		for segment in sp.features:
			if all(f in segment for f in fs):
				indexes.append(sp.features.index(segment))
		if indexes == []:
			return ('No match found')
		output = ''
		for i in indexes:
			symbol = sp.symbols[i]
			name = sp.names[i]
			features = sp.features[i]
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
		return sp.symbols
	elif query == 'n':
		return sp.names
	elif query == 'f':
		return list(sp.phonemes[0]['features'].keys())

def help():
	os.system('cls' if os.name == 'nt' else 'clear')
	print("""This is an interface for the segment database used in pylexemes.
You can search for an IPA symbol of a segment (for example, 's'), its name (like 'voiced dental fricative'), or features (like 'cons +' or 'cont -').
Features can be combined to see all the phonemes who share all the features listed (like 'cons +, cont -').
You can enter 'l' or 'list' to see all the available options for each query.\n""")
	input('press any key to return to main menu\n')

if __name__ == '__main__':
	main()	