# Anton Osten
# http://ostensible.me

import json

class LexemeParser():

	def __init__(self):
		try:
			self._lexemes = json.load(open("lexemes.json"))
		except ValueError as ve:
			self.somethingwrong(e)
		except FileNotFoundError:
			self.create_dummy()
			
		self._lang_names = []
		self._lang_codes = []
		self._forms = []

		for n in self._lexemes:
			try:
				self._lang_names.append(n['lang_name'])
				self._lang_codes.append(n['lang_code'])
				self._forms.append(n['form'])
			except KeyError as ke:
				self.somethingwrong(ke)

	def lexemes():
	    doc = "Lexemes."
	    def fget(self):
	        return self._lexemes
	    def fset(self, value):
	        self._lexemes = value
	    def fdel(self):
	        del self._lexemes
	    return locals()
	lexemes = property(**lexemes())

	def lang_names():
	    doc = "Language names."
	    def fget(self):
	        return self._lang_names
	    def fset(self, value):
	        self._lang_names = value
	    def fdel(self):
	        del self._lang_names
	    return locals()
	lang_names = property(**lang_names())

	def lang_codes():
	    doc = "ISO codes for languages"
	    def fget(self):
	        return self._lang_codes
	    def fset(self, value):
	        self._lang_codes = value
	    def fdel(self):
	        del self._lang_codes
	    return locals()
	lang_codes = property(**lang_codes())

	def forms():
	    doc = "Forms."
	    def fget(self):
	        return self._forms
	    def fset(self, value):
	        self._forms = value
	    def fdel(self):
	        del self._forms
	    return locals()
	forms = property(**forms())

	def create_dummy(self):
		doc = "Creates a dummy lexemes.json file if one isn't found."
		print("JSON file for lexemes was not found. Creating a dummy.")
		dummydata = [{"lang_name": "alalalian", "lang_code": "aaa", "form": "dvronts"},
		 {"lang_name": "boblabian", "lang_code": "bbb", "form": "txovant"}, 
		 {"lang_name": "cycoclian", "lang_code": "ccc", "form": "-l-wa----"}]
		json.dump(dummydata, open('lexemes.json', 'w'))
		self._lexemes = json.load(open('lexemes.json', 'r'))

	def somethingwrong(self, e):
		doc = "Invoked when there is something wron in the lexemes.json file."
		print("Error with %s" % e)
		quit("\nIt seems that there is something wrong in the JSON file for lexemes. Check it over and run me again.")



		