#!/usr/bin/env python3
# Anton Osten
# http://ostensible.me

import collections as c
import itertools as i
import difflib
import argparse, datetime
from phonemeparser import PhonemeParser
from lexemeparser import LexemeParser

argparser = argparse.ArgumentParser()
argparser.add_argument('-verbose', '-v', action='count', help='varying levels of output verbosity')
argparser.add_argument('-log', '-l', action='store_true', help='create a log of reconstruction')
args = argparser.parse_args()

unmatched_symbols = []
symbol_groups = []
reconstructions = []

def main():
	# call the parsers
	pp = PhonemeParser()
	lp = LexemeParser()

	# consonants
	symbols = pp.symbols
	features = pp.features

	# get polysymbol phonemes
	polysymbols = get_polysymbols(symbols)

	# forms
	forms = lp.forms

	polysymbols = get_polysymbols(symbols)

	output = ''

	# verbosity
	if args.verbose:
 		if args.verbose > 1:
 			output += 'Symbol groups: {}\n'.format(symbol_groups)	
#			if args.verbose > 2:

	output += 'Without branch collapsing *{}\n'.format(reconstruct(forms, symbols, polysymbols, features))
	output += ('With branch collapsing *{}').format(collapse(forms, symbols, polysymbols, features))

	# write to log
	if args.log:
		logfile = open('reconstruction_log.txt', 'a')
		dt = datetime.datetime
		logfile.write('\n\n{0}\n-----------------\n'.format(dt.isoformat(dt.now())))
		logfile.write(output)
		logfile.close()

	print(output)

# functions

def reconstruct(forms, symbols, polysymbols, features):
	splitforms = split_forms(forms, polysymbols)
	maxlength = max_length(splitforms)
	symbol_groups = assemble_groups(splitforms, maxlength)
	matched_features = match_p_f(symbol_groups, symbols, features)
	rearranged_features = rearrange_groups(matched_features)
	most_prom_f = most_prom_feat(rearranged_features)
	matched_symbols = match_f_symbols(most_prom_f, symbols, features)
	return matched_symbols[0]

def collapse(forms, symbols, polysymbols, features):
	doc = "Recursively iterates over forms, each time collapsing two most similar forms into one."
	if len(forms) == 1:
		return forms[0]
	elif len(forms) == 2:
		# print(forms)
		return reconstruct(forms, symbols, polysymbols, features)
	else:
		# print(forms)
		forms_ratios = sim_ratios(forms, symbols, polysymbols, features)
		max_sim_forms = sort_form_ratios(forms_ratios)
		cur_forms = [max_sim_forms[0], max_sim_forms[1]]
		reconstructed = reconstruct(cur_forms, symbols, polysymbols, features)
		forms.remove(max_sim_forms[0])
		forms.remove(max_sim_forms[1])
		forms.append(reconstructed)
		# all of the recursion
		return collapse(forms, symbols, polysymbols, features)


def sim_ratios(forms, symbols, polysymbols, features):
	doc = "Returns tuples of two forms with their similarity ratios."
	sim_ratios = []
	for x in forms:
		split_x = split_forms(x, polysymbols)
		len_x = len(x)
		# x_symbol_groups = assemble_groups(x, len_x)
		x_pf = match_p_f(split_x, symbols, features)
		for y in forms:
			# no one wants to do extra work
			if x != y:
				split_y = split_forms(y, polysymbols)
				len_y = len(y)
				y_pf = match_p_f(split_y, symbols, features)
				pf_ratios = []
				for x_f, y_f in i.zip_longest(x_pf, y_pf, fillvalue=[]):
					try:
						x_f = x_f[0]
						y_f = y_f[0]
						pf_ratio = difflib.SequenceMatcher(None, x_f, y_f).ratio()
						pf_ratios.append(pf_ratio)
					except:
						pf_ratios.append(0)
				ratio = sum(pf_ratios)/len(pf_ratios)
				if (y, x, ratio) not in sim_ratios:
					sim_ratios.append((x, y, ratio))
	return sim_ratios

