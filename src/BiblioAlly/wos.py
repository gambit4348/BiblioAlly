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

    def bibtex_from_document(self, document):
        lines = []
        lines.append("Title = " + self._curly(document.title))
        lines.append("Author = " + self._curly([(author.longName if author.longName is not None else author.shortName)
                                                for author in document.authors], " and "))
        affiliations = []
        for author in document.authors:
            affiliation = document.affiliations[author]
            affiliations.append(', '.join([affiliation.description, affiliation.country]))
        lines.append("Affiliations = " + self._curly(affiliations, "; "))
        lines.append("Keywords = " + self._curly(document.keywords))
        lines.append("Abstract = " + self._curly(document.abstract))
        lines.append("DA = " + self._curly(str(document.year) + "-06-01"))
        if document.doi is not None:
            lines.append("DOI = " + self._curly(document.doi))

        bibTex = ",\n".join(lines)
        bibTex = "@" + document.kind + "{" + document.bibId + ",\n" + bibTex + "\n}"
        return bibTex

    def _document_from_proto_document(self, proto_document):
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


WebOfScience = "WebOfScience"
cat.Catalog.translators[WebOfScience] = WoSBibTexTranslator
