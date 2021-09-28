import src.bibtex.translator as bibtex
from src import catalog as cat, domain


class AcmDLTranslator(bibtex.Translator):
    def _document_from_proto_document(self, proto_document):
        kind = proto_document['type'].lower()
        fields = proto_document['field']

        title = self._unbroken(self._uncurlied(fields['title']))
        if 'abstract' in fields:
            abstract = self._unbroken(self._uncurlied(fields['abstract']))
        else:
            abstract = ''
        year = int(fields['year'])
        if 'author' in fields:
            author_field = self._unbroken(self._uncurlied(fields['author']))
        else:
            author_field = 'Author, Unamed'
        authors = self._authors_from_field(author_field)
        affiliations = self._expand_affiliations(None, authors)
        keywords = []
        if 'keywords' in fields:
            all_keywords = self._all_uncurlied(fields['keywords']).split(',')
            keyword_names = set()
            for keyword_name in all_keywords:
                name = keyword_name.strip().capitalize()
                if name not in keyword_names:
                    keyword_names.add(name)
            keyword_names = list(keyword_names)
            for keyword_name in keyword_names:
                keywords.append(domain.Keyword(name=keyword_name))
        document = domain.Document(proto_document['id'].strip(), kind, title, abstract, keywords, year, affiliations)
        document.generator = "ACM Digital Library"
        if 'journal' in fields:
            document.journal = self._uncurlied(fields['journal'])
        elif 'booktitle' in fields and kind in ['inproceedings', 'inbook']:
            document.journal = self._uncurlied(fields['booktitle'])
        for name in ['doi', 'pages', 'url', 'volume', 'number']:
            if name in fields:
                value = self._uncurlied(fields[name])
                if len(value) > 0:
                    setattr(document, name, value)
        return document


AcmDL = "AcmDL"
cat.Catalog.translators[AcmDL] = AcmDLTranslator
