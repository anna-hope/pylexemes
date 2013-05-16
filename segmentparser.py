# Anton Osten
# http://ostensible.me
# pylexemes project

try:
    import simplejson as json
except ImportError:
    from warnings import warn
    warn(UserWarning('simplejson not found. Using site-provided json, parsing may be slower.'))
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
		self._duplicates = self.find_duplicates()

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

	def duplicates():
	    doc = "The duplicates property."
	    def fget(self):
	        return self._duplicates
	    def fset(self, value):
	        self._duplicates = value
	    def fdel(self):
	        del self._duplicates
	    return locals()
	duplicates = property(**duplicates())

	def find_duplicates(self):
		doc = "Returns segments with the same features."
		# the two lists are needed to keep indexes in sync
		done_symbols = []
		done_features = []
		duplicate_groups = []
		for s in self._features:
			# features of the current segment
			cur_features = self._features[s]
			if cur_features in done_features:
				for duplicate_group in duplicate_groups:
					# if there is already more than a pair of segments with the same features
					# we'll do this to add the current segment to the list of those duplicates
					# first checking that we're not adding a duplicate (ha!) symbol
					if done_symbols[done_features.index(cur_features)] in duplicate_group:
						symbol = [s for s in self._features if (s not in duplicate_group and self._features[s] == cur_features)][0]
						duplicate_group.append(symbol)
						break
				else:
					# otherwise just append it as a list 
					duplicate_groups.append([done_symbols[done_features.index(cur_features)], s])
			else:
				done_symbols.append(s)
				done_features.append(self._features[s])
		return duplicate_groups

	def somethingwrong(self, e):
		doc = "Invoked when something goes wrong with the segments.json file."
		print(e)
		quit('It seems that there is something wrong with the json file for segments. Check it over and run me again.')