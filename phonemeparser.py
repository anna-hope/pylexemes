# Anton Osten
# http://ostensible.me

import json

class PhonemeParser:

	def __init__(self, phonemes_f=None):

		try:
			if phonemes_f == None:
				phonemes = json.load(open('phonemes.json'))
			else:
				phonemes = json.load(open(phonemes_f))
		except Exception as e:
			self.somethingwrong(e)

		self._phonemes = phonemes
		self._symbols = []
		self._names = []
		self._features = []

		try:
			for n in phonemes:
				self._symbols.append(n['symbol'])
				self._names.append(n['name'])
				self._features.append(list(n['features'].values()))
		except Exception as e:
			self.somethingwrong(e)

	def phonemes():
	    doc = "Phonemes as a dict."
	    def fget(self):
	        return self._phonemes
	    def fset(self, value):
	        self._phonemes = value
	    def fdel(self):
	        del self._phonemes
	    return locals()
	phonemes = property(**phonemes())
	
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

	def names():
	    doc = "Phoneme names."
	    def fget(self):
	        return self._names
	    def fset(self, value):
	        self._names = value
	    def fdel(self):
	        del self._names
	    return locals()
	names = property(**names())

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
