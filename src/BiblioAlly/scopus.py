from . import translator as bibtex
from . import catalog as cat
from . import domain


class ScopusTranslator(bibtex.Translator):
    def bibtex_from_document(self, document):
        lines = []
        lines.append("author=" + self._curly([(author.longName if author.longName is not None
                                                 else author.shortName) for author in document.authors], " and "))
        lines.append("title=" + self._curly(document.title))
        if document.journal is not None:
            lines.append("journal=" + self._curly(document.journal))
        lines.append("year=" + self._curly(str(document.year)))
        if document.pages is not None:
            lines.append("pages=" + self._curly(str(document.pages)))
        if document.volume is not None:
            lines.append("volume=" + self._curly(str(document.volume)))
        if document.number is not None:
            lines.append("number=" + self._curly(str(document.number)))
        if document.doi is not None:
            lines.append("doi=" + self._curly(document.doi))
        affiliations = []
        for author in document.authors:
            if author in document.affiliations:
                affiliation = document.affiliations[author]
                affiliations.append(affiliation)

        def by_first(item):
            return item.first

        affiliations.sort(key=by_first, reverse=True)
        if len(affiliations) > 0 and not affiliations[0].first:
            raise NameError('HiThere')
        bibtex_affiliations = []
        for affiliation in affiliations:
            country = affiliation.country if affiliation.country is not None else 'Unknown'
            description = affiliation.description if affiliation.description is not None else 'Unknown'
            bibtex_affiliations.append(', '.join([description, country]))
        lines.append("affiliation=" + self._curly(bibtex_affiliations, "; "))
        lines.append("author_keywords=" + self._curly(document.keywords))
        lines.append("abstract=" + self._curly(document.abstract))
        lines.append("references=" + self._curly('; '.join(document.references)))
        if document.language is not None:
            lines.append("language=" + self._curly(str(document.language)))
        if document.document_type is not None:
            lines.append("document_type=" + self._curly(str(document.document_type)))
        lines.append("generator=" + self._curly(document.generator))

        bibTex = ",\n".join(lines)
        bibTex = "@" + document.kind.upper() + "{" + document.bibId + ",\n" + bibTex + "\n}"
        return bibTex

    def _document_from_proto_document(self, proto_document):
        kind = proto_document['type'].lower()
        if kind == 'conference':
            kind = 'inproceddings'
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


Scopus = "Scopus"
cat.Catalog.translators[Scopus] = ScopusTranslator
