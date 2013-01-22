#!/bin/sh
# Anton Osten
# http://ostensible.me

import collections
from phonemeparser import PhonemeParser
from lexemeparser import LexemeParser

def main():
	# call the parsers
	pp = PhonemeParser()
	lp = LexemeParser()

	# consonants
	cons = pp.consonants
	cons_symbols = pp.cons_symbols
	cons_features = pp.cons_features

	# vowels
	vwls = pp.vowels
	vwl_symbols = pp.vwl_symbols
	vwl_features = pp.vwl_features

	# forms and languages
	forms = lp.forms
	langs = lp.langs

	print("The forms are: %s" % forms)

	maxlength = max_length(forms)
	groups = assemble_groups(forms, maxlength)
	# print(groups)
	matched_features = match_p_f(groups, cons_symbols, cons_features, vwl_symbols, vwl_features)
	# print("Features per phoneme per group: %s" % matched_features)
	most_prom_f = most_prom_feat(matched_features)
	# print('Most prominent featurs: %s' % most_prom_f)
	matched_symbols = match_f_symbols(most_prom_f, cons_symbols, cons_features, vwl_symbols, vwl_features)
	print ('The reconstructed form is most possibly: *%s' % matched_symbols[0])

# get the length of the longest form
def max_length(forms):
	forms.sort(key=len, reverse=True)
	return len(forms[0])

# assembles phoneme groups, still only works for 1:1 matches
def assemble_groups(forms, maxlength):
	p_groups = []
	p_count = 0
	while p_count < maxlength:
		cur_group = []
		for n in forms:
			try:
				cur_group.append(n[p_count])
			except IndexError:
				cur_group.append('-')
		p_groups.append(cur_group)
		p_count += 1
	return p_groups

# match phonemes to their features
def match_p_f(p_groups, cons_symbols, cons_features, vwl_symbols, vwl_features):
	features = []
	# iterate over phoneme groups
	for n in p_groups:
		# current phoneme feature group
		cur_feat_g = []
		# iterate over phonemes in each group
		for pn in n:
			if pn in cons_symbols:
				cur_feat_g.append(cons_features[cons_symbols.index(pn)])
			elif pn in vwl_symbols:
				cur_feat_g.append(vwl_features[vwl_symbols.index(pn)])
			else:
				cur_feat_g.append([' ', ' ', ' '])
		features.append(cur_feat_g)
	return features

# select most prominent features
def most_prom_feat(features):
	# collections module to get the most common property (see below)
	c = collections
	p_features = []
	
	# iterate over groups of phonemic features
	for group_n, groups in enumerate(features):
		# iterate over phonemes in each group
		cur_group = []
		for phoneme_n, phonemes in enumerate(groups):
			cur_phon = []
			# iterate over each property (manner, height, etc.) in each phoneme
			for prop_n, props in enumerate(phonemes):
				cur_prop = []
				# iterate over phonemes in each group again to get the property at the same place
				# (i.e. just manner, or just voice)
				for n, x in enumerate(groups):
					# append the property at that place to the list of properties at that place
					cur_prop.append(groups[n][prop_n])
				# append the most common property at that place to list of features for current phoneme
				cur_phon.append(c.Counter(cur_prop).most_common(1)[0][0])
			# append the current theoretical phoneme to the list of phonemes as features
			cur_group.append(cur_phon)
		p_features.append(cur_group[0])

	return p_features

# match theoretical phonemes as features to IPA symbols in the database
def match_f_symbols(features, cons_symbols, cons_features, vwl_symbols, vwl_features):
	symbols = []
	unmatched_features = []
	for n in features:
		if n in cons_features:
			symbols.append(cons_symbols[cons_features.index(n)])
		elif n in vwl_features:
			symbols.append(vwl_symbols[vwl_features.index(n)])
		else:
			symbols.append('-')
			unmatched_features.append(n)
	return (''.join(symbols), unmatched_features)

if __name__ == "__main__":
	main()