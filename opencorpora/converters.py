# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys

from opencorpora import reader
from opencorpora.reader import CorpusReader
from russian_tagsets import converters

class UDConverter(object):
    """
    Tries to convert the data provided by CorpusReader
    to Universal Dependencies 1.4 (CoNLL-U) format.
    OpenCorpora currently has no syntax markup so
    respective fields remain empty

    Processes and returns one sentence at a time
    """

    def __init__(self, reader, docids=None, categories=None):
        assert isinstance(reader, CorpusReader)
        self.docs = reader.iter_documents(docids, categories)
        self.converter = converters.converter('opencorpora-int', 'ud14')

    def sentences(self):
        for doc in self.docs:
            for sent in doc.iter_parsed_sents():
                yield self._convert_sentence(sent)

    def _convert_token(self, token, token_no):
        if len(token[1]) > 1:
            raise Exception("Ambiguous parses cannot be converted to UD: {}".format(token[1]))
        lemma = token[1][0][0].upper()
        pos, grams = self.converter(token[1][0][1]).split()
        return '\t'.join((
            str(token_no),
            token[0],
            lemma,
            pos,
            '_',  # here should be XPOSTAG (lang-specific POS)
            grams,
            '\t'.join(['_'] * 4)  # here should be syntax and misc
        ))

    def _convert_sentence(self, sent):
        return '\n'.join(self._convert_token(token, i+1) for i, token in enumerate(sent))


if __name__ == "__main__":
    reader = CorpusReader(sys.argv[1])
    conv = UDConverter(reader)
    for sent_str in conv.sentences():
        print(sent_str.encode('utf-8') + '\n')
