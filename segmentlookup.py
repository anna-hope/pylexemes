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
		query = input("Please enter a segment name, symbol, or feature(s). Enter 'list' for a list of queries, 'help' for help,  or 'quit' to quit.\n")
		while (query != 'quit'):
			if query == 'list':
				list_query = input("Enter 's' to see all available symbols, 'n' to see all available segment names, or 'f' to see all possible feature keys.\n".format(len(sp.segments)))
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
		name = sp.names[query]
		features = sp.true_features[query]
		return ('Name: {}\nFeatures: {}'.format(name, features))
	elif query in list(sp.names.values()):
		symbol = [n for n in sp.names if sp.names[n] == query][0]
		features = sp.true_features[symbol]
		return (('Symbol: {}\nFeatures: {}').format(symbol, features))
	# if it matches a regexp for feature notation
	elif re.match("\w+ [\+-0]", query):
		fs_query = re.findall("\w+ [\+-0]", query)
		fs = [parse_feature(f) for f in fs_query]
		symbols = []
		for segment in sp.features:
			# print(sp.features[segment])
			if all(f in list(sp.features[segment].items()) for f in fs):
				symbols.append(segment)
		if symbols == []:
			return ('No match found')
		output = ''
		for s in symbols:
			name = sp.names[s]
			features = sp.true_features[s]
			output += 'Symbol: {}\nName: {}\nFeatures: {}\n-----\n'.format(s, name, features)
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
	output = ''
	if query == 's':
		output += '\n'
		for s in sp.symbols:
			output += '{} '.format(s)
	elif query == 'n':
		output += '\n'
		for n in sp.names.values():
			output += '{}\n'.format(n)
	elif query == 'f':
		output += '\n'
		for f in sp.segments[0]['features'].keys():
			output += '{}\n'.format(f)
	elif query == 'num':
		output += '{}\n'.format(len(sp.segments))
	else:
		output = 'Invalid query.'
	return output

def help():
	os.system('cls' if os.name == 'nt' else 'clear')
	print("""This is an interface for the segment database used in pylexemes.
You can search for an IPA symbol of a segment (for example, 's'), its name (like 'voiced dental fricative'), or features (like 'cons +' or 'cont -').
Features can be combined to see all the segments who share all the features listed (like 'cons +, cont -').
You can enter 'l' or 'list' to see all the available options for each query.\n""")
	input('press any key to return to main menu\n')

if __name__ == '__main__':
	main()	