#!/bin/sh
# Anton Osten
# http://ostensible.me

import json

class LexemeParser():

	def __init__(self):
		try:
			self._lexemes = json.load(open("lexemes.json"))
		except ValueError:
			quit("It seems that there is something wrong in the json file for lexemes. Check it over and run me again.")
		self._langs = []
		self._forms = []

		for n in self._lexemes:
			self._langs.append(n['lang'])
			self._forms.append(n['form'])

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

		