#!/usr/bin/env python3
# pylexemes
# UNFINISHED

import json, argparse

argparser = argparse.ArgumentParser()
argparser.add_argument('-l', '--lang', type=str, help='Language name or code')
argparser.add_argument('--list', action='store_true', help='List all languages in the database')
args = argparser.parse_args()

def main():
	try:
		langs = json.load(open('langs.json'))
	except FileNotFoundError:
		quit('No langs.json file found. Quitting...')
	if args.lang:
		print(lookup(langs, args.lang))
	elif args.list:
		print(list_langs(langs))
	else:
		interactive(langs)

def interactive(langs):
	query = input('Please enter a language name or its three letter ISO code. Type list for a list of languages or quit to quit.\n')
	while query != 'quit':
		if query == 'list':
			print(list_langs(langs))
		else:
			print(lookup(langs, query))
		interactive(langs)
	quit('Bye now!')

def lookup(langs, query):
	if query.title() in langs:
		output = 'ISO code: {}'.format(langs[query.title()])
	else:
		try:
			output = [lang for lang in langs if langs[lang] == query][0]
		except IndexError:
			output = 'No language with that ISO code found.'
	return output

def list_langs(langs):
	output = ''
	for lang in langs:
		output += '{}, {}\n'.format(lang, langs[lang])
	output += '{} languages in total'.format(len(langs))
	return output

if __name__ == '__main__':
	main()