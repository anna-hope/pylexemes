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
		self._starting_forms = forms

		# set the threshold to none
		threshold = None
		self._threshold = threshold

		# set the cap
		cap = len(forms) * 3
		self._form_cap = cap

		# call methods
		splitforms = self.split_forms(forms)
		avglength = self.avg_length(splitforms)
		self._avglength = avglength
		
		# deal with output
		output = ''
		self._output = output

		# temporary reconstruction
		forms_ratios = self.sim_ratios(self._starting_forms)
		max_sim = self.max_sim_ratio(forms_ratios)
		temp_reconstruction = self.reconstruct([max_sim[0], max_sim[1]])
		self._temp_reconstruction = temp_reconstruction
		self._output += 'Temporary reconstruction: {}\n'.format(self._temp_reconstruction)

		# do the reconstructions
		reconstruction = self.reconstruct(forms)
		bc_reconstruction = self.collapse(forms)

		# ARGUMENTS

		# verbosity
		if args.verbose:
	 		# if args.verbose > 1:
	 		#	output += 'Symbol groups: {}\n'.format(symbol_groups)	
			self._output += 'Similarity threshold: {}\n'.format(self._threshold)

		self._output += 'Without branch collapsing: *{}\n'.format(reconstruction)
		self._output += ('With branch collapsing: *{}').format(bc_reconstruction)

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

	def starting_forms():
	    doc = "Forms given at the beginning."
	    def fget(self):
	        return self._starting_forms
	    def fset(self, value):
	        self._starting_forms = value
	    def fdel(self):
	        del self._starting_forms
	    return locals()
	starting_forms = property(**starting_forms())

	def avglength():
	    doc = "Average length of starting forms."
	    def fget(self):
	        return self._avglength
	    def fset(self, value):
	        self._avglength = value
	    def fdel(self):
	        del self._avglength
	    return locals()
	avglength = property(**avglength())

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

	def temp_reconstruction():
	    doc = "The temp_reconstruction property."
	    def fget(self):
	        return self._temp_reconstruction
	    def fset(self, value):
	        self._temp_reconstruction = value
	    def fdel(self):
	        del self._temp_reconstruction
	    return locals()
	temp_reconstruction = property(**temp_reconstruction())

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

	def form_cap():
	    doc = "The form_cap property."
	    def fget(self):
	        return self._form_cap
	    def fset(self, value):
	        self._form_cap = value
	    def fdel(self):
	        del self._form_cap
	    return locals()
	form_cap = property(**form_cap())

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

	def reconstruct(self, cur_forms):
		print('Current reconstruction: {}'.format(cur_forms))
		tokens = self.split_forms(cur_forms)
		symbol_groups = self.assemble_groups(tokens, self._avglength)
		matched_features = self.match_p_f(symbol_groups)
		# matched_features = self.match_true_features(symbol_groups)
		rearranged_features = self.rearrange_groups(matched_features)
		most_prom_f = self.most_prom_feat(rearranged_features)
		# most_prom_f = self.push_features(rearranged_features)
		matched_symbols = self.match_f_symbols(most_prom_f, sp.symbols, sp.features)
		return matched_symbols[0]

	def collapse(self, cur_forms):
		doc = "Recursively iterates over forms, each time collapsing two most similar forms into one."
		if len(cur_forms) == 1:
			print('Current forms: {}\n'.format(cur_forms))
			return cur_forms[0]
		elif len(cur_forms) == 2:
			print('Current forms: {}\n'.format(cur_forms))
			return self.reconstruct(cur_forms)
		else:
			print('Current forms: {}\n'.format(cur_forms))
			forms_ratios = self.sim_ratios(cur_forms)
			self.set_threshold(forms_ratios)
			ms = self.merge_similar(forms_ratios)
			if ms == []:
				return self.pick_likeliest(cur_forms)
			elif(len(ms) >= self._form_cap):
				return self.reconstruct(ms)
			else:
				return self.collapse(ms)

	def pick_likeliest(self, cur_forms):
		s_ratios = []
		for cf in cur_forms:
			s_ratio = self.sim_ratios([cf, self._temp_reconstruction])
			if s_ratio != []:
				s_ratios.append(s_ratio)
		likeliest = list(self.max_sim_ratio(s_ratios))
		return likeliest[0][0]

	def merge_similar(self, forms_ratios):
		ms = []
		for fr in forms_ratios:
			if fr[2] >= self._threshold and self.is_likely(fr[0]) and self.is_likely(fr[1]):
				if fr[0] not in ms and fr[1] not in ms:
					reconstruction = self.reconstruct([fr[0], fr[1]])
					if self.is_likely(reconstruction):
						print('Likely: {}'.format(reconstruction))
						ms.append(reconstruction)
					else:
						print('Unlikely: {}'.format(reconstruction))
		print(ms)
		return ms

	def is_likely(self, form):
		try:
			ratio = (self.temp_rec_sim_ratio(form))[0][1]
			print('Ratio: {}'.format(ratio))
		except:
			return False
		if ratio >= self._threshold:
			return True
		else:
			return False

	def temp_rec_sim_ratio(self, forms):
		forms_ratios = []
		used_forms = []
		split_reconstructed = self.split_forms(self._temp_reconstruction)
		reconstructed_pf = self.match_p_f(split_reconstructed)
		if type(forms) == str:
			forms = [forms]
		for form in forms:
			if form == self._temp_reconstruction:
				sim_ratios.append(form, form, 1.0)
				used_forms.append(form)
				forms.remove(form)
			else:
				split_form = self.split_forms(form)
				form_pf = self.match_p_f(split_form)
				sf_ratios = []
				for form_f, reconstructed_f in i.zip_longest(form_pf, reconstructed_pf, fillvalue=None):
					try:
						form_f = form_f[0]
						reconstructed_f = reconstructed_f[0]
						sf_ratio = difflib.SequenceMatcher(None, form_f, reconstructed_f).ratio()
						sf_ratios.append(sf_ratio)
					except:
						if len(sf_ratios) != 0:
							sf_ratios.append(sum(sf_ratios)/len(sf_ratios))
						else:
							sim_ratios.append(0)
				try:
					ratio = sum(sf_ratios)/len(sf_ratios)
				except ZeroDivisionError:
					ratio = 0
				forms_ratios.append((form, ratio))
				used_forms.append(form)
		return forms_ratios

	def sim_ratios(self, forms):
		doc = "Returns tuples of two forms with their similarity ratios."
		sim_ratios = []
		used_forms = []
		for x in forms:
			split_x = self.split_forms(x)
			x_pf = self.match_p_f(split_x)
			# x_pf = self.match_true_features(split_x)
			for y in forms:
				# no one wants to do extra work
				if x not in used_forms and y not in used_forms:
					if x != y:
						split_y = self.split_forms(y)
						y_pf = self.match_p_f(split_y)
						# y_pf = self.match_true_features(split_y)
						pf_ratios = []
						for x_f, y_f in i.zip_longest(x_pf, y_pf, fillvalue=None):
							try:
								x_f = x_f[0]
								y_f = y_f[0]
								pf_ratio = difflib.SequenceMatcher(None, x_f, y_f).ratio()
								pf_ratios.append(pf_ratio)
							except:
								pf_ratios.append(sum(pf_ratios)/len(pf_ratios))
						try:
							ratio = sum(pf_ratios)/len(pf_ratios)
						except ZeroDivisionError:
							ratio = 0
						sim_ratios.append((x, y, ratio))
						used_forms.append(x)
						used_forms.append(y)
					# else:
					# 	while x in forms:
					# 		forms.remove(x)
					# 	sim_ratios.append((x, x, 1.0))
						# used_forms.append(x)
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
					continue
			s_groups.append(cur_group)
			# symbol_groups.append(sg)
			p_count += 1
		return s_groups

	# match phonemes to their features
	def match_p_f(self, groups):
		matched_features = []
		# iterate over phoneme groups
		for group in groups:
			# current phoneme feature group
			cur_feat_g = []
			# iterate over phonemes in each group
			for symbol in group:
				if symbol in sp.symbols:
					cur_feat_g.append(list(sp.features[symbol].items()))
				else:
					# append the unidentified symbol to the list of unmatched symbols
					# (if it isn't already there)
					if symbol not in self._unmatched_symbols:
						self._unmatched_symbols.append(symbol)
			if cur_feat_g != []:
				matched_features.append(cur_feat_g)
		return matched_features

	# def match_true_features(self, groups):
	# 	matched_features = []
	# 	# iterate over phoneme groups
	# 	for group in groups:
	# 		# current phoneme feature group
	# 		cur_feat_g = []
	# 		# iterate over phonemes in each group
	# 		for symbol in group:
	# 			if symbol in sp.symbols:
	# 				cur_feat_g.append(sp.true_features[symbol])
	# 			else:
	# 				# append the unidentified symbol to the list of unmatched symbols
	# 				# (if it isn't already there)
	# 				if symbol not in self._unmatched_symbols:
	# 					self._unmatched_symbols.append(symbol)
	# 		if cur_feat_g != []:
	# 			matched_features.append(cur_feat_g)
	# 	return matched_features


	def rearrange_groups(self, matched_features):
		doc = "This function rearranges the phoneme groups so that each phoneme is in the group which it belongs to by running the most_prom_feat functions preliminarily and seeing whether the feature set of each phoneme."
		# the following is done to ensure safety and is probably redundant
		rearranged_features = matched_features
		# get the preliminary most prominent features
		# mpf = self.push_features(rearranged_features)
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
							continue
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

	# er, this didn't work out
	# def push_features(self, matched_features):
	# 	p_features = []
	# 	for groups in matched_features:
	# 		cur_g = []
	# 		for group in groups:
	# 			cur_phon = []
	# 			for n_seg, segment in enumerate(group):
	# 				cur_segment = []
	# 				for n, x in enumerate(groups):
	# 					try:
	# 						feature = groups[n][n_seg]
	# 						if feature not in cur_segment:
	# 							cur_segment.append(feature)
	# 					except:
	# 						continue
	# 				cur_phon += cur_segment
	# 		p_features.append(cur_phon)
	# 	return p_features


	def guess_segment(self, t_segment):
		doc = "Find the segment whose feature set has the highest similarity ratio with the theoretical segment."
		ratios = {}
		for n, f in enumerate(sp.features):
			ratios[f] = difflib.SequenceMatcher(None, t_segment, list(sp.features[f].items())).ratio()
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