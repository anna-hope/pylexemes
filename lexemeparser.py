#!/usr/bin/env python3
# Anton Osten
# http://ostensible.me

import json, re

class LexemeParser:

	def __init__(self, f=None):

		if f != None:
			lexemefile = f
		else:
			lexemefile = 'lexemes.json'

		try:
			self._lexemes = json.load(open(lexemefile))
		except ValueError as ve:
			self.somethingwrong(e)
		except FileNotFoundError:
			self.create_dummy()
			
		self._lang_names = []
		self._lang_codes = []
		raw_forms = []

		for n in self._lexemes:
			try:
				self._lang_names.append(n['lang_name'])
				self._lang_codes.append(n['lang_code'])
				lang_forms = re.findall('\w+', n['forms'])
				raw_forms.append((lang_forms, n['lang_code']))
			except KeyError as ke:
				self.somethingwrong(ke)

		self._forms = self.sort_forms(raw_forms)
		self.store_lang_info(self._lang_names, self._lang_codes)

	def lexemes():
	    doc = "Lexemes."
	    def fget(self):
	        return self._lexemes
	    def fset(self, value):
	        self._lexemes = value
	    def fdel(self):
	        del self._lexemes
	    return locals()
	lexemes = property(**lexemes())

	def lang_names():
	    doc = "Language names."
	    def fget(self):
	        return self._lang_names
	    def fset(self, value):
	        self._lang_names = value
	    def fdel(self):
	        del self._lang_names
	    return locals()
	lang_names = property(**lang_names())

	def lang_codes():
	    doc = "ISO codes for languages"
	    def fget(self):
	        return self._lang_codes
	    def fset(self, value):
	        self._lang_codes = value
	    def fdel(self):
	        del self._lang_codes
	    return locals()
	lang_codes = property(**lang_codes())

	def forms():
	    doc = "Forms."
	    def fget(self):
	        return self._forms
	    def fset(self, value):
	        self._forms = value
	    def fdel(self):
	        del self._forms
	    return locals()
	forms = property(**forms())

	def sort_forms(self, raw_forms):
		numlangs = len(raw_forms)
		numforms = len(raw_forms[0][0])
		sorted_forms = []
		for num in range(numforms):
			cur_forms = []
			for n, lang in enumerate(raw_forms):
				cur_forms.append(raw_forms[n][0][num])
			sorted_forms.append(cur_forms)
		return sorted_forms

	def create_dummy(self):
		doc = "Creates a dummy lexemes.json file if one isn't found."
		print("JSON file for lexemes was not found. Creating a dummy.")
		dummydata = [{"lang_name": "alalalian", "lang_code": "???", "forms": "dvronts"},
		 {"lang_name": "boblabian", "lang_code": "???", "forms": "txovant"}, 
		 {"lang_name": "cycoclian", "lang_code": "???", "forms": "lwa"}]
		json.dump(dummydata, open('dummydata.json', 'w'))
		self._lexemes = json.load(open('dummydata.json', 'r'))

	def store_lang_info(self, lang_names, lang_codes):
		doc = "Stores language name and three letter ISO code in a langs.json file for future reference."
		try:
			langs = json.load(open('langs.json'))
		except:
			langs = json.loads('{}')
		for lang_name, lang_code in zip(lang_names, lang_codes):
			if '?' not in lang_code and lang_name.title() not in langs:
				# check if this language isn't named differently in the database
				match_code = [lang for lang in langs if langs[lang] == lang_code.casefold()]
				if match_code == []:
					# if there isn't  a language with that code, we'll add it
					langs[lang_name.title()] = lang_code.casefold()
				else:
					# if there is a language with that code, but it's named differently, we could change the current instance of it
					# but I'm sure I want to do that
					pass
		if langs != json.load(open('langs.json')):
			json.dump(langs, open('langs.json', 'w'))

	def somethingwrong(self, e):
		doc = "Invoked when there is something wron in the lexemes.json file."
		print("Error with %s" % e)
		quit("\nIt seems that there is something wrong in the JSON file for lexemes. Check it over and run me again.")