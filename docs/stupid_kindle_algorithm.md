## The stupid kindle algorithm

The kindle algorithm for looking up words is very badly written. According to my current knowledge:

1. It looks for among all headwords (so far ignoring inflections) for the marked word, with diacritics removed. If it finds one, it returns only the one found this way, even if a better headword matching all the diacritics exists. That way it will only return ano if you look up año. But it will return él and el if you look up él
2. If it finds no results, it looks among the inflections and only returns the first one (!!??).This has been tested for spanish word fue (inflection of ir and ser) - and the exact parameter was set - where there is no difference in accent

You can set the parameter "exact", but this parameter sucks because it only works (I haven't tested it, but I assume so) for inflections and not for headwords. Another thing that is highly annoying is that it prevents the matching of uppercase words that stand (for example) at beginning of sentences. This makes it even more useless than it already is.

### What we have learned

Even if you had tried, you could not have written a worse algorithm. The author should feel bad.