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

	# print(symbols)

	# get multisymbol phonemes
	multisymbols = []
	for n in symbols:
		if len(n) > 1:
			multisymbols.append(n)

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

# find multisymbols
def split_forms(forms, multisymbols):
	new_forms = []
	# iterate over the forms
	for form in forms:
		new_forms.append(split_affr(form, multisymbols))
	return new_forms

def split_multisymbols(form, multisymbols):
	splitform = []
	for affr in multisymbols:
		if affr in form:
			splitform = form.split(affr)
			n_affr = form.count(affr)
			if '' in splitform:
				ins_ind = splitform.index('')
				splitform = list(filter(None, splitform))
				for n in range(n_affr):
					splitform.insert(ins_ind, affr)
					ins_ind = ins_ind + 2
			else:
				ins_ind = 1
				for n in range(n_affr):
					splitform.insert(ins_ind, affr)
					ins_ind = ins_ind + 2
			# let's reinsert the non-affricate chunks as separate letters
			for n, chunk in enumerate(splitform):
				if chunk in multisymbols:
					del splitform[ind_chunk]
					chunklist = list(chunk)
					for no, l in enumerate(chunklist):
						splitform.insert((no + n), l)
				else:
					multisymbols.remove(affr)
					new_splitform = split_affr(chunk, multisymbols)
					splitform.insert(new_splitform, n)
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
						#print(e)
						cur_prop.append('')
				# append the most common property at that place to list of features for current phoneme
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