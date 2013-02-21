#!/usr/bin/env python3
"""
@author Anton Osten
pylexemes project
"""

import argparse, re, os
from segmentparser import SegmentParser

argparser = argparse.ArgumentParser()
group = argparser.add_mutually_exclusive_group()
group.add_argument('-s', '--segment', type=str, help='segment symbol, name, or feature(s)')
group.add_argument('-ls', '--list', type=str, choices=['s', 'n', 'f'], help='list avaliable symbols (s), names (n), or features')
group.add_argument('-d', '--duplicates', action='store_true', help='displays duplicates (segments with the same feature sets) in the database')
args = argparser.parse_args()

sp = SegmentParser()

def main():
	if args.segment:
		print(lookup(args.segment.casefold()))
	elif args.list:
		print(list_opts(args.list))
	elif args.duplicates:
		print(lookup('duplicates'))
	# interactive
	else:
		print("Please enter a segment name, symbol, feature(s), or a command. Enter 'help' to see all available commands.")
		query = input("> ").casefold()
		while ('quit' not in query):
			if 'list' in query:
				print("{} segments in the database".format(len(sp.segments)))
				print("Enter 's' to see all available symbols, 'n' to see all available segment names, or 'f' to see all possible feature keys.")
				list_query = input("> ")
				print(list_opts(list_query))
			elif re.match('list [snf]', query):
				list_query = re.search('(?<= )[snf]', query).group(0)
				print(list_opts(list_query))
			elif 'help' in query:
				help()
			else:
				print(lookup(query))
			main()
		quit('Have a nice day!')

def lookup(query):
	output = ''
	# just one symbol
	if query in sp.symbols:
		output += 'Name: {}\nFeatures: {}'.format(sp.names[query], sp.true_features[query])
	# multiple symbols
	elif re.match('\w \w', query):
		symbols = re.findall('\w', query)
		features = []
		for symbol in symbols:
			output += 'Symbol: {}\n'.format(symbol)
			output += 'Name: {}\n'.format(sp.names[symbol])
			s_features = sp.true_features[symbol]
			output += 'Features: {}\n-----\n'.format(s_features)
			features.append(s_features)
		output += shared_features(symbols, features)
	# exact match for a name
	elif query in list(sp.names.values()):
		symbol = [n for n in sp.names if sp.names[n] == query][0]
		features = sp.true_features[symbol]
		output =  'Symbol: {}\nFeatures: {}'.format(symbol, features)
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
		features = []
		for s in symbols:
			name = sp.names[s]
			s_features = sp.true_features[s]
			features.append(s_features)
			output += 'Symbol: {}\nName: {}\nFeatures: {}\n-----'.format(s, name, s_features)
		features = [f for s in features for f in s]
		output += shared_features(symbols, features)
	# partial name matching
	elif [segment for segment in sp.names if query in sp.names[segment]] != []:
		matches = [segment for segment in sp.names if query.casefold() in sp.names[segment]]
		features = []
		for m in matches:
			output += 'Symbol: {}\n'.format(m)
			output += 'Name: {}\n'.format(sp.names[m])
			output += 'Features: {}\n'.format(sp.true_features[m])
			features.append(sp.true_features[m])
			output += '-----\n'
		output += shared_features(matches, features)
	# duplicates
	elif query == 'duplicates':
		output = sp.duplicates
	else:
		output = 'No match found'
	return output

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

def shared_features(segments, features):
	doc = "Finds features shared between all segments"
	if len(segments) == 1:
		return ''
	features = [f for s in features for f in s]
	shared_features = [f for f in features if features.count(f) == len(segments)]
	if shared_features != []:
		return 'Shared features: {}'.format(set(shared_features))
	else:
		return 'No shared features'

def list_opts(query):
	doc = "List options"
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
You can enter 'list' to see all the available options for each query.
If you want to see duplicates (segments with the same feature sets) currently in the database, enter 'duplicates'.\n""")
	input('press any key to return to main menu\n')

if __name__ == '__main__':
	main()	