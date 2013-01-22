##pylexemes by Anton Osten
anton@ostensible.me
---------------------------------------------
#v 0.2.5 notes (22 Jan 2013):
- removed the division into consonants and vowels in phonemes.json. That was stupid and made my life more complicated than it had to be. I have no idea why my brain decided it would be a good idea in the first place. Everything should be a bit simpler and more elegant now.
- reconstructor.py can do minimal (read: practically no) guessing of theoretical phonemes that are unmatched. I'll work on it more later.
- I am considering switching to Townsend-Janda phoneme feature notation because it seems like it would work better than the normal one.

#v 0.2.1.1 notes (21 Jan 2013):
- better error handling in lexemeparser and phonemeparser

#v 0.2.1 notes (21 Jan 2013):
- modified lexemeparser.py to create a dummy lexemes.json file if one isn't there for whatever reason

#v 0.2 notes (21 Jan 2013):
- Complete rewrite
- Now using json instead of XML to make it less bulky and faster (hopefully)
- Still only 1:1 matches and no support for aspiration, nasalisation, labialisation, ejectives, affricates, and many other things

#v 0.1 notes:
- Initial version

