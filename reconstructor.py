#!/usr/bin/env python3
# Anton Osten
# http://ostensible.me

import collections as c
import itertools as i
import difflib, argparse, datetime, pprint
from datetime import datetime
from operator import itemgetter
from segmentparser import SegmentParser
from lexemeparser import LexemeParser

sp = SegmentParser()

class Reconstructor:

	def __init__(self, lexemesfile=None, times=1, verbose=0, log=False):

		unmatched_symbols = []
		self._unmatched_symbols = unmatched_symbols
		
		# custom lexemes file
		if lexemesfile is None:
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
		self.output = output

		# do the reconstructions
		self.output += 'Unbiased reconstructions: {}\n'.format(prov_recs)

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

		self.reconstruction = self.run_biased(forms, prov_recs, times)
		tests = self.test_recs(self.reconstruction, lp.true_recs, lang_ratios)
		
		# ARGUMENTS

		# verbosity
		if verbose:
			if verbose > 1:
				self.output += 'Similarity ratios: {}\n'.format(ratios)
				self.output += 'Forms: {}\n'.format(forms)
				self.output += 'Language ratios: {}\n'.format(avg_ratio_lang)
			self.output += 'Symbols not found in the database: {}\n'.format(self._unmatched_symbols)
			try:
				for test in tests[0]:
					self.output += '{}, real reconstruction: {}, similarity: {}%, {}\n'.format(test[0], test[1], test[2], test[3])
				self.output += 'average accuracy: {}%, {}\n'.format(tests[1][0], tests[1][1])
			except TypeError:
				pass

		# self.output += 'Biased reconstructions: {}'.format(self.reconstruction)

		# write to log
		if log:
			logfile = open('reconstruction_log.txt', 'a')
			dt = datetime
			logfile.write('\n\n{0}\n-----------------\n'.format(dt.isoformat(dt.now())))
			logfile.write(self.output)
			logfile.close()

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
		b_recs = []
		for root, prov_rec in zip(forms, prov_recs):
			ratio_pairs = [self.sim_ratio(form, prov_rec) for form in root if form != '-']
			ratios = [rp[2] for rp in ratio_pairs]
			threshold = sum(ratios)/len(ratios)
			# cut_root = [rp[0] for rp in ratio_pairs if rp[2] >= threshold]
			cut_root = []
			for rp in ratio_pairs:
				if rp[2] >= threshold:
					for n in range(round(rp[2] * 10)):
						cut_root.append(rp[0])
			cut_forms.append(cut_root)
		for root, prov_rec in zip(cut_forms, prov_recs):
			self._avglength = self.avg_length(root)
			b_rec = self.reconstruct(root + [prov_rec])
			print(b_rec)
			b_recs.append(b_rec)
		return (cut_forms, b_recs)

	def run_biased(self, forms, prov_recs, times):
		for n in range(times):
			(forms, prov_recs) = self.biased_reconstruct(forms, prov_recs)
		return prov_recs

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
			for n, symbol in enumerate(group):
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
		for n, g in enumerate(rearranged_features):
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
			for s in g:
				# calculate the ratio between this phoneme's features and the preliminary theoretical phoneme in the current group
				r = difflib.SequenceMatcher(None, s, mpfn).ratio()
				if mpf0 and mpf1:
					# if both mpf0 and mpf1 exist, calculate similarity ratios for them and the current phoneme's feature set
					r0 = difflib.SequenceMatcher(None, s, mpf0).ratio()
					r1 = difflib.SequenceMatcher(None, s, mpf1).ratio()
					# the greatest similarity ratio
					b_r = max([r, r0 ,r1])
					if b_r == r0:
						g.remove(s)
						# if it's more similar to the preceding group, move it there
						rearranged_features[n-1].append(s)
					elif b_r == r1:
						g.remove(s)
						# likewise, if it's more similar to the following group, move it there
						rearranged_features[n+1].append(s)
				elif mpf0:
					# if the next group doesn't exist, work on the previous
					r0 = difflib.SequenceMatcher(None, s, mpf0).ratio()
					if r0 > r:
						g.remove(s)
						rearranged_features[n-1].append(s)
				elif mpf1:
					# if the previous group doesn't exist, work on the next
					r1 = difflib.SequenceMatcher(None, s, mpf1).ratio()
					if r1 > r:
						g.remove(s)
						rearranged_features[n+1].append(s)
		# if there are still extraneous segments, let's just kill them
		rearranged_features = self.drop_segments(rearranged_features)
		return rearranged_features

	def drop_segments(self, s_features):
		doc = "Drops segments which are extraneous based on their similarity to the most prominent segment features in their group"
		mpf = self.most_prom_feat(s_features)
		new_groups = []
		for n, g in enumerate(s_features):
			mpfn = mpf[n]
			threshold = self.avg_sg_ratio(g)
			cut_segments = [segment for segment in g if difflib.SequenceMatcher(None, segment, mpfn).ratio() >= threshold]
			new_groups.append(cut_segments)
		return new_groups

	def avg_sg_ratio(self, s_features):
		doc = "Returns the average similarity ratio for that segment group, used for thresholding"
		ratios = [difflib.SequenceMatcher(None, x, y).ratio() for x in s_features for y in s_features]
		return sum(ratios)/len(ratios)

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
		for f in sp.features:
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
		f2_tokens = self.split_forms(form2)

		# this needs to be passed as a list cuz otherwise symbols_to_features thinks that every token is a group
		try:
			f1_features = (self.symbols_to_features([f1_tokens]))[0] 
			f2_features = (self.symbols_to_features([f2_tokens]))[0]
		except IndexError:
			return (form1, form2, 0.0)

		ratios = []
		for segment1, segment2 in i.zip_longest(f1_features, f2_features, fillvalue=[]):
			if segment1 == segment2:
				ratios.append(1.0)
			elif segment1 == [] or segment2 == []:
				# still don't really know what to do in this case
				# because any clever trick I try leads to worse reconstructions
				# like the one below, for instance
				# try:
				# 	ratios.append((sum(ratios)/len(ratios)) ** (len(f1_features) - len(f2_features)))
				# except ZeroDivisionError:
				# 	pass
				break
			else:
				ratios.append(difflib.SequenceMatcher(None, segment1, segment2).ratio())
		try:
			ratio = sum(ratios)/len(ratios)
		except ZeroDivisionError:
			ratio = 0.0
			# this looks like an owl in my font
		return (form1, form2, ratio)

	def test_recs(self, recs, true_recs, lang_ratios):
		if true_recs == None:
			return
		threshold = sum(lang_ratios)/len(lang_ratios)
		tests = []
		for rec, true_rec in zip(recs, true_recs):
			ratio = (self.sim_ratio(rec, true_rec))
			if ratio[2] >= threshold:
				tests.append((rec, true_rec, (round((ratio[2] * 100), 1)), 'passed'))
			else:
				tests.append((rec, true_rec, (round((ratio[2] * 100), 1)), 'failed'))
		ratios = [test[2] for test in tests]
		avg = sum(ratios)/len(ratios)
		if avg >= threshold:
			result = (round(avg, 1), 'success :)')
		else:
			result = (round(avg, 1), 'failure :(')
		return (tests, result)
			
def main():
	print('Working...')
	r = Reconstructor(args.lexemesfile, args.times, args.verbose, args.log)
	pp = pprint.PrettyPrinter()
	print(r.output)
	pp.pprint(r.reconstruction)

if __name__ == "__main__":
	# arguments
	argparser = argparse.ArgumentParser()
	argparser.add_argument('-v', '--verbose', action='count', help='varying levels of output verbosity')
	argparser.add_argument('-l', '--log', action='store_true', help='create a log of reconstruction')
	argparser.add_argument('-f', '--lexemesfile', type=str, help='specify a lexemes file')
	argparser.add_argument('-t','--times', type=int, default=1, help='the number of times to run the reconstruction')
	args = argparser.parse_args()
	main()