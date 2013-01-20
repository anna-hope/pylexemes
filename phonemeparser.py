#!/bin/sh
import xml.etree.ElementTree as ET

class PhonemeParser():

	def __init__(self):
		self.phonemes = ET.parse("phonemes.xml")
		self.root = self.phonemes.getroot()

		self.all_consonants = self.root[0]
		self.all_vowels = self.root[1]

		self.numconsonants = len(self.all_consonants)
		self.numvowels = len(self.all_vowels)

	def get_cons_symbols(self, numconsonants):

		cons_symbols = []

		for n in range (numconsonants):
			cons_symbols.append(self.all_consonants[n][0].text)

		return cons_symbols

	def get_vwl_symbols(self, numvowels):

		vwl_symbols = []

		for n in range (numvowels):
			vwl_symbols.append(self.all_vowels[n][0].text)

		return vwl_symbols

	def get_cons_features(self, numconsonants):

		cons_features = []

		for n in range (numconsonants):
			current_phoneme = []
			for fn in range (len(self.all_consonants[n][1])):
				current_phoneme.append(self.all_consonants[n][1][fn].text)
			cons_features.append(current_phoneme)

		return cons_features

	def get_vwl_features(self, numvowels):
		vwl_features = []

		for n in range (numvowels):
			current_phoneme = []
			for fn in range (len(self.all_vowels[n][1])):
				current_phoneme.append(self.all_vowels[n][1][fn].text)
			vwl_features.append(current_phoneme)

		return vwl_features