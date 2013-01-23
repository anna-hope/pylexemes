#!/usr/bin/env python3.3
# Anton Osten
# http://ostensible.me

import collections as c
import itertools as i
from phonemeparser import PhonemeParser
from lexemeparser import LexemeParser

def main():
	# call the parsers
	pp = PhonemeParser()
	lp = LexemeParser()

	# consonants
	symbols = pp.symbols
	features = pp.features
	# print('Features: %s\n' % features)

	# forms and languages
	forms = lp.forms
	langs = lp.langs

	# print("The forms are: %s" % forms)

	maxlength = max_length(forms)
	groups = assemble_groups(forms, maxlength)
	# print(groups)
	matched_features = match_p_f(groups, symbols, features)
	# print("Features per phoneme per group: %s" % matched_features)
	most_prom_f = most_prom_feat(matched_features)
	# print('Most prominent featurs: %s' % most_prom_f)
	matched_symbols = match_f_symbols(most_prom_f, matched_features, symbols, features)
	print ('The reconstructed form is most possibly: *%s' % matched_symbols[0])
	print('Unmatched theoretical phonemes: %s' % matched_symbols[1])

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
def match_p_f(p_groups, symbols, features):
	matched_features = []
	# iterate over phoneme groups
	for n in p_groups:
		# current phoneme feature group
		cur_feat_g = []
		# iterate over phonemes in each group
		for pn in n:
			if pn in symbols:
				cur_feat_g.append(features[symbols.index(pn)])
			else:
				cur_feat_g.append(['', '', ''])
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
			# iterate over each property (manner, height, etc.) in each phoneme
			for prop_n, props in enumerate(phonemes):
				cur_prop = []
				# iterate over phonemes in each group again to get the property at the same place
				# (i.e. just manner, or just voice)
				for n, x in enumerate(groups):
					# append the property at that place to the list of properties at that place
					try:
						#print("Current property: %s" % groups[n][prop_n])
						cur_prop.append(groups[n][prop_n])
					except Exception as e:
						print(e)
						cur_prop.append('')
				# append the most common property at that place to list of features for current phoneme
				cur_phon.append(c.Counter(cur_prop).most_common(1)[0][0])
			# append the current theoretical phoneme to the list of phonemes as features
			print('Current phoneme: %s' % cur_phon)
			cur_group.append(cur_phon)
		p_features.append(cur_group[0])

	return p_features

# match theoretical phonemes as features to IPA symbols in the database
def match_f_symbols(mcf, matched_features, symbols, features):
	matched_symbols = []
	unmatched_features = []
	for n, feature in enumerate(mcf):
		feature = list(filter(None, feature))
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