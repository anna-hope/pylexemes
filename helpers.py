# helper classes for the reconstructor
# (c) Anton Osten
# http://ostensible.me

import re
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

        self._segments = segments
        self._symbols = []
        self._names = {}
        self._features = {}

        try:
            for n in self._segments:
                symbol = n['symbol']
                self._symbols.append(symbol)
                self._names[symbol] = n['name']
                self._features[symbol] = n['features']

        except Exception as e:
            self.somethingwrong(e)

        polysymbols = [n for n in self._symbols if len(n) > 1]
        self._polysymbols = polysymbols

        true_features = {}
        for s in self._features:
             segment_true_features = [f for f in self._features[s] if self._features[s][f]]
             true_features[s] = segment_true_features
        self._true_features = true_features
        self._duplicates = self.find_duplicates()

    def segments():
        doc = "Segments as a dictionary."
        def fget(self):
            return self._segments
        def fset(self, value):
            self._segments = value
        def fdel(self):
            del self._segments
        return locals()
    segments = property(**segments())
    
    def symbols():
        doc = "Segment symbols as a lyst."
        def fget(self):
            return self._symbols
        def fset(self, value):
            self._symbols = value
        def fdel(self):
            del self._symbols
        return locals()
    symbols = property(**symbols())

    def polysymbols():
        doc = "Polysymbols."
        def fget(self):
            return self._polysymbols
        def fset(self, value):
            self._polysymbols = value
        def fdel(self):
            del self._polysymbols
        return locals()
    polysymbols = property(**polysymbols())

    def names():
        doc = "Segment names."
        def fget(self):
            return self._names
        def fset(self, value):
            self._names = value
        def fdel(self):
            del self._names
        return locals()
    names = property(**names())

    def features():
        doc = "All segment features (including false and non-applicable)."
        def fget(self):
            return self._features
        def fset(self, value):
            self._features = value
        def fdel(self):
            del self._features
        return locals()
    features = property(**features())

    def true_features():
        doc = "Only the active features of segments."
        def fget(self):
            return self._true_features
        def fset(self, value):
            self._true_features = value
        def fdel(self):
            del self._true_features
        return locals()
    true_features = property(**true_features())

    def duplicates():
        doc = "The duplicates property."
        def fget(self):
            return self._duplicates
        def fset(self, value):
            self._duplicates = value
        def fdel(self):
            del self._duplicates
        return locals()
    duplicates = property(**duplicates())

    def find_duplicates(self):
        doc = "Returns segments with the same features."
        # the two lists are needed to keep indexes in sync
        done_symbols = []
        done_features = []
        duplicate_groups = []
        for s in self._features:
            # features of the current segment
            cur_features = self._features[s]
            if cur_features in done_features:
                for duplicate_group in duplicate_groups:
                    # if there is already more than a pair of segments with the same features
                    # we'll do this to add the current segment to the list of those duplicates
                    # first checking that we're not adding a duplicate (ha!) symbol
                    if done_symbols[done_features.index(cur_features)] in duplicate_group:
                        symbol = [s for s in self._features if (s not in duplicate_group and self._features[s] == cur_features)][0]
                        duplicate_group.append(symbol)
                        break
                else:
                    # otherwise just append it as a list 
                    duplicate_groups.append([done_symbols[done_features.index(cur_features)], s])
            else:
                done_symbols.append(s)
                done_features.append(self._features[s])
        return duplicate_groups

    def somethingwrong(self, e):
        doc = "Invoked when something goes wrong with the segments.json file."
        print(e)
        quit('It seems that there is something wrong with the json file for segments. Check it over and run me again.')
        
class FormParser:
    '''Parses forms to compute reconstructions from'''

    def __init__(self, f=None):

        if f != None:
            lexemefile = f
        else:
            lexemefile = 'lexemes.json'

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
                    # but I'm sure I want to do that
                    pass
        if langs != json.load(open('langs.json')):
            json.dump(langs, open('langs.json', 'w'))

    def somethingwrong(self, e):
        doc = "Invoked when there is something wron in the lexemes.json file."
        print("Error with %s" % e)
        raise FormParsingError('''It seems that there is something wrong in the JSON file for lexemes. 
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
                self.segments = self._tokenise(self.sp.polysymbols)
                # create a feature representation
                self.features = self._to_features(self.sp.features)
            # if it's a non-empty list
            elif form != []:
                # its segments need to be converted into IPA symbols
                self.segments = self._to_symbols(form, self.sp.features)
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
                self.lang_code = form['lang_code']
                self.gloss = form['gloss']
            else:
                raise ValueError('Dictionary keys invalid')
        else:
            raise TypeError('Must be str, list of features or dict')
    
    def __str__(self):
        return self.str
    
    def __repr__(self):
        return 'Form({})'.format(self.str)
    
    def _tokenise(self, polysymbols):
        '''Splits a form into separate symbols.
        Detects polysymbollic segments such as affricates.'''
        segments = []
        i = 0
        while i < len(self.str):
            cur_segment = self.str[i]
            next_segment = self.str[(i + 1) % len(self.str)]
            if cur_segment + next_segment in polysymbols:
                segments.append(cur_segment + next_segment)
                i += 2
            else:
                segments.append(cur_segment)
                i += 1
        return segments
    
    def _to_features(self, features):
        """Retrieves features for a given IPA symbol"""
        form_features = []
        for segment in self.segments:
            segment_features = features.get(segment)
            if segment_features is None:
                return None
            form_features.append(list(segment_features.items()))
        return form_features
    
    def _to_symbols(self, form, features):
        '''Returns symbols for a given set of features.
        Is most porbably slow and not very efficient, as well as potentially unstable.'''
        def process_segment(segment):
            # leave only the features which are true for this segmetn
            segment = [feature[0] for feature in segment if feature[1]]
            # we need to sort it so that the order is not random
            # it's quite a bit ugly
            segment = tuple(sorted(segment))
            return segment
        def guess_symbol(segment):
            ratios = {true_segments[true_segment]: difflib.SequenceMatcher(None,
                                segment, 
                                true_segment).ratio()
                                for true_segment in true_segments}
            return max(ratios, key=ratios.get)
        # phew
        flipped_features = {tuple(features[segment].items()): segment for segment in features}
        true_segments = {process_segment(segment): flipped_features[segment] for segment in flipped_features}
        # then let's process the features we are given
        given_segments = [process_segment(segment) for segment in form]
        symbols = []
        for segment in given_segments:
            if segment in true_segments:
                symbols.append(true_segments[segment])
            else:
                symbols.append('(' + guess_symbol(segment) + ')')
        return symbols

class CognateSet:
    '''A cognate set is a set-like collection of Form objects'''
    
    def __init__(self, forms):
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
        return str(self.forms)
    
    def __repr__(self):
        return str(self.forms)
    
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
                self.remove(form_to_kill)
            else:
                raise BadFormQueryError('Need a Form object or str')
        
        elif lang_code is not None:
            form_to_kill = self.get(lang_code=lang_code)
            self.forms.remove(form_to_kill)
        
        else:
            raise BadFormQueryError(
                        'Need a form object, its string representation, or a language code')    