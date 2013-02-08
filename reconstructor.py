#!/usr/bin/env python3
# Anton Osten
# http://ostensible.me

import collections as c
import itertools as i
import difflib, argparse, datetime
from segmentparser import SegmentParser
from lexemeparser import LexemeParser

sp = SegmentParser()

class Reconstructor:

	def __init__(self):
		argparser = argparse.ArgumentParser()
		argparser.add_argument('-verbose', '-v', action='count', help='varying levels of output verbosity')
		argparser.add_argument('-log', '-l', action='store_true', help='create a log of reconstruction')
		argparser.add_argument('-f', '--lexemesfile', type=str, help='specify a lexemes file')
		args = argparser.parse_args()

		unmatched_symbols = []
		self._unmatched_symbols = unmatched_symbols
		
		# custom lexemes file
		if args.lexemesfile:
			lexemesfile = args.lexemesfile
		else:
			lexemesfile = 'lexemes.json'

		# call the parsers
		lp = LexemeParser(lexemesfile)

		# forms
		forms = lp.forms

		# set the threshold to none
		threshold = None
		self._threshold = threshold

		# call methods
		splitforms = self.split_forms(forms)
		avglength = self.avg_length(splitforms)
		
		# deal with output
		output = ''
		self._output = output

		# do the reconstructions
		reconstruction = self.reconstruct(forms, avglength)
		bc_reconstruction = self.collapse(forms, avglength)

		# ARGUMENTS

		# verbosity
		if args.verbose:
	 		# if args.verbose > 1:
	 		#	output += 'Symbol groups: {}\n'.format(symbol_groups)	
			self._output += 'Similarity threshold: {}\n'.format(self._threshold)

		self._output += 'Without branch collapsing: *{}\n'.format(self.reconstruct(forms, avglength))
		self._output += ('With branch collapsing: *{}').format(self.collapse(forms, avglength))

		# write to log
		if args.log:
			logfile = open('reconstruction_log.txt', 'a')
			dt = datetime.datetime
			logfile.write('\n\n{0}\n-----------------\n'.format(dt.isoformat(dt.now())))
			logfile.write(self._output)
			logfile.close()

	def __str__(self):
		return self._output

	# properties

	def unmatched_symbols():
	    doc = "Symbols that were not found in the segment database."
	    def fget(self):
	        return self._unmatched_symbols
	    def fset(self, value):
	        self._unmatched_symbols = value
	    def fdel(self):
	        del self._unmatched_symbols
	    return locals()
	unmatched_symbols = property(**unmatched_symbols())

	def threshold():
	    doc = "Form similarity threshold."
	    def fget(self):
	        return self._threshold
	    def fset(self, value):
	    	if self._threshold == None:
	        	self._threshold = value
	    def fdel(self):
	        del self._threshold
	    return locals()
	threshold = property(**threshold())

	def output():
	    doc = "The output of the reconstruction."
	    def fget(self):
	        return self._output
	    def fset(self, value):
	        self._output = value
	    def fdel(self):
	        del self._output
	    return locals()
	output = property(**output())

	# functions

	def reconstruct(self, cur_forms, avglength):
		tokens = self.split_forms(cur_forms)
		symbol_groups = self.assemble_groups(tokens, avglength)
		matched_features = self.match_p_f(symbol_groups, sp.symbols, sp.features)
		rearranged_features = self.rearrange_groups(matched_features)
		most_prom_f = self.most_prom_feat(rearranged_features)
		matched_symbols = self.match_f_symbols(most_prom_f, sp.symbols, sp.features)
		return matched_symbols[0]

	def collapse(self, cur_forms, avglength):
		doc = "Recursively iterates over forms, each time collapsing two most similar forms into one."
		if len(cur_forms) == 1:
			return cur_forms[0]
		elif len(cur_forms) == 2:
			# self._output += str(cur_forms)
			return self.reconstruct(cur_forms, avglength)
		else:
			forms_ratios = self.sim_ratios(cur_forms)
			self.set_threshold(forms_ratios)
			max_sim_forms = self.max_sim_ratio(forms_ratios)
			if max_sim_forms[2] >= self._threshold:
				cur_forms = [max_sim_forms[0], max_sim_forms[1]]
				reconstructed = self.reconstruct(cur_forms, avglength)
				cur_forms.remove(max_sim_forms[0])
				cur_forms.remove(max_sim_forms[1])
				cur_forms.append(reconstructed)
				return self.collapse(cur_forms, avglength)
			else:
				return self.pick_likeliest(cur_forms, avglength)

	def pick_likeliest(self, cur_forms, avglength):
		reconstruction = self.reconstruct(forms, avglength)
		s_ratios = []
		for cf in cur_forms:
			s_ratio = self.sim_ratios([cf, reconstruction])
			if s_ratio != []:
				s_ratios.append(s_ratio)
		likeliest = list(self.max_sim_ratio(s_ratios))
		return likeliest[0][0]

	def sim_ratios(self, forms):
		doc = "Returns tuples of two forms with their similarity ratios."
		sim_ratios = []
		for x in forms:
			split_x = self.split_forms(x)
			x_pf = self.match_p_f(split_x, sp.symbols, sp.features)
			for y in forms:
				# no one wants to do extra work
				if x != y:
					split_y = self.split_forms(y)
					y_pf = self.match_p_f(split_y, sp.symbols, sp.features)
					pf_ratios = []
					for x_f, y_f in i.zip_longest(x_pf, y_pf, fillvalue=None):
						try:
							x_f = x_f[0]
							y_f = y_f[0]
							pf_ratio = difflib.SequenceMatcher(None, x_f, y_f).ratio()
							pf_ratios.append(pf_ratio)
						except:
							break
					try:
						ratio = sum(pf_ratios)/len(pf_ratios)
					except ZeroDivisionError:
						ratio = 0
					if (y, x, ratio) not in sim_ratios:
						sim_ratios.append((x, y, ratio))
		return sim_ratios

	def max_sim_ratio(self, forms_ratios):
		doc = "Returns the forms with the maximum similarity ratio."
		if len(forms_ratios) == 0:
			return []
		if len(forms_ratios) == 1:
			return forms_ratios
		for form_ratio in forms_ratios:
			try:
				if form_ratio[2] > max_sim[2]:
					max_sim = form_ratio
			except:
				# if it's empty
				max_sim = form_ratio
		return max_sim

	def set_threshold(self, forms_ratios):
		doc = "Sets the similarity threshold for forms."
		if self._threshold == None:
			ratios = []
			for fr in forms_ratios:
				ratios.append(fr[2])
			avg = sum(ratios)/len(ratios)
			# square it so that it's not crazy-high if we have a lot of similar forms
			self._threshold = avg

	def split_forms(self, forms):
		doc = "Splits forms into separate phonemes using split_polysymbols"
		tokens = []
		# check if it's a list of forms or just one form as a string
		if type(forms) is list:	
			tokens = [self.split_polysymbols(form) for form in forms]
		else:
			tokens = self.split_polysymbols(forms)
		return tokens

	def split_polysymbols(self, form):
		doc = "Splits a form into separate phonemes, detecting polysymbollic phonemes such as affricates."
		splitform = []
		# this list will contain the indexes of polysymbollic phonemes in our form
		indexes = []
		polysymbols = sp.polysymbols

		# iterate over the polysymbols to get the indexes
		for polysymbol in polysymbols:
			# temporary form variable to remove polysymbols already accounted for
			t_form = form
			count = 0
			mc = form.count(polysymbol)
			while count < mc:
				# the start index in the temporary form
				t_form_index = t_form.find(polysymbol)
				# difference in lengths between the t_form and the real form
				diff = (len(form) - len(t_form))
				# actual start index
				real_start_index = t_form_index + diff
				endindex = real_start_index + len(polysymbol)

				indexes.append((real_start_index, endindex))
				# slice the t_form so that the part up to which the polysymbol is in is no longer there
				t_form = t_form[(endindex - diff):]
				count += 1

		# if there are no polysymbollic phonemes in this form, then just split it as a list
		if indexes == []:
			return list(form)
		# otherwise split it according to the indexes of polysymbols
		else:
			ls = list(form)

			# the value by which we'll adjust the indexing calls
			# because the length of the list is going to decrease as we go through
			adjust = 0

			for index in indexes:
				del ls[(index[0] - adjust):(index[1] - adjust)]
				ls.insert((index[0] - adjust), form[index[0]:index[1]])
				# adjust the next indexes according to the length of the polysymbol that we've just concatenated
				adjust += ((index[1] - index[0]) - 1)

			splitform = ls
			return splitform

	# get the length of the longest form
	def max_length(self, forms):
		forms.sort(key=len, reverse=True)
		return len(forms[0])

	def avg_length(self, forms):
		doc = "Returns average length of lexemes."
		lengths = []
		for f in forms:
			lengths.append(len(f))
		return round(sum(lengths)/len(lengths))

	# assembles phoneme groups
	def assemble_groups(self, forms, avglength):
		s_groups = []
		p_count = 0
		while p_count < avglength:
			cur_group = []
			# for symbols that have already occured
			sg = []
			for f in forms:
				try:
					sg.append(f[p_count])
					cur_group.append(f[p_count])
				except IndexError:
					# cur_group.append('-')
					pass
			s_groups.append(cur_group)
			# symbol_groups.append(sg)
			p_count += 1
		return s_groups

	# match phonemes to their features
	def match_p_f(self, groups, symbols, features):
		matched_features = []
		# iterate over phoneme groups
		for group in groups:
			# current phoneme feature group
			cur_feat_g = []
			# iterate over phonemes in each group
			for symbol in group:
				if symbol in symbols:
					cur_feat_g.append(list(features[symbol].items()))
				else:
					# append the unidentified symbol to the list of unmatched symbols
					# (if it isn't already there)
					if symbol not in self._unmatched_symbols:
						self._unmatched_symbols.append(symbol)
			if cur_feat_g != []:
				matched_features.append(cur_feat_g)
		return matched_features

	def rearrange_groups(self, matched_features):
		doc = "This function rearranges the phoneme groups so that each phoneme is in the group which it belongs to by running the most_prom_feat functions preliminarily and seeing whether the feature set of each phoneme."
		# the following is done to ensure safety and is probably redundant
		rearranged_features = matched_features
		# get the preliminary most prominent features
		mpf = self.most_prom_feat(rearranged_features)
		for n, f in enumerate(rearranged_features):
			# get the most prominent features of current group
			try:		
				mpfn = mpf[n]
			except:
				return rearranged_features
			try:
				# get the most prominent features of the previous group, if it exists
				mpf0 = mpf[(n - 1)]
			except:
				# if not, then not
				mpf0 = None
			try:
				# get the most prominent features of the next group, if it exists
				mpf1 = mpf[(n + 1)]
			except:
				mpf1 = None
			for p in f:
				# calculate the ratio between this phoneme's features and the preliminary theoretical phoneme in the current group
				r = difflib.SequenceMatcher(None, p, mpfn).ratio()
				if mpf0 and mpf1:
					# if both mpf0 and mpf1 exist, calculate similarity ratios for them and the current phoneme's feature set
					r0 = difflib.SequenceMatcher(None, p, mpf0).ratio()
					r1 = difflib.SequenceMatcher(None, p, mpf1).ratio()
					# the greatest similarity ratio
					b_r = max([r, r0 ,r1])
					if b_r == r0:
						f.remove(p)
						# if it's more similar to the preceding group, move it there
						rearranged_features[n-1].append(p)
					elif b_r == r1:
						f.remove(p)
						# likewise, if it's more similar to the following group, move it there
						rearranged_features[n+1].append(p)
				elif mpf0:
					# if the next group doesn't exist, work on the previous
					r0 = difflib.SequenceMatcher(None, p, mpf0).ratio()
					if r0 > r:
						f.remove(p)
						rearranged_features[n-1].append(p)
				elif mpf1:
					# if the previous group doesn't exist, work on the next
					r1 = difflib.SequenceMatcher(None, p, mpf1).ratio()
					if r1 > r:
						f.remove(p)
						rearranged_features[n+1].append(p)
		return rearranged_features

	# select most prominent features
	def most_prom_feat(self, matched_features):
		# collections module to get the most common property (see below)
		p_features = []
		# iterate over groups of phonemic features
		for group_n, groups in enumerate(matched_features):
			# iterate over phonemes in each group
			cur_group = []
			for phoneme_n, phonemes in enumerate(groups):
				cur_phon = []
				# iterate over each feature (cons, son, round, etc.) in each phoneme
				for prop_n, props in enumerate(phonemes):
					cur_prop = []
					# iterate over phonemes in each group again to get the feature at the same place
					for n, x in enumerate(groups):
						# append the feature at that place to the list of properties at that place
						try:
							cur_prop.append(groups[n][prop_n])
						except Exception as e:
							cur_prop.append('')
					# append the most common feature at that place to list of features for current segment
					cur_phon.append(c.Counter(cur_prop).most_common(1)[0][0])
				# append the current theoretical segment to the list of phonemes as features
				cur_group.append(cur_phon)
			try:
				if list(filter(None, cur_group)) != []:
					p_features.append(cur_group[0])
			# hack in case the group is a singleton
			except:
				p_features.append(cur_group)

		return p_features

	def guess_segment(self, t_segment):
		doc = "Find the segment whose feature set has the highest similarity ratio with the theoretical segment."
		ratios = {}
		tstf = [n[0] for n in t_segment if n[1]]
		for n, f in enumerate(sp.true_features):
			ratios[f] = difflib.SequenceMatcher(None, tstf, sp.true_features[f]).ratio()
		return max(ratios, key=ratios.get)

	# match theoretical phonemes as features to IPA symbols in the database
	def match_f_symbols(self, mcf, symbols, features):
		matched_symbols = []
		symbols = []
		list_features = []
		for f in features:
			symbols.append(f)
			list_features.append(list(features[f].items()))
		unmatched_features = []
		for n, t_segment in enumerate(mcf):
			if t_segment in list_features:
				matched_symbols.append(symbols[list_features.index(t_segment)])
			else:
				# so, if there is no match for the theoretical segment that we've assembled, we're going to make an educated guess
				# based on the similarity ratio between our theoretical segment and the phonemes in our database
				# so the segment which has the highest similarity ratio with our theoretical segment gets picked
				guessed_symbol = self.guess_segment(t_segment)
				matched_symbols.append('(' + guessed_symbol + ')')
				unmatched_features.append((n, t_segment))
		unmatched_features = list(filter(None, unmatched_features))
		return (''.join(matched_symbols), unmatched_features)

def main():
	r = Reconstructor()
	print(r.output)

if __name__ == "__main__":
	main()