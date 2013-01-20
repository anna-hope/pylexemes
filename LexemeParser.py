#!/bin/sh
# Sound Changes v 0.01
# Anton Melnikov

import xml.etree.ElementTree as ET
import collections
from phonemeparser import PhonemeParser

lexemes = ET.parse("lexemes.xml")
root = lexemes.getroot()
numlexemes = len(root)

p = PhonemeParser()

def main():
	langs = get_langs()
	forms = get_forms()
	langforms = []

	for n in range (numlexemes):
		langforms.append((langs[n], forms[n]))

	print ("The languages and the forms are %s\n" % langforms)
	lengths = get_length(forms)
	phonemegroups = assemble_groups(forms, lengths[0], lengths[1])

	# print (phonemegroups)

	# yes, this is ugly, but imma gon fix it some day
	cons_symbols = p.get_cons_symbols(p.numconsonants)
	cons_features = p.get_cons_features(p.numconsonants)

	vwl_symbols = p.get_vwl_symbols(p.numvowels)
	vwl_features = p.get_vwl_features(p.numvowels)

	matched_phonemes = match_phonemes_features(phonemegroups, cons_symbols, vwl_symbols, cons_features, vwl_features)
	most_common_features = get_most_common_features(matched_phonemes)

	print("Most common phonemes according to their features are %s\n" % most_common_features)

	matched_symbols = match_pf_symbols(most_common_features, cons_symbols, cons_features, vwl_symbols, vwl_features)

	reconstructed_form = reconstruct(matched_symbols)

	print("The reconstructed form is quite possibly '*%s' " % reconstructed_form)

# get all the languages from the database
def get_langs():
	langs = []
	for n in range (numlexemes):
		langs.append(root[n].find("lang").text)
	return langs

# get all the forms from the database
def get_forms():
	forms = []
	for n in range (numlexemes):
		forms.append(root[n].find("form").text)
	return forms

# let's get the shortest form and the longest form
def get_length(forms):
	minlength = 0
	maxlength = 0

	count = 0
	while count < numlexemes:
		if (minlength == 0 and maxlength == 0):
			minlength = len(forms[count])
			maxlength = len(forms[count])
		else:
			if minlength > len(forms[count]):
				minlength = len(forms[count])
			elif maxlength < len(forms[count]):
				maxlength = len(forms[count])
		count += 1

		return [minlength, maxlength]


# assemble the phoneme groups
def assemble_groups(forms, minlength, maxlength):
	
	phonemegroups = []

	# now let's get all the phonemes according to each group
	# THIS ALGORITHM WORKS ONLY FOR 1:1 MATCHES AT THE MOMENT
	# TODO: create an xml file with phoneme groupings (w,v,etc.) and make it assemble groups according to that file
	lettercount = 0
	while lettercount < maxlength:
		count = 0
		currentgroup = []
		while count < numlexemes:
			try:
				currentgroup.append(forms[count][lettercount])
			except IndexError:
				currentgroup.append(' ')
			count += 1
		phonemegroups.append(currentgroup)
		lettercount += 1

	# print (phonemegroups)
	return phonemegroups

# match phonemes according to their features
def match_phonemes_features(phonemegroups, cons_symbols, vwl_symbols, cons_features, vwl_features):
	features = []

	# super ugly, yes
	for n in range (len(phonemegroups)):
		current_feature_group = []
		for no in range(len(phonemegroups[n])):
			if phonemegroups[n][no] in cons_symbols:
				current_feature_group.append(cons_features[cons_symbols.index(phonemegroups[n][no])])
			elif phonemegroups[n][no] in vwl_symbols:
				current_feature_group.append(vwl_features[vwl_symbols.index(phonemegroups[n][no])])
			else:
				current_feature_group.append([" ", " ", " "])
		features.append(current_feature_group)

	return features

# this takes all the features of each phoneme in each lexeme
# and takes the most frequently occuring property (voice, place, manner for Cs and closedness, height etc. for Vs)
# and assembles theoretical phonemic features according to frequency
def get_most_common_features(features):
	c = collections

	most_common_phoneme_features = []

	# UGLY UGLY UGLY AND CLUMSY AND UGLY
	for group_n in range(len(features)):
		current_group = []
		for phon_n in range(len(features[group_n])):
			current_phoneme = []
			for prop_n in range(len(features[group_n][phon_n])):
				current_properties = []
				for n in range(len(features[group_n])):
					current_properties.append(features[group_n][n][prop_n])
				current_phoneme.append(c.Counter(current_properties).most_common(1)[0][0])
			current_group.append(current_phoneme)
		most_common_phoneme_features.append(current_group[0])

	return most_common_phoneme_features

def match_pf_symbols(most_common_p_features, cons_symbols, cons_features, vwl_symbols, vwl_features):
	symbols = []
	for n in range(len(most_common_p_features)):
		if most_common_p_features[n] in cons_features:
			symbols.append(cons_symbols[cons_features.index(most_common_p_features[n])])
		elif most_common_p_features[n] in vwl_features:
			symbols.append(vwl_symbols[vwl_features.index(most_common_p_features[n])])
		else:
			symbols.append('-')

	return symbols

# reconstruct the form
# TODO: for now only works with most commonly occuring phonemes
def reconstruct(symbols):
	return ''.join(symbols)

if __name__ == "__main__":
	main()