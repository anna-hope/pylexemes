#!/usr/bin/env python3

import json, argparse, os

argparser = argparse.ArgumentParser()
argparser.add_argument('-f', '--filename', type=str, help='specify a filename for the lexemes database')
args = argparser.parse_args()

def main():
	try: 
		langs = json.load(open('langs.json'))
	except FileNotFoundError:
		langs = {}

	if args.filename:
		if '.json' in args.filename:
			lexemesfile = args.filename
		else:
			lexemesfile = args.filename + '.json'
	else:
		lexemesfile = 'lexemes.json'

	try:
		output = 'The following data is already in the file:\n'
		lexemes = json.load(open(lexemesfile))
		for l in lexemes:
			output += '{}\n'.format(list(l.values()))
		print(output)
	except FileNotFoundError:
		lexemes = []

	lang_name = input('Please enter a language name:\n> ').title()
	if lang_name == 'quit' or lang_name == '':
		quit()

	try:
		lang_code = langs[lang_name]
	except KeyError:
		print('Please enter ')
		lang_code = input('Please enter its three letter ISO code:\n> ').casefold()
	forms = input('Please enter forms separated by a comma (a,b,c,etc.):\n> ').casefold()

	entry = {"lang_name": lang_name, "lang_code": lang_code, "forms": forms}
	add_entry(lexemesfile, entry, lexemes)
	response = input("Would you like to add another entry? (y/n)\n> ").casefold()
	if 'y' in response:
		main()
	else:
		quit('Okay. See you later then!')

def add_entry(lexemesfile, entry, lexemes):
	if entry['lang_name'] in [lexeme['lang_name'] for lexeme in lexemes]:
		match = [lexeme for lexeme in lexemes if lexeme['lang_name'] == entry['lang_name']][0]
		lexemes.remove(match)
		lexemes.append(entry)
	else:
		lexemes.append(entry)
	json.dump(lexemes, open(lexemesfile, 'w'))

if __name__ == "__main__":
	main()