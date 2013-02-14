#!/usr/bin/env python3
# Anton Osten
# http://ostensible.me

import collections as c
import itertools as i
import difflib, argparse, datetime
from datetime import datetime
from operator import itemgetter
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
		
		forms = lp.forms
		lang_codes = lp.lang_codes

		# assemble just the forms

		prov_recs = []

		# run unbiased reconstruction for each root
		for root in forms:
			splitforms = self.split_forms(root)
			avglength = self.avg_length(splitforms)
			self._avglength = avglength
			reconstruction = self.reconstruct(root)
			prov_recs.append(reconstruction)
		
		# deal with output
		output = ''
		self._output = output

		# do the reconstructions
		self._output += 'Unbiased reconstructions: {}\n'.format(prov_recs)

		# calculate the similarity ratios of each form to the provisional reconstruction
		ratios = []
		for prov_rec, root in zip(prov_recs, forms):
			cur_root_ratios = []
			for lexeme in root:
				cur_root_ratios.append(self.sim_ratio(lexeme, prov_rec))
			ratios.append(cur_root_ratios)

		avg_ratio_lang = {}

		for lang in lang_codes:
			lang_ratios = [root[lang_codes.index(lang)][2] for root in ratios if root[lang_codes.index(lang)][2] != 0]
			avg_ratio_lang[lang] = sum(lang_ratios)/len(lang_ratios)

		lang_ratios = [avg_ratio_lang[lang] for lang in avg_ratio_lang]

		b_recs = self.biased_reconstruct(forms, prov_recs)
		
		# ARGUMENTS

		# verbosity
		if args.verbose:
			self._output += 'Forms: {}\n'.format(forms)
			self._output += 'Symbols not found in the database: {}\n'.format(self._unmatched_symbols)
			if args.verbose > 1:
				self._output += 'Similarity ratios: {}\n'.format(ratios)
	 	
		self._output += 'Biased reconstructions: {}\n'.format(b_recs)

		# write to log
		if args.log:
			logfile = open('reconstruction_log.txt', 'a')
			dt = datetime
			logfile.write('\n\n{0}\n-----------------\n'.format(dt.isoformat(dt.now())))
			logfile.write(self._output)
			logfile.close()

	def __str__(self):
		return self._output

	# properties

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

	def threshold():
	    doc = "Similarity threshold."
	    def fget(self):
	        return self._threshold
	    def fset(self, value):
	        self._threshold = value
	    def fdel(self):
	        del self._threshold
	    return locals()
	threshold = property(**threshold())

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
		doc = "Reconstructs multiple forms of a single root based on frequency of each feature in each segment of the root."
		tokens = self.split_forms(cur_forms)
		symbol_groups = self.assemble_groups(tokens, self._avglength)
		matched_features = self.symbols_to_features(symbol_groups)
		features = self.rearrange_groups(matched_features)
		most_prom_f = self.most_prom_feat(features)
		symbols = self.features_to_symbols(most_prom_f, sp.symbols, sp.features)
		return symbols[0]

	def biased_reconstruct(self, forms, prov_recs):
		doc = "Reconstructs every form provided in the data according to how similar each feature of a form is to the feature of the provisional reconstruction"
		cut_forms = []
		thresholds = []
		b_recs = []
		for root, prov_rec in zip(forms, prov_recs):
			ratio_pairs = [self.sim_ratio(form, prov_rec) for form in root if form != '-']
			ratios = [rp[2] for rp in ratio_pairs]
			threshold = sum(ratios)/len(ratios)
			thresholds.append(threshold)
			cut_root = [rp[0] for rp in ratio_pairs if rp[2] >= threshold]
			cut_forms.append(cut_root)
		for root, prov_rec in zip(cut_forms, prov_recs):
			self._avglength = self.avg_length(root)
			b_rec = self.reconstruct(root + [prov_rec])
			b_recs.append(b_rec)
		return b_recs

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

	def avg_length(self, forms):
		doc = "Returns the average length of forms."
		lengths = [len(f) for f in forms]
		return round(sum(lengths)/len(lengths))

	def assemble_groups(self, forms, avglength):
		doc = "Assembles segment groups."
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
	def symbols_to_features(self, groups):
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

	def guess_segment(self, t_segment):
		doc = "Find the segment whose feature set has the highest similarity ratio with the theoretical segment."
		ratios = {}
		for n, f in enumerate(sp.features):
			ratios[f] = difflib.SequenceMatcher(None, t_segment, list(sp.features[f].items())).ratio()
		return max(ratios, key=ratios.get)

	# match theoretical phonemes as features to IPA symbols in the database
	def features_to_symbols(self, mcf, symbols, features):
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

	def sim_ratio(self, form1, form2):
		# it's unlikely, but whatevs
		if form1 == form2:
			return (form1, form2, 1.0)

		f1_tokens = self.split_forms(form1)
		f1_features = self.symbols_to_features([f1_tokens]) 
		# this needs to be passed as a list cuz otherwise symbols_to_features thinks that every token is a group

		f2_tokens = self.split_forms(form2)
		f2_features = self.symbols_to_features([f2_tokens])

		ratios = []
		for segment1, segment2 in i.zip_longest(f1_features, f2_features, fillvalue=[]):
			if segment1 == segment2:
				ratios.append(1.0)
			else:
				try:
					ratios.append(difflib.SequenceMatcher(None, segment1[0], segment2[0]).ratio())
				except IndexError:
					# still need to figure out what to do when the iteration falls off the end of one of the forms
					# if ratios != []:
					# 	ratios.append(sum(ratios)/len(ratios))
					break
		try:
			ratio = sum(ratios)/len(ratios)
		except ZeroDivisionError:
			ratio = 0.0
			# this looks like an owl in my font
		return (form1, form2, ratio)
			
def main():
	r = Reconstructor()
	print(r.output)

if __name__ == "__main__":
	main()