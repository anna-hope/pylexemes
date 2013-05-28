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
    warn('simplejson not found. Using site-provided json, parsing may be slower.')
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
    
# classes

class Segment:
    def __init__(self, symbol, name, features):
        self.symbol = symbol
        self.features = features
    
    def __repr__(self):
        return 'Segment({})'.format(self.symbol)
    
    def __str__(self):
        return self.symbol

class SegmentParser:
    '''Loads and parses segments from the segments.json file'''

    def __init__(self, segments_f=None):

        if segments_f == None:
            segments = json.load(open('segments.json'))
        else:
            segments = json.load(open(segments_f))

        self.segments = set()
        self.symbols = []
        self.names = {}
        self.features = {}
        
        # a named tuple for storing the features of segments
        Features = namedtuple('Features', sorted(segments[0]['features'].keys()))

        for n in segments:
            symbol = n['symbol']
            self.symbols.append(symbol)
            segment_name = n['name']
            self.names[symbol] = segment_name
            segment_features = Features(**n['features'])
            self.features[symbol] = segment_features
            self.segments.add(Segment(symbol, segment_name, segment_features))
        
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
                    '''if there is already more than a pair of segments with the same features
                    we'll do this to add the current segment to the list of those duplicates
                    first checking that we're not adding a duplicate (ha!) symbol'''
                    
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
    
    def get_segment(self, symbol):
        for segment in self.segments:
            if segment.symbol == symbol:
                return segment
    
    def parse(self, form):
        '''Tokenises a form into separate Segment objects,
        detecting polysymbollic segments such as affricates'''
        segments = []
        i = 0
        while i < len(form):
            cur_symbol = form[i]
            next_symbol = form[(i + 1) % len(form)]
            if cur_symbol + next_symbol in self.polysymbols:
                segment = self.get_segment(cur_symbol + next_symbol)
                i += 2
            else:
                segment = self.get_segment(cur_symbol)
                i += 1

            if segment is None:
                segment = Segment(cur_symbol, None, None)

            segments.append(segment)
        return segments

class Form:
    '''A form is a list of segments'''
    
    sp = SegmentParser()
    
    def __init__(self, form, lang_code=None, gloss=None):
        self.str = ''
        if isinstance(form, list):
            for segment in form:
                if isinstance(segment, Segment):
                    # build the string representation of the form
                    self.str += segment.symbol
                else:
                    raise TypeError('Must be a list of Segment objects')
                    
            # the form is a list of segments
            self.segments = form
            self.lang_code = lang_code
            self.gloss = gloss
            
        else:
            raise TypeError('Must be a list of Segment objects')               
    
    def __str__(self):
        return self.str
    
    def __repr__(self):
        return 'Form({})'.format(self.str)
        
    def __iter__(self):
        return iter(self.segments)

    def __len__(self):
        return len(self.segments)

    def __getitem__(self, key):
        return self.segments[key]
    
    def __contains__(self, segment):
        if isinstance(segment, Segment):
            return (segment in self.segments)
        elif isinstance(segment, str):
            return (segment in self.str)
        else:
            return False
    
    def __eq__(self, form):
        return (self.str == form.str
                and self.lang_code == form.lang_code
                and self.gloss == form.gloss)
                
    def __hash__(self):
        # the operators in the hash value calculation are pretty much random
        return ~(hash(self.str) | hash(self.lang_code) * hash(self.gloss))
    
    def _to_features(self):
        '''Returns a feature representation of the form'''
        return [segment.features for segment in self.segments]
    
    def _to_symbols(self, form):
        symbols = []
        for segment in form:
            if segment.features in self.sp.flipped_features:
                symbols.append(self.sp.flipped_features[segment])
                
            # if it's not in there, get the closest one
            else:
                sim_ratios = {symbol: SequenceMatcher(None,
                                 self.sp.features[symbol], segment.features).ratio()
                                      for symbol in self.sp.features}
                closest_match = max(sim_ratios, key=sim_ratios.get)
                symbols.append('({})'.format(closest_match))
        return symbols
                
    
    @property
    def structure(self):
        struct = []
        
        for segment in self.segments:
            if segment.features.syl:
                struct.append('V')
            elif segment.features.cons:
                struct.append('C')
            else:
                struct.append('S')
                
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
    
    def __contains__(self, form, lang_code=None):
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
        '''Add a Form object to the cognate set'''
        if isinstance(form, Form):
            self.forms.add(form)
        else:
            raise TypeError('Must be a Form object')
    
    def get(self, form_as_str=None, lang_code=None):
        '''Get a form by its string representation or ISO language code'''
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
        '''Remove a Form from the CognateSet using its string representation
        or ISO language code'''
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
    
    def flip(self):
        '''Flips the arrangement of the cognate set, so that each segment has its own row'''
        pass
    
    @property
    def langs(self):
        '''A set of ISO language codes present in the cognate set'''
        return {form.lang_code for form in self.forms}
    
    @property
    def average_len(self):
        '''Returns the rounded average length of all forms in the cognate set'''
        lengths = [len(form) for form in self.forms]
        return round(sum(lengths) / len(lengths))
                        
                        
class FormParser:
    '''Parses forms to compute reconstructions from'''
    
    sp = SegmentParser()

    def __init__(self, file):

        self.lexemes = json.load(open(file))
            
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
                    # if the language code is unknown, let's make one up
                    # so that we can refer to it later on
                    raw_forms.append((lang_forms,
                                        self._get_lang_code(
                                        n['lang_code'], n['lang_name'])))
            except KeyError as ke:
                self._somethingwrong(ke)

        self.forms = self._process_forms(raw_forms)
        self._store_lang_info(self.lang_names, self.lang_codes)
    
    def _get_lang_code(self, lang_code, lang_name):
        '''Creates a language code for a language if it is not known'''
        # if we have a valid ISO language code
        if '?' not in lang_code:
            return lang_code
        else:
            lang_name = lang_name.casefold()
            # if it's unknown, 
            # we'll take the first, the second and the last letter of the name
            return lang_name[0] + lang_name[1] + lang_name[len(lang_name) - 1]

    def _process_forms(self, raw_forms):
        numlangs = len(raw_forms)
        numforms = len(raw_forms[0][0])
        processed_forms = []
        for num in range(numforms):
            cset = CognateSet()
            for n, lang in enumerate(raw_forms):
                # n is the language number
                # 0 or 1 is the index for either the forms in the language or its language code
                # and num is the number of a particular form in that language
                form_segments = self.sp.parse(raw_forms[n][0][num])
                lang_code = raw_forms[n][1]
                cset.add(Form(form_segments, lang_code=lang_code))
            processed_forms.append(cset)
        return processed_forms

    def _store_lang_info(self, lang_names, lang_codes):
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
                    # but I'm not sure if I want to do that
                    pass
        if langs != json.load(open('langs.json')):
            json.dump(langs, open('langs.json', 'w'))

    def _somethingwrong(self, e):
        doc = "Invoked when there is something wron in the lexemes.json file."
        print("Error with %s" % e)
        raise SegmentParsingError('''It seems that there is something wrong in the JSON file for lexemes. 
        Check it over and run me again.''')  