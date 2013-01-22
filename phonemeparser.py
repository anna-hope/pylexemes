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
		self._consonants = phonemes['consonants']
		self._vowels = phonemes['vowels']
		self._cons_symbols = []
		self._cons_features = []
		self._vwl_symbols = []
		self._vwl_features = []

		try:
			for n in self._consonants:
				self._cons_symbols.append(n['symbol'])
				self._cons_features.append(list(n['features'].values()))

			for n in self._vowels:
				self._vwl_symbols.append(n['symbol'])
				self._vwl_features.append(list(n['features'].values()))
		except Exception as e:
			self.somethingwrong(e)

	def consonants():
	    doc = "Consonants."
	    def fget(self):
	        return self._consonants
	    def fset(self, value):
	        self._consonants = value
	    def fdel(self):
	        del self._consonants
	    return locals()
	consonants = property(**consonants())

	def vowels():
	    doc = "Vowels."
	    def fget(self):
	        return self._vowels
	    def fset(self, value):
	        self._vowels = value
	    def fdel(self):
	        del self._vowels
	    return locals()
	vowels = property(**vowels())

	def cons_symbols():
	    doc = "Symbols for consonants."
	    def fget(self):
	        return self._cons_symbols
	    def fset(self, value):
	        self._cons_symbols = value
	    def fdel(self):
	        del self._cons_symbols
	    return locals()
	cons_symbols = property(**cons_symbols())

	def cons_features():
	    doc = "Consonant features."
	    def fget(self):
	        return self._cons_features
	    def fset(self, value):
	        self._cons_features = value
	    def fdel(self):
	        del self._cons_features
	    return locals()
	cons_features = property(**cons_features())

	def vwl_symbols():
	    doc = "Symbols for vowels."
	    def fget(self):
	        return self._vwl_symbols
	    def fset(self, value):
	        self._vwl_symbols = value
	    def fdel(self):
	        del self._vwl_symbols
	    return locals()
	vwl_symbols = property(**vwl_symbols())

	def vwl_features():
	    doc = "Vowel features."
	    def fget(self):
	        return self._vwl_features
	    def fset(self, value):
	        self._vwl_features = value
	    def fdel(self):
	        del self._vwl_features
	    return locals()
	vwl_features = property(**vwl_features())

	def somethingwrong(self, e):
		doc = "Invoked when something goes wrong with the phonemes.json file."
		print(e)
		quit('It seems that there is something wrong with the json file for lexemes. Check it over and run me again.')
