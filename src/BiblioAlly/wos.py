from . import translator as bibtex
from . import catalog as cat
from . import domain


class WoSBibTexTranslator(bibtex.Translator):
    def _affiliations_from_field(self, affiliations_field):
        separator = '. '
        values = affiliations_field.split(separator)
        if len(values) > 1:
            values = values[1:]
            affiliations_field = separator.join(values).strip()
        if affiliations_field[-1] == '.':
            affiliations_field = affiliations_field[:len(affiliations_field) - 1]
        return super()._affiliations_from_field(affiliations_field, separator)

    def _document_from_proto_document(self, proto_document):
        bibtex.Translator._translate_kind(proto_document)
        kind = proto_document['type']
        fields = proto_document['field']

        if kind == 'book':
            title = self._unbroken(self._uncurlied(fields['Booktitle']))
        else:
            title = self._unbroken(self._uncurlied(fields['Title']))
        if 'Abstract' in fields:
            abstract = self._unbroken(self._uncurlied(fields['Abstract']))
        else:
            abstract = ''
        if 'Year' in fields:
            year = int(self._all_uncurly(fields['Year']))
        else:
            date = self._uncurlied(fields['DA'])
            year = int(self._uncurlied(fields['DA']).split('-')[0])
        author_field = self._unbroken(self._uncurlied(fields['Author']))
        authors = self._authors_from_field(author_field)
        if 'Affiliation' in fields:
            affiliations = self._affiliations_from_field(self._all_uncurly(fields['Affiliation']))
        else:
            affiliations = None
        affiliations = self._expand_affiliations(affiliations, authors)
        keywords = []
        if 'Keywords' in fields:
            all_keywords = self._all_uncurly(fields['Keywords']).split(';')
            keyword_names = set()
            for keyword_name in all_keywords:
                name = keyword_name.strip().capitalize()
                if name not in keyword_names:
                    keyword_names.add(name)
            keyword_names = list(keyword_names)
            for keyword_name in keyword_names:
                keywords.append(domain.Keyword(name=keyword_name))
        document = domain.Document(proto_document['id'].strip(), kind, title, abstract, keywords, year, affiliations)
        document.generator = "Web of Science"
        if 'DOI' in fields:
            document.doi = self._uncurlied(fields['DOI'])
        if kind == 'article':
            if 'Journal' in fields:
                document.journal = self._uncurlied(fields['Journal'])
        elif kind == 'inproceedings':
            if 'Booktitle' in fields:
                document.journal = self._uncurlied(fields['Booktitle'])
        if 'Language' in fields:
            document.language = self._uncurlied(fields['Language'])
        if 'Number' in fields:
            document.number = self._uncurlied(fields['Number'])
        if 'Pages' in fields:
            document.pages = self._uncurlied(fields['Pages'])
        if 'Volume' in fields:
            document.volume = self._uncurlied(fields['Volume'])
        if 'Type' in fields:
            document.document_type = self._uncurlied(fields['Type'])

        return document

    def _proto_document_from_document(self, document: domain.Document):
        kind = document.kind
        if kind == 'proceedings':
            kind = 'inproceedings'
        fields = dict()
        fields['external_key'] = document.external_key

        doc_authors = document.authors
        doc_authors.sort(key=lambda doc_author: doc_author.first)
        doc_authors.reverse()
        all_authors = [(doc_author.author.long_name if doc_author.author.long_name is not None
                        else doc_author.author.short_name) for doc_author in doc_authors]
        fields['Author'] = self._curly(all_authors, separator=' and ')

        fields['Title'] = self._curly(document.title, rep=2)

        affiliations = dict()
        for doc_author in doc_authors:
            institution = doc_author.institution
            if institution is not None:
                affiliation = ('*' if doc_author.first else '') + ', '.join([institution.name, institution.country])
                if affiliation not in affiliations:
                    affiliations[affiliation] = []
                affiliations[affiliation].append(doc_author)
        if len(affiliations) > 0:
            all_affiliations = []
            for affiliation, doc_authors in affiliations.items():
                all_affiliations.append(self._formatted_affiliation(affiliation, doc_authors))
            fields['Affiliations'] = self._curly(all_affiliations, '.\n', rep=2)

        fields['Year'] = self._curly(str(document.year), rep=2)
        if document.international_number is not None:
            fields['ISSN'] = self._curly(str(document.international_number), rep=2)
        if document.publisher is not None:
            fields['Publisher'] = self._curly(str(document.publisher), rep=2)
        if document.address is not None:
            fields['Address'] = self._curly(str(document.address), rep=2)
        if document.doi is not None:
            fields['DOI'] = self._curly(str(document.doi), rep=2)
        fields['Abstract'] = self._curly(document.abstract, rep=2)
        if document.journal is not None:
            if kind == 'article':
                fields['Journal'] = self._curly(str(document.journal), rep=2)
            else:
                fields['Booktitle'] = self._curly(str(document.journal), rep=2)
        if document.pages is not None:
            fields['Pages'] = self._curly(str(document.pages), rep=2)
        if document.volume is not None:
            fields['Volume'] = self._curly(str(document.volume), rep=2)
        if document.number is not None:
            fields['Number'] = self._curly(str(document.number), rep=2)
        if document.language is not None:
            fields['Language'] = self._curly(str(document.language), rep=2)
        keywords = [keyword.name for keyword in document.keywords]
        fields['Keywords'] = self._curly(keywords, ', ', rep=2)
        if document.document_type is not None:
            fields['Document-Type'] = self._curly(document.document_type)
        fields['Source'] = self._curly(document.generator)
        if len(document.references) > 0:
            references = [r.description for r in document.references]
            fields['Cited-References'] = self._curly(references, '.\n', rep=2)
            fields['Number-of-Cited-References'] = self._curly(f'{len(references)}', rep=2)

        proto_document = {
            'type': kind,
            'fields': fields
        }
        return proto_document

    def _as_bibtex(self, proto_document):
        kind = proto_document['type']
        fields = proto_document['fields']
        external_key = fields['external_key']
        del fields['external_key']
        key_value = []
        for key, value in fields.items():
            key_value.append(f'{key} = {value}')
        bibtex = f'@{kind}' + '{ ' + f'{external_key},\n' + ',\n'.join(key_value) + '\n}\n'
        return bibtex

    @staticmethod
    def _formatted_affiliation(affiliation: str, doc_authors) -> str:
        if affiliation[0] == '*':
            affiliation = affiliation[1:]
        formatted_affiliation = '; '.join([doc_author.author.long_name +
                                           (' (Corresponding Author)' if doc_author.first else '')
                                           for doc_author in doc_authors]) + ', ' + affiliation
        return formatted_affiliation


WebOfScience = "WebOfScience"
cat.Catalog.translators[WebOfScience] = WoSBibTexTranslator
