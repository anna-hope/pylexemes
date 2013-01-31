#!/usr/bin/env python3
# Anton Osten
# http://ostensible.me

import collections as c
import itertools as i
import argparse, datetime
from phonemeparser import PhonemeParser
from lexemeparser import LexemeParser

unmatched_symbols = []

argparser = argparse.ArgumentParser()
argparser.add_argument('-verbose', '-v', action='count', help='varying levels of output verbosity')
argparser.add_argument('-log', '-l', action='store_true', help='create a log of reconstruction')
args = argparser.parse_args()

def main():
	# call the parsers
	pp = PhonemeParser()
	lp = LexemeParser()

	# consonants
	symbols = pp.symbols
	features = pp.features

	# get polysymbol phonemes
	polysymbols = []
	for n in symbols:
		if len(n) > 1:
			polysymbols.append(n)

	# forms and languages
	forms = lp.forms
	langs = lp.langs

	splitforms = split_forms(forms, polysymbols)

	maxlength = max_length(splitforms)
	groups = assemble_groups(splitforms, maxlength)
	matched_features = match_p_f(groups, symbols, features)

	most_prom_f = most_prom_feat(matched_features)

	matched_symbols = match_f_symbols(most_prom_f, matched_features, symbols, features)

	output = ''

	if args.verbose:
		if args.verbose > 1:
			if args.verbose > 2:
				output += """Features: {0}
				Groups: {1}
				Features per phoneme per group: {2}
				Most prominent featurs: {3}
				-----------------\n
				""".format(features, groups, matched_features, most_prom_f)
			if matched_features[1] != []:
				output += 'The following features had no match in the database: {0}\n'.format(matched_features[1])

		if len(unmatched_symbols) != 0:
			output += 'The following symbols were not in the database: {0}\n'.format(unmatched_symbols)
	
	output += 'The reconstructed form is *{0}'.format(matched_symbols[0])

	if args.log:
		logfile = open('reconstruction_log.txt', 'a')
		dt = datetime.datetime
		logfile.write('\n\n{0}\n-----------------\n'.format(dt.isoformat(dt.now())))
		logfile.write(output)
		logfile.close()

	print(output)

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
	# this list will contain the indexes of polysymbollic phonemes in the form
	indexes = []

	# iterate over the polysymbols to get the indexes
	for polysymbol in polysymbols:
		# temporary form variable to remove polysymbols already accounted for from it
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
			adjust += 1

		splitform = ls
		return splitform

# get the length of the longest form
def max_length(forms):
	forms.sort(key=len, reverse=True)
	return len(forms[0])

# assembles phoneme groups, still only works for 1:1 matches
def assemble_groups(forms, maxlength):
	s_groups = []
	p_count = 0
	while p_count < maxlength:
		cur_group = []
		for n in forms:
			if n not in cur_group:
				try:
					cur_group.append(n[p_count])
				except IndexError:
					cur_group.append('-')
		s_groups.append(cur_group)
		p_count += 1
	return s_groups

# match phonemes to their features
def match_p_f(p_groups, symbols, features):
	matched_features = []
	# iterate over phoneme groups
	for group in p_groups:
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

# select most prominent features
def most_prom_feat(features):
	# collections module to get the most common property (see below)
	p_features = []
	# iterate over groups of phonemic features
	for group_n, groups in enumerate(features):
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
			# print('Current phoneme: %s' % cur_phon)
			cur_group.append(cur_phon)
		p_features.append(cur_group[0])

	return p_features

# match theoretical phonemes as features to IPA symbols in the database
def match_f_symbols(mcf, matched_features, symbols, features):
	matched_symbols = []
	unmatched_features = []
	for n, feature in enumerate(mcf):
		if feature in features:
			matched_symbols.append(symbols[features.index(feature)])
		else:
			# this should be temporary
			matched_symbols.append('-')
			unmatched_features.append(feature)
	unmatched_features = list(filter(None, unmatched_features))
	return (''.join(matched_symbols), unmatched_features)

if __name__ == "__main__":
	main()