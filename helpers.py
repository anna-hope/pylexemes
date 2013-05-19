# helper classes for the reconstructor
# (c) Anton Osten
# http://ostensible.me

import re
from collections import namedtuple
from difflib import SequenceMatcher
try:
    import simplejson as json
except ImportError:
    from warnings import warn
    warn(UserWarning('simplejson not found. Using site-provided json, parsing may be slower.'))
    import json
    
# custom errors

class CustomError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class SegmentParsingError(CustomError):
    pass

class FormParsingError(CustomError):
    pass

class BadFormQueryError(CustomError):
    pass

class SegmentParser:
    '''Loads and parses segments from the segments.json file'''

    def __init__(self, segments_f=None):

        try:
            if segments_f == None:
                segments = json.load(open('segments.json'))
            else:
                segments = json.load(open(segments_f))
        except Exception as e:
            self.somethingwrong(e)

        self.segments = segments
        self.symbols = []
        self.names = {}
        self.features = {}
        
        # a named tuple for storing the features of segments
        Features = namedtuple('Features', sorted(segments[0]['features'].keys()))

        try:
            for n in self.segments:
                symbol = n['symbol']
                self.symbols.append(symbol)
                self.names[symbol] = n['name']
                self.features[symbol] = Features(**n['features'])

        except Exception as e:
            self.somethingwrong(e)
        
        # this is useful for mapping features back to symbols
        self.flipped_features = {self.features[segment]: segment for segment in self.features}

        polysymbols = [n for n in self.symbols if len(n) > 1]
        self.polysymbols = polysymbols

        true_features = {}
        for s in self.features:
            segment_features = vars(self.features[s])
            segment_true_features = [f for f in segment_features if segment_features[f]]
            true_features[s] = segment_true_features
        self.true_features = true_features
        self.duplicates = self.find_duplicates()

    def find_duplicates(self):
        doc = "Returns segments with the same features."
        # the two lists are needed to keep indexes in sync
        done_symbols = []
        done_features = []
        duplicate_groups = []
        for s in self.features:
            # features of the current segment
            cur_features = self.features[s]
            if cur_features in done_features:
                for duplicate_group in duplicate_groups:
                    # if there is already more than a pair of segments with the same features
                    # we'll do this to add the current segment to the list of those duplicates
                    # first checking that we're not adding a duplicate (ha!) symbol
                    if done_symbols[done_features.index(cur_features)] in duplicate_group:
                        symbol = [s for s in self.features if (
                                            s not in duplicate_group
                                            and self.features[s] == cur_features)][0]
                        duplicate_group.append(symbol)
                        break
                else:
                    # otherwise just append it as a list 
                    duplicate_groups.append([done_symbols[done_features.index(cur_features)], s])
            else:
                done_symbols.append(s)
                done_features.append(self.features[s])
        return duplicate_groups

    def somethingwrong(self, e):
        '''Invoked when something goes wrong with the segments.json file.'''
        raise SegmentParsingError(e)
        
class FormParser:
    '''Parses forms to compute reconstructions from'''

    def __init__(self, file):

        try:
            self.lexemes = json.load(open(lexemefile))
        except ValueError as ve:
            self.somethingwrong(e)
        except FileNotFoundError:
            self.create_dummy()
            
        self.lang_names = []
        self.lang_codes = []
        self.true_recs = None
        raw_forms = []

        for n in self.lexemes:
            try:
                if n['lang_name'].casefold() == 'key':
                    self.true_recs = re.findall('[\w-]+', n['forms'])
                else:
                    self.lang_names.append(n['lang_name'])
                    self.lang_codes.append(n['lang_code'])
                    lang_forms = re.findall('[\w-]+', n['forms'])
                    raw_forms.append((lang_forms, n['lang_code']))
            except KeyError as ke:
                self.somethingwrong(ke)


        self.forms = self.sort_forms(raw_forms)
        self.store_lang_info(self.lang_names, self.lang_codes)

    def sort_forms(self, raw_forms):
        numlangs = len(raw_forms)
        numforms = len(raw_forms[0][0])
        sorted_forms = []
        for num in range(numforms):
            cur_forms = []
            for n, lang in enumerate(raw_forms):
                cur_forms.append(raw_forms[n][0][num])
            sorted_forms.append(cur_forms)
        return sorted_forms

    def create_dummy(self):
        doc = "Creates a dummy lexemes.json file if one isn't found."
        print("JSON file for lexemes was not found. Creating a dummy.")
        dummydata = [{"lang_name": "alalalian", "lang_code": "???", "forms": "dvronts"},
         {"lang_name": "boblabian", "lang_code": "???", "forms": "txovant"}, 
         {"lang_name": "cycoclian", "lang_code": "???", "forms": "lwa"}]
        json.dump(dummydata, open('dummydata.json', 'w'))
        self.lexemes = json.load(open('dummydata.json', 'r'))

    def store_lang_info(self, lang_names, lang_codes):
        doc = "Stores language name and three letter ISO code in a langs.json file for future reference."
        try:
            langs = json.load(open('langs.json'))
        except:
            langs = json.loads('{}')
        for lang_name, lang_code in zip(lang_names, lang_codes):
            if '?' not in lang_code and lang_name.title() not in langs:
                # check if this language isn't named differently in the database
                match_code = [lang for lang in langs if langs[lang] == lang_code.casefold()]
                if match_code == []:
                    # if there isn't  a language with that code, we'll add it
                    langs[lang_name.title()] = lang_code.casefold()
                else:
                    # if there is a language with that code, but it's named differently, we could change the current instance of it
                    # but I'm not sure I want to do that
                    pass
        if langs != json.load(open('langs.json')):
            json.dump(langs, open('langs.json', 'w'))

    def somethingwrong(self, e):
        doc = "Invoked when there is something wron in the lexemes.json file."
        print("Error with %s" % e)
        raise SegmentParsingError('''It seems that there is something wrong in the JSON file for lexemes. 
        Check it over and run me again.''')
    
