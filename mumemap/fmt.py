import codecs
import re

# Latin-1 replacement values taken from the MUME help page.
# https://mume.org/help/latin1
latin_encoding_replacements = {
	"\u00a0": b" ",
	"\u00a1": b"!",
	"\u00a2": b"c",
	"\u00a3": b"L",
	"\u00a4": b"$",
	"\u00a5": b"Y",
	"\u00a6": b"|",
	"\u00a7": b"P",
	"\u00a8": b'"',
	"\u00a9": b"C",
	"\u00aa": b"a",
	"\u00ab": b"<",
	"\u00ac": b",",
	"\u00ad": b"-",
	"\u00ae": b"R",
	"\u00af": b"-",
	"\u00b0": b"d",
	"\u00b1": b"+",
	"\u00b2": b"2",
	"\u00b3": b"3",
	"\u00b4": b"'",
	"\u00b5": b"u",
	"\u00b6": b"P",
	"\u00b7": b"*",
	"\u00b8": b",",
	"\u00b9": b"1",
	"\u00ba": b"o",
	"\u00bb": b">",
	"\u00bc": b"4",
	"\u00bd": b"2",
	"\u00be": b"3",
	"\u00bf": b"?",
	"\u00c0": b"A",
	"\u00c1": b"A",
	"\u00c2": b"A",
	"\u00c3": b"A",
	"\u00c4": b"A",
	"\u00c5": b"A",
	"\u00c6": b"A",
	"\u00c7": b"C",
	"\u00c8": b"E",
	"\u00c9": b"E",
	"\u00ca": b"E",
	"\u00cb": b"E",
	"\u00cc": b"I",
	"\u00cd": b"I",
	"\u00ce": b"I",
	"\u00cf": b"I",
	"\u00d0": b"D",
	"\u00d1": b"N",
	"\u00d2": b"O",
	"\u00d3": b"O",
	"\u00d4": b"O",
	"\u00d5": b"O",
	"\u00d6": b"O",
	"\u00d7": b"*",
	"\u00d8": b"O",
	"\u00d9": b"U",
	"\u00da": b"U",
	"\u00db": b"U",
	"\u00dc": b"U",
	"\u00dd": b"Y",
	"\u00de": b"T",
	"\u00df": b"s",
	"\u00e0": b"a",
	"\u00e1": b"a",
	"\u00e2": b"a",
	"\u00e3": b"a",
	"\u00e4": b"a",
	"\u00e5": b"a",
	"\u00e6": b"a",
	"\u00e7": b"c",
	"\u00e8": b"e",
	"\u00e9": b"e",
	"\u00ea": b"e",
	"\u00eb": b"e",
	"\u00ec": b"i",
	"\u00ed": b"i",
	"\u00ee": b"i",
	"\u00ef": b"i",
	"\u00f0": b"d",
	"\u00f1": b"n",
	"\u00f2": b"o",
	"\u00f3": b"o",
	"\u00f4": b"o",
	"\u00f5": b"o",
	"\u00f6": b"o",
	"\u00f7": b"/",
	"\u00f8": b"o",
	"\u00f9": b"u",
	"\u00fa": b"u",
	"\u00fb": b"u",
	"\u00fc": b"u",
	"\u00fd": b"y",
	"\u00fe": b"t",
	"\u00ff": b"y",
}

latin_decoding_replacements = {
	ord(k): str(v, "us-ascii") for k, v in latin_encoding_replacements.items()
}


def latintoascii(error):
	if isinstance(error, UnicodeEncodeError):
		# Return value can be bytes or a string.
		return latin_encoding_replacements.get(error.object[error.start], b"?"), error.start + 1
	else:  # UnicodeDecodeError.
		# Return value must be a string.
		return latin_decoding_replacements.get(error.object[error.start], "?"), error.start + 1

codecs.register_error("latintoascii", latintoascii)

whitespace_regex = re.compile(r"\s+", flags=re.UNICODE)

def stringAscii(string):
	return (stringFlat(string).encode("us-ascii", "latintoascii").decode("us-ascii"))

def stringFlat(string):
	# removes all whitespace characters
	# (space, tab, newline, return, formfeed)
	return " ".join(string.split())

