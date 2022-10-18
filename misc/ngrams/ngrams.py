from collections import Counter
from itertools import chain
from typing import Iterable, Iterator
from string import whitespace, ascii_lowercase

def clean(text: Iterable[str], keep: Iterable[str] = None) -> str:
    keep = set(whitespace if keep is None else keep)
    return ''.join(filter(lambda c: c.isalpha() or c in keep, text)).lower()

def ngrams(text: Iterable[str], n: int, keep: Iterable[str] = None) -> Iterator[str]:
    '''Returns ngrams in the text, in order of apparition.
    By default, doesn't count ngrams separated by whitespace: set keep = '' to get rid of this behavior.'''
    return map(''.join, chain.from_iterable(zip(*[word[i:] for i in range(n)]) for word in clean(text, keep = keep).split()))

def occurences(text: Iterable[str], n: int, keep: Iterable[str] = None) -> Counter[str]:
    '''Count the number of occurences of each ngram in the given text.
    By default, count no n-gram crossing words separated by whitespace.
    Set `keep = ''` to get rid of whitespaces.'''
    return Counter(ngrams(text, n, keep))

def ngram_freq(ngram: Iterable[str], refcount: dict[str, int], reftotal: int = None) -> float:
    '''Frequency of ngram among all ngrams for a given reference'''
    reftotal = reftotal or sum(refcount.values())
    return refcount.get(''.join(ngram), 0) / reftotal

def score(text: Iterable[str], n: int, refcount: dict[str, int], reftotal: int = None) -> float:
    '''Useful as heuristic to distinguish between candidates in "likeness with respect to reference".
    If A has more n-grams in common with refcount than B, then score(A, n, refcount) > score(B, n, refcount)
    Example:
        n = 3 # trigrams
        refcount = occurences(some_long_english_text, n)
        if score(A, n, refcount) > score(B, n, refcount):
            print("A looks more like english than B")
        else:
            print("A looks less like english than B")
    '''
    reftotal = reftotal or sum(refcount.values())
    return sum(refcount.get(ngram, 0) for ngram in ngrams(text, n)) / reftotal

def ioc(text: Iterable[str], n: int = 1, alphabet: Iterable[str] = ascii_lowercase):
    '''Return n-gram index of coincidence of the text for the given alphabet'''
    N = len(text)
    return sum(f * (f - 1) for f in occurences(text, n, alphabet).values()) / (N*N - N)
