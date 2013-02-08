# Anton Osten
# http://ostensible.me
# pylexemes project

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
		self._names = {}
		self._features = {}

		try:
			for n in self._segments:
				symbol = n['symbol']
				self._symbols.append(symbol)
				self._names[symbol] = n['name']
				self._features[symbol] = n['features']

		except Exception as e:
			self.somethingwrong(e)

		polysymbols = [n for n in self._symbols if len(n) > 1]
		self._polysymbols = polysymbols

		true_features = {}
		for s in self._features:
		 	segment_true_features = [f for f in self._features[s] if self._features[s][f]]
		 	true_features[s] = segment_true_features
		self._true_features = true_features

	def segments():
	    doc = "Segments as a dictionary."
	    def fget(self):
	        return self._segments
	    def fset(self, value):
	        self._segments = value
	    def fdel(self):
	        del self._segments
	    return locals()
	segments = property(**segments())
	
	def symbols():
	    doc = "Segment symbols as a lyst."
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
	    doc = "Segment names."
	    def fget(self):
	        return self._names
	    def fset(self, value):
	        self._names = value
	    def fdel(self):
	        del self._names
	    return locals()
	names = property(**names())

	def features():
	    doc = "All segment features (including false and non-applicable)."
	    def fget(self):
	        return self._features
	    def fset(self, value):
	        self._features = value
	    def fdel(self):
	        del self._features
	    return locals()
	features = property(**features())

	def true_features():
	    doc = "Only the active features of segments."
	    def fget(self):
	        return self._true_features
	    def fset(self, value):
	        self._true_features = value
	    def fdel(self):
	        del self._true_features
	    return locals()
	true_features = property(**true_features())

	def somethingwrong(self, e):
		doc = "Invoked when something goes wrong with the segments.json file."
		print(e)
		quit('It seems that there is something wrong with the json file for segments. Check it over and run me again.')
