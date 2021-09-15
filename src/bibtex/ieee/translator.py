import src.bibtex.translator as bibtex
from src import catalog as cat, domain


class IeeeXTranslator(bibtex.Translator):
    def _document_from_proto_document(self, proto_document):
        kind = proto_document['type'].lower()
        fields = proto_document['field']

        if 'title' in fields:
            title = self._unbroken(self._uncurlied(fields['title']))
        else:
            title = ''
        if 'abstract' in fields:
            abstract = self._unbroken(self._uncurlied(fields['abstract']))
        else:
            abstract = ''
        year = int(fields['year'])
        author_field = ''
        if 'author' in fields:
            author_field = self._unbroken(self._all_uncurlied(fields['author'].replace('}and', ' and')))
        if author_field == '':
            author_field = 'Author, Unamed'
        authors = self._authors_from_field(author_field)
        affiliations = self._expand_affiliations(None, authors)
        keywords = []
        if 'keywords' in fields:
            all_keywords = self._all_uncurlied(fields['keywords']).split(';')
            keyword_names = set()
            for keyword_name in all_keywords:
                name = keyword_name.strip().capitalize()
                if name not in keyword_names:
                    keyword_names.add(name)
            keyword_names = list(keyword_names)
            for keyword_name in keyword_names:
                keywords.append(domain.Keyword(name=keyword_name))
        document = domain.Document(proto_document['id'].strip(), kind, title, abstract, keywords, year, affiliations)
        document.generator = "IEEE Xplore"
        if 'doi' in fields:
            document.doi = self._uncurlied(fields['doi'])
        if 'journal' in fields:
            document.journal = self._uncurlied(fields['journal'])
        elif 'booktitle' in fields and kind == 'inproceedings':
            document.journal = self._uncurlied(fields['booktitle'])
        if 'number' in fields:
            if len(self._uncurlied(fields['number'])) > 0:
                document.number = self._uncurlied(fields['number'])
        if 'pages' in fields:
            if len(self._uncurlied(fields['pages'])) > 0:
                document.pages = self._uncurlied(fields['pages'])
        if 'url' in fields:
            if len(self._uncurlied(fields['url'])) > 0:
                document.url = self._uncurlied(fields['url'])
        if 'volume' in fields:
            if len(self._uncurlied(fields['volume'])) > 0:
                document.volume = self._uncurlied(fields['volume'])
        return document


IeeeXplore = "IeeeXplore"
cat.Catalog.translators[IeeeXplore] = IeeeXTranslator
