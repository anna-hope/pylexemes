#!/bin/sh
# Anton Osten
# http://ostensible.me

import json

class LexemeParser():

	def __init__(self):
		try:
			self._lexemes = json.load(open("lexemes.json"))
		except ValueError as ve:
			self.somethingwrong(e)
		except FileNotFoundError:
			self.create_dummy()
			
		self._langs = []
		self._forms = []

		for n in self._lexemes:
			try:
				self._langs.append(n['lang'])
				self._forms.append(n['form'])
			except KeyError as ke:
				self.somethingwrong(ke)

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

	def langs():
	    doc = "Languages."
	    def fget(self):
	        return self._langs
	    def fset(self, value):
	        self._langs = value
	    def fdel(self):
	        del self._langs
	    return locals()
	langs = property(**langs())

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

	def create_dummy(self):
		doc = "Creates a dummy lexemes.json file if one isn't found."
		print("JSON file for lexemes was not found. Creating a dummy.")
		dummydata = [{"lang": "aaa", "form": "druvantes"}, {"lang": "bbb", "form": "txuvantes"}, {"lang": "ccc", "form": "---vande-"}]
		json.dump(dummydata, open('lexemes.json', 'w'))
		self._lexemes = json.load(open('lexemes.json', 'r'))

	def somethingwrong(self, e):
		doc = "Invoked when there is something wron in the lexemes.json file."
		print("Error with %s" % e)
		quit("\nIt seems that there is something wrong in the JSON file for lexemes. Check it over and run me again.")



		