class Form:
    '''A form'''
    
    sp = SegmentParser()
    
    def __init__(self, form, lang_code=None, gloss=None):
        # if it's a list or a string
        if isinstance(form, (str, list)):
            # if it's string
            if isinstance(form, str):
                # the string representation is the form itself
                self.str = form
                # tokenise it into segments
                self.segments = self._tokenise()
                # create a feature representation
                self.features = self._to_features()
            # if it's a non-empty list
            elif form != []:
                # its segments need to be converted into IPA symbols
                self.segments = self._to_symbols(form)
                # its string representation are the joined segments
                self.str = ''.join(self.segments)
            else:
                raise ValueError('Empty list given')
            # assign it the language code and the gloss
            self.lang_code = lang_code
            self.gloss = gloss
        elif isinstance(form, dict):
            if ['form'] in form and ['lang_code'] in form and ['gloss'] in form:
                self.str = form['form']
                self.segments = self._tokenise
                self.features = self._to_features()
                self.lang_code = form['lang_code']
                self.gloss = form['gloss']
            else:
                raise ValueError('Dictionary keys invalid')
        else:
            raise TypeError('Must be str, list of features or dict')
    
    def __str__(self):
        return self.str
    
    def __repr__(self):
        return 'Form({form_as_str}, {lang_code}, {gloss})'.format(form_as_str = self.str,
                                                              lang_code = self.lang_code,
                                                              gloss = self.gloss)
    
    def __eq__(self, form):
        return (self.str == form.str 
                and self.lang_code == form.lang_code
                and self.gloss == form.gloss)
                
    def __hash__(self):
        # the operators in the hash value calculation are pretty much random
        return ~(hash(self.str) | hash(self.lang_code) * hash(self.gloss))
    
    def _tokenise(self):
        '''Splits a form into separate symbols.
        Detects polysymbollic segments such as affricates.'''
        segments = []
        i = 0
        while i < len(self.str):
            cur_segment = self.str[i]
            next_segment = self.str[(i + 1) % len(self.str)]
            if cur_segment + next_segment in self.sp.polysymbols:
                segments.append(cur_segment + next_segment)
                i += 2
            else:
                segments.append(cur_segment)
                i += 1
        return segments
    
    def _to_features(self):
        """Retrieves features for a given IPA symbol"""
        form_features = []
        for segment in self.segments:
            segment_features = self.sp.features.get(segment)
            form_features.append(segment_features)
        return form_features
    
    def _to_symbols(self, form):
        symbols = []
        for segment in form:
            if segment in self.sp.flipped_features:
                symbols.append(self.sp.flipped_features[segment])
            # if it's in there, get the closest one
            else:
                sim_ratios = {symbol: SequenceMatcher(None,
                                 self.sp.features[symbol], segment).ratio()
                                      for symbol in self.sp.features}
                closest_match = max(sim_ratios, key=sim_ratios.get)
                symbols.append('({})'.format(closest_match))
        return symbols
                
    
    @property
    def structure(self):
        struct = []
        for feature in self.features:
            if feature.cons:
                struct.append('C')
            else:
                struct.append('V')
        return struct

class CognateSet:
    '''A cognate set is a set-like collection of Form objects'''
    
    def __init__(self, forms=None):
        if forms is None:
            self.forms = set()
        else:
            if isinstance(forms, Form):
                self.forms = {forms}
            elif isinstance(forms, set):
                for x in forms:
                    if not isinstance(x, Form):
                        raise TypeError('Must be a list of Form objects')
                else:
                    self.forms = forms
    
    def __iter__(self):
        return iter(self.forms)
    
    def __len__(self):
        return len(self.forms)
    
    def __contains__(self, form=None, lang_code=None):
        if form is not None:
            if isinstance(form, Form):
                return form in self.forms
            elif isinstance(form, str):
                for f in self.forms:
                    if f.str == form:
                        return True
                else:
                    return False
            else:
                raise TypeError('Query must be a Form object or str')
        elif lang_code is not None:
            for f in self.forms:
                if f.lang_code == lang_code:
                    return True
            else:
                return False
        else:
            raise BadFormQueryError(
                        'Need a form object, its string representation, or a language code')
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        if len(self.forms) == 0:
            return 'CognateSet()'
        else:
            return 'CognateSet({})'.format(str(self.forms))
    
    def add(self, form):
        if isinstance(form, Form):
            self.forms.add(form)
        else:
            raise TypeError('Must be a Form object')
    
    def get(self, form_as_str=None, lang_code=None):
        if not self.__contains__(form_as_str, lang_code):
            return None
            
        if form_as_str is not None:
            for form in self.forms:
                if form.str == form_as_str:
                    return form
                    
        elif lang_code is not None:
            for form in self.forms:
                if form.lang_code == lang_code:
                    return form
        
        else:
            raise BadFormQueryError(
                        'Need a form object, its string representation, or a language code')
    
    def remove(self, form=None, lang_code=None):
        if form is not None:
            if isinstance(form, Form):
                self.forms.remove(form)
            elif isinstance(form, str):
                form_to_kill = self.get(form)
                self.forms.remove(form_to_kill)
            else:
                raise BadFormQueryError('Need a Form object or str')
        
        elif lang_code is not None:
            form_to_kill = self.get(lang_code=lang_code)
            self.forms.remove(form_to_kill)
        
        else:
            raise BadFormQueryError(
                        'Need a form object, its string representation, or a language code')    