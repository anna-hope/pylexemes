#!/bin/sh
# Anton Osten
# http://ostensible.me

import json

class PhonemeParser():

	def __init__(self):
		try:
			phonemes = json.load(open("phonemes.json"))
		except Exception as e:
			self.somethingwrong(e)
		
		self._symbols = []
		self._features = []

		try:
			for n in phonemes:
				self._symbols.append(n['symbol'])
				self._features.append(list(n['features'].values()))
		except Exception as e:
			self.somethingwrong(e)

	
	def symbols():
	    doc = "Phoneme symbols."
	    def fget(self):
	        return self._symbols
	    def fset(self, value):
	        self._symbols = value
	    def fdel(self):
	        del self._symbols
	    return locals()
	symbols = property(**symbols())

	def features():
	    doc = "Phoneme features."
	    def fget(self):
	        return self._features
	    def fset(self, value):
	        self._features = value
	    def fdel(self):
	        del self._features
	    return locals()
	features = property(**features())

	def somethingwrong(self, e):
		doc = "Invoked when something goes wrong with the phonemes.json file."
		print(e)
		quit('It seems that there is something wrong with the json file for phonemes. Check it over and run me again.')
