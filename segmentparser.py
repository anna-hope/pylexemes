# Anton Osten
# http://ostensible.me

import json

class SegmentParser:

	def __init__(self, segments_f=None):

		try:
			if segments_f == None:
				segments = json.load(open('segments.json'))
			else:
				segments = json.load(open(segments_f))
		except Exception as e:
			self.somethingwrong(e)

		self._segments = segments
		self._symbols = []
		self._names = []
		self._features = []

		try:
			for n in segments:
				self._symbols.append(n['symbol'])
				self._names.append(n['name'])
				self._features.append(list(n['features'].items()))
		except Exception as e:
			self.somethingwrong(e)

		polysymbols = [n for n in self._symbols if len(n) > 1]
		self._polysymbols = polysymbols

	def segments():
	    doc = "Segments as a dictionary."
	    def fget(self):
	        return self.segments
	    def fset(self, value):
	        self.segments = value
	    def fdel(self):
	        del self.segments
	    return locals()
	segments = property(**segments())
	
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

	def polysymbols():
	    doc = "Polysymbols."
	    def fget(self):
	        return self._polysymbols
	    def fset(self, value):
	        self._polysymbols = value
	    def fdel(self):
	        del self._polysymbols
	    return locals()
	polysymbols = property(**polysymbols())

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
		doc = "Invoked when something goes wrong with the segments.json file."
		print(e)
		quit('It seems that there is something wrong with the json file for segments. Check it over and run me again.')
