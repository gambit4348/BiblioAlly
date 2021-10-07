from . import translator as bibtex
from . import catalog as cat
from . import domain


class ScopusTranslator(bibtex.Translator):
    def bibtex_from_document(self, ref):
        lines = []
        lines.append("author=" + self._curlied([(author.longName if author.longName is not None
                                                 else author.shortName) for author in ref.authors], " and "))
        lines.append("title=" + self._curlied(ref.title))
        if ref.journal is not None:
            lines.append("journal=" + self._curlied(ref.journal))
        lines.append("year=" + self._curlied(str(ref.year)))
        if ref.pages is not None:
            lines.append("pages=" + self._curlied(str(ref.pages)))
        if ref.volume is not None:
            lines.append("volume=" + self._curlied(str(ref.volume)))
        if ref.number is not None:
            lines.append("number=" + self._curlied(str(ref.number)))
        if ref.doi is not None:
            lines.append("doi=" + self._curlied(ref.doi))
        affiliations = []
        for author in ref.authors:
            if author in ref.affiliations:
                affiliation = ref.affiliations[author]
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
        lines.append("affiliation=" + self._curlied(bibtex_affiliations, "; "))
        lines.append("author_keywords=" + self._curlied(ref.keywords))
        lines.append("abstract=" + self._curlied(ref.abstract))
        lines.append("references=" + self._curlied('; '.join(ref.references)))
        if ref.language is not None:
            lines.append("language=" + self._curlied(str(ref.language)))
        if ref.document_type is not None:
            lines.append("document_type=" + self._curlied(str(ref.document_type)))
        lines.append("generator=" + self._curlied(ref.generator))

        bibTex = ",\n".join(lines)
        bibTex = "@" + ref.kind.upper() + "{" + ref.bibId + ",\n" + bibTex + "\n}"
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
            affiliations = self._affiliations_from_field(self._all_uncurlied(fields['affiliation']))
        else:
            affiliations = None
        affiliations = self._expand_affiliations(affiliations, authors)
        keywords = []
        if 'author_keywords' in fields:
            all_keywords = self._all_uncurlied(fields['author_keywords']).split(';')
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
