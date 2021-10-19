from . import translator as bibtex
from . import catalog as cat
from . import domain


class ScopusTranslator(bibtex.Translator):
    def _document_from_proto_document(self, proto_document):
        bibtex.Translator._translate_kind(proto_document)
        kind = proto_document['type']
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
            author_field = ''
        authors = self._authors_from_field(author_field)
        if 'affiliation' in fields:
            affiliations = self._affiliations_from_field(self._all_uncurly(fields['affiliation']))
        else:
            affiliations = None
        affiliations = self._expand_affiliations(affiliations, authors)
        keywords = []
        if 'author_keywords' in fields:
            all_keywords = self._all_uncurly(fields['author_keywords']).split(';')
            keyword_names = set()
            for keyword_name in all_keywords:
                name = keyword_name.strip().capitalize()
                if name not in keyword_names:
                    keyword_names.add(name)
            keyword_names = list(keyword_names)
            for keyword_name in keyword_names:
                keywords.append(domain.Keyword(name=keyword_name))
        document = domain.Document(proto_document['id'].strip(), kind, title, abstract, keywords, year, affiliations)
        document.generator = "Scopus"
        if 'document_type' in fields:
            document.document_type = self._uncurlied(fields['document_type'])
        for name in ['doi', 'pages', 'url', 'volume', 'number', 'language', 'journal']:
            if name in fields:
                value = self._uncurlied(fields[name])
                if len(value) > 0:
                    setattr(document, name, value)
        return document

        return document

    def _proto_document_from_document(self, document: domain.Document):
        kind = document.kind
        if kind == 'proceedings':
            kind = 'conference'
        fields = dict()
        fields['external_key'] = document.external_key

        doc_authors = document.authors
        doc_authors.sort(key=lambda doc_author: doc_author.first)
        doc_authors.reverse()
        all_authors = [(doc_author.author.long_name if doc_author.author.long_name is not None
                        else doc_author.author.short_name) for doc_author in doc_authors]
        fields['author'] = self._curly(all_authors, separator=' and ')

        fields['title'] = self._curly(document.title)

        affiliations = []
        for doc_author in doc_authors:
            institution = doc_author.institution
            if institution is not None:
                affiliation = ', '.join([institution.name, institution.country])
                affiliations.append(affiliation)
        if len(affiliations) > 0:
            fields['affiliation'] = self._curly(affiliations, '; ')

        fields['year'] = self._curly(str(document.year))
        if document.international_number is not None:
            fields['issn'] = self._curly(str(document.international_number))
        if document.publisher is not None:
            fields['publisher'] = self._curly(str(document.publisher))
        if document.address is not None:
            fields['address'] = self._curly(str(document.address))
        if document.doi is not None:
            fields['doi'] = self._curly(str(document.doi))
        if document.international_number is not None:
            fields['url'] = self._curly(str(document.url))
        fields['abstract'] = self._curly(document.abstract)
        if document.journal is not None:
            fields['journal'] = self._curly(str(document.journal))
        if document.pages is not None:
            fields['pages'] = self._curly(str(document.pages))
        if document.volume is not None:
            fields['volume'] = self._curly(str(document.volume))
        if document.number is not None:
            fields['number'] = self._curly(str(document.number))
        if document.language is not None:
            fields['language'] = self._curly(str(document.language))
        keywords = [keyword.name for keyword in document.keywords]
        fields['author_keywords'] = self._curly(keywords, ';  ')
        if len(document.references) > 0:
            fields['references'] = self._curly('; '.join(document.references))
        if document.document_type is not None:
            fields['document_type'] = self._curly(document.document_type)
        fields['source'] = self._curly(document.generator)

        proto_document = {
            'type': kind,
            'fields': fields
        }
        return proto_document

    def _as_bibtex(self, proto_document):
        kind = proto_document['type'].upper()
        fields = proto_document['fields']
        external_key = fields['external_key']
        del fields['external_key']
        key_value = []
        for key, value in fields.items():
            key_value.append(f'{key}={value}')
        bibtex = f'@{kind}' + '{' + f'{external_key},\n' + ',\n'.join(key_value) + '\n}\n'
        return bibtex


Scopus = "Scopus"
cat.Catalog.translators[Scopus] = ScopusTranslator