def sort_form_ratios(forms_ratios):
	doc = "Returns the forms with the maximum similarity ratio."
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

def avg_sim_ratio(forms_ratios):
	doc = "Returns the average similarity ratio."
	ratios = []
	for fr in forms_ratios:
		ratios.append(fr[2])
	avg = sum(ratios)/len(ratios)
	return avg

def get_polysymbols(symbols):
	polysymbols = [n for n in symbols if len(n) > 1]
	return polysymbols 

def split_forms(forms, polysymbols):
	doc = "Splits forms into separate phonemes using split_polysymbols"
	new_forms = []
	# iterate over the forms
	for form in forms:
		new_forms.append(split_polysymbols(form, polysymbols))
	return new_forms


def split_polysymbols(form, polysymbols):
	doc = "Splits a form into separate phonemes, detecting polysymbollic phonemes such as affricates."
	splitform = []
	# this list will contain the indexes of polysymbollic phonemes in our form
	indexes = []

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
			adjust += ((index[1] - index[0]) -1)

		splitform = ls
		return splitform

# get the length of the longest form
def max_length(forms):
	forms.sort(key=len, reverse=True)
	return len(forms[0])

# assembles phoneme groups
def assemble_groups(forms, maxlength):
	s_groups = []
	p_count = 0
	while p_count < maxlength:
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
		symbol_groups.append(sg)
		p_count += 1
	return s_groups

# match phonemes to their features
def match_p_f(groups, symbols, features):
	matched_features = []
	# iterate over phoneme groups
	for group in groups:
		# current phoneme feature group
		cur_feat_g = []
		# iterate over phonemes in each group
		for symbol in group:
			if symbol in symbols:
				cur_feat_g.append(features[symbols.index(symbol)])
			else:
				# append the unidentified symbol to the list of unmatched symbols
				# (if it isn't already there)
				if symbol not in unmatched_symbols:
					unmatched_symbols.append(symbol)
		matched_features.append(cur_feat_g)
	return matched_features

def rearrange_groups(matched_features):
	doc = "This function rearranges the phoneme groups so that each phoneme is in the group which it belongs to by running the most_prom_feat functions preliminarily and seeing whether the feature set of each phoneme."
	# the following is done to ensure safety and is probably redundant
	rearranged_features = matched_features
	# get the preliminary most prominent features
	mpf = most_prom_feat(rearranged_features)
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
def most_prom_feat(matched_features):
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
				# append the most common feature at that place to list of features for current phoneme
				cur_phon.append(c.Counter(cur_prop).most_common(1)[0][0])
			# append the current theoretical phoneme to the list of phonemes as features
			cur_group.append(cur_phon)
		try:
			if list(filter(None, cur_group)) != []:
				p_features.append(cur_group[0])
		# hack in case the group is a singleton
		except:
			p_features.append(cur_group)

	return p_features

def guess_phoneme(t_phoneme, symbols, features):
	doc = "Find the phoneme whose feature set has the highest similarity ratio with the theoretical phoneme."
	ratios = {}
	for n, f in enumerate(features):
		ratios[symbols[n]] = difflib.SequenceMatcher(None, t_phoneme, f).ratio()
	return max(ratios, key=ratios.get)

# match theoretical phonemes as features to IPA symbols in the database
def match_f_symbols(mcf, symbols, features):
	matched_symbols = []
	unmatched_features = []
	for n, t_phoneme in enumerate(mcf):
		if t_phoneme in features:
			matched_symbols.append(symbols[features.index(t_phoneme)])
		else:
			# so, if there is no match for the theoretical phoneme that we've assembled, we're going to make an educated guess
			# based on the similarity ratio between our theoretical phoneme and the phonemes in our database
			# so the phoneme which has the highest similarity ratio with our theoretical phoneme gets picked
			guessed_symbol = guess_phoneme(t_phoneme, symbols, features)
			matched_symbols.append(guessed_symbol)
			unmatched_features.append((n, t_phoneme))
	unmatched_features = list(filter(None, unmatched_features))
	return (''.join(matched_symbols), unmatched_features)

if __name__ == "__main__":
	main()