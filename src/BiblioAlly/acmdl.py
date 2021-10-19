from . import translator as bibtex
from . import catalog as cat
from . import domain


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
            all_keywords = self._all_uncurly(fields['keywords']).split(',')
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

    def _proto_document_from_document(self, document: domain.Document):
        fields = dict()
        fields['external_key'] = document.external_key
        authors = [(doc_author.author.long_name if doc_author.author.long_name is not None
                    else doc_author.author.short_name) for doc_author in document.authors]
        fields['author'] = self._curly(authors, separator=' and ')
        fields['title'] = self._curly(document.title)
        fields['year'] = self._curly(str(document.year))
        if document.international_number is not None:
            if document.kind == 'article':
                fields['issn'] = self._curly(str(document.international_number))
            else:
                fields['isbn'] = self._curly(str(document.international_number))
        if document.publisher is not None:
            fields['publisher'] = self._curly(str(document.publisher))
        if document.address is not None:
            fields['address'] = self._curly(str(document.address))
        if document.url is not None:
            fields['url'] = self._curly(str(document.url))
        if document.doi is not None:
            fields['doi'] = self._curly(str(document.doi))
        fields['abstract'] = self._curly(document.abstract)
        if document.journal is not None:
            if document.kind == 'article':
                fields['journal'] = self._curly(str(document.journal))
            else:
                fields['booktitle'] = self._curly(str(document.journal))
        if document.pages is not None:
            fields['pages'] = self._curly(str(document.pages))
        if document.volume is not None:
            fields['volume'] = self._curly(str(document.volume))
        if document.number is not None:
            fields['number'] = self._curly(str(document.number))
        keywords = [keyword.name for keyword in document.keywords]
        fields['keywords'] = self._curly(keywords, ', ')
        if document.document_type is not None:
            fields['document_type'] = self._curly(document.document_type)
        fields['source'] = self._curly(document.generator)

        proto_document = {
            'type': document.kind,
            'fields': fields
        }
        return proto_document


AcmDL = "AcmDL"
cat.Catalog.translators[AcmDL] = AcmDLTranslator
