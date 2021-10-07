import datetime
from . import domain
from functools import reduce
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import select


class Catalog:
    translators = dict()

    def __init__(self, catalog_path=None, echo=False, future=True):
        self._engine = None
        self._session = None
        if catalog_path is not None:
            self.open(catalog_path, echo, future)

    def add_summary(self, summary: domain.DocumentMetadata) -> domain.DocumentMetadata:
        """
        Add a document summary to the catalog, that will later be persisted by calling the Catalog.commit() method.

        Parameters:
            summary (domain.DocumentMetadata): the instance passed, that must be already linked to the document it
            belongs to (DocumentSummary.document).

        Returns:
            domain.DocumentMetadata: The same instance passed.
        """
        self._session.add(summary)
        return summary

    def author_by(self, **kwargs) -> domain.Author:
        """
        Query-by-example for one single author.

        Parameters:
            **kwargs :
                a list of attribute names and values that will work as an example of the desired instance.

        Returns:
            one instance, if any, of Author that corresponds to the criteria passed.

        If no instance can be found with the criteria specified, the return value is None. On the other hand, if
        more than one instance corresponds to the criteria specified, one single instance is returned but there is
        no way to predict which one.

        Example:
            catalog.author_by(short_name='Einstein, A.')
        """
        return self._session.execute(select(domain.Author).filter_by(**kwargs)).scalars().first()

    def authors_by(self, **kwargs):
        """
        Query-by-example for authors.

        Parameters:
            **kwargs :
                a list of attribute names and values that will work as an example of the desired instances.

        Returns:
            a list containing all the Authors, if any. that correspond to the criteria passed.

        If no instance can be found with the criteria specified, an empty list si returned.

        Example:
            catalog.authors_by(short_name='Einstein, A.')
        """
        return self._session.execute(select(domain.Author).filter_by(**kwargs)).scalars().all()

    def document_by(self, tagged_as=None, untagged_as=None, **kwargs):
        """
        Query-by-example for one single document.

        Parameters:
            tagged_as : (optional)
                a name or a list of names of tags that are required to be assigned to the document.
            untagged_as : (optional)
                a name or a list of names of tags that are required to not be assigned to the document.
            **kwargs :
                a list of attribute names and values that will work as an example of the desired instance.

        Returns:
            one instance, if any, of Document that corresponds to the criteria passed.

        If no instance can be found with the criteria specified, the return value is None. On the other hand, if
        more than one instance corresponds to the criteria specified, one single instance is returned but there is
        no way to predict which one.

        Example:
            catalog.documents_by(tagged_as=catalog.domain.INCLUDED,untagged_as=[catalog.domain.DUPLICATE])
            catalog.document_by(doi='biblio-ally/10000.0000')
        """
        stm = self._document_by(tagged_as=tagged_as, untagged_as=untagged_as, **kwargs)
        return self._session.execute(stm).scalars().first()

    def documents_by(self, tagged_as=None, untagged_as=None, **kwargs):
        """
        Query-by-example for documents.

        Parameters:
            tagged_as : (optional)
                a name or a list of names of tags that are required to be assigned to the document.
            untagged_as : (optional)
                a name or a list of names of tags that are required to not be assigned to the document.
            **kwargs :
                a list of attribute names and values that will work as an example of the desired instances.

        Returns:
            a list containing all the Documents, if any. that meet the criteria passed.

        If no instance can be found with the criteria specified, an empty list is returned.

        Example:
            catalog.documents_by(tagged_as=catalog.domain.INCLUDED,untagged_as=[catalog.domain.DUPLICATE])
        """
        stm = self._document_by(tagged_as=tagged_as, untagged_as=untagged_as, **kwargs)
        return self._session.execute(stm).scalars().all()

    def _document_by(self, tagged_as=None, untagged_as=None, alias=None, **kwargs):
        if alias is None:
            stm = select(domain.Document)
        else:
            stm = select(alias)
        if len(kwargs) > 0:
            stm = stm.filter_by(**kwargs)
        if tagged_as is not None or untagged_as is not None:
            stm = stm.join(domain.DocumentTag).join(domain.Tag)
        if tagged_as is not None:
            if type(tagged_as) == str:
                tagged_as = [tagged_as]
            stm = stm.where(domain.Tag.name.in_(tagged_as))
        if untagged_as is not None:
            if type(untagged_as) == str:
                untagged_as = [untagged_as]
            doc_alias = aliased(domain.Document, name=alias)
            stm = stm.where(~self._document_by(tagged_as=untagged_as, alias=doc_alias, id=domain.Document.id).exists())
        return stm

    def keyword_by(self, **kwargs):
        return self._session.execute(select(domain.Keyword).filter_by(**kwargs)).scalars().first()

    def keywords_by(self, **kwargs):
        return self._session.execute(select(domain.Keyword).filter_by(**kwargs)).scalars().all()

    def reasons(self):
        all_reasons = self._session.execute(select(domain.Reason)).scalars().all()
        all_reasons.sort(key=lambda item: item.description)
        return all_reasons

    def import_from_file(self, source, filename):
        if source not in Catalog.translators:
            return 0, 0, 0
        translator_class = Catalog.translators[source]
        translator = translator_class()
        loaded_documents = translator.documents_from_file(filename)
        authors = reduce(lambda x, y: x + y, [document.authors for document in loaded_documents])
        author_names = dict()
        for author in authors:
            name = author.author.long_name if author.author.long_name != '' else author.author.short_name
            if name not in author_names:
                author_names[name] = author.author
        institutions = [author.institution for author in authors if author.institution is not None]
        institution_names = dict()
        for institution in institutions:
            if institution.name not in institution_names:
                institution_names[institution.name] = institution
        load_count = 0
        try:
            session = self._session
            for loaded_document in loaded_documents:
                original_document = session.execute(select(domain.Document).
                                                    filter_by(title=loaded_document.title,
                                                              original_document=None)).scalars().first()
                if original_document is not None and original_document.generator == loaded_document.generator:
                    continue
                loaded_document.import_date = datetime.date.today()
                self._update_authors(loaded_document, author_names)
                self._update_institutions(loaded_document, institution_names)
                self._update_keywords(loaded_document)
                self._tag(loaded_document, domain.TAG_IMPORTED)
                load_count += 1
                if original_document is not None:
                    self._tag(loaded_document, domain.TAG_DUPLICATE)
                    loaded_document.original_document = original_document
                session.add(loaded_document)
        finally:
            self._session.commit()
            base_count = self._session.query(domain.Document).count()
        return load_count, len(loaded_documents), base_count

    def close(self):
        self._session = None
        self._engine = None

    def commit(self):
        if self.is_open:
            self._session.commit()

    def open(self, catalog_path, echo=True, future=True):
        self._engine = create_engine('sqlite+pysqlite:///' + catalog_path, echo=echo, future=future)
        self._update_database(self._engine, domain.biblioally_mapper)
        self._session = Session(self._engine)
        self._tag_by_name(domain.TAG_IMPORTED)
        self._tag_by_name(domain.TAG_DUPLICATE)
        self._tag_by_name(domain.TAG_EXCLUDED)
        self._tag_by_name(domain.TAG_PRE_ACCEPTED)
        self._tag_by_name(domain.TAG_ACCEPTED)
        self._session.commit()

    def tag(self, document, tag_name):
        return self._tag(document, tag_name)

    @staticmethod
    def untag(document, tag_name):
        document.untag(tag_name)
        return document

    @property
    def is_open(self):
        return self._session is not None

    def _add_keyword(self, document, keyword_name):
        if document.has_keyword(keyword_name):
            return document
        the_keyword = self._keyword_by_name(keyword_name)
        document.keywords.append(the_keyword)
        return document

    def _author_by_name(self, author_name, auto_create=True):
        existing_author = self._session.execute(select(domain.Author).filter_by(long_name=author_name))\
            .scalars().first()
        if existing_author is None:
            if auto_create:
                existing_author = domain.Author(name=author_name, import_date=datetime.datetime.today())
                self._session.add(existing_author)
        return existing_author

    def _institution_by_name(self, institution_name, auto_create=True):
        existing_institution = self._session.execute(select(domain.Institution).filter_by(name=institution_name))\
            .scalars().first()
        if existing_institution is None:
            if auto_create:
                existing_institution = domain.Institution(name=institution_name, import_date=datetime.datetime.today())
                self._session.add(existing_institution)
        return existing_institution

    def _keyword_by_name(self, keyword_name, auto_create=True):
        existing_keyword = self._session.execute(select(domain.Keyword).filter_by(name=keyword_name)).scalars().first()
        if existing_keyword is None:
            if auto_create:
                existing_keyword = domain.Keyword(name=keyword_name, import_date=datetime.datetime.today())
                self._session.add(existing_keyword)
        return existing_keyword

    def _tag(self, document, tag_name):
        if document.is_tagged(tag_name):
            return document
        the_tag = self._tag_by_name(tag_name)
        doc_tag = domain.DocumentTag(tag=the_tag)
        document.tags.append(doc_tag)
        return document

    def _tag_by_name(self, tag_name, auto_create=True):
        existing_tag = self._session.execute(select(domain.Tag).filter_by(name=tag_name)).scalars().first()
        if existing_tag is None:
            if auto_create:
                existing_tag = domain.Tag(name=tag_name)
                self._session.add(existing_tag)
        return existing_tag

    @staticmethod
    def _update_database(engine, mapper):
        mapper.metadata.create_all(engine)

    def _update_authors(self, document, author_names):
        for author in document.authors:
            existing_author = self._author_by_name(author.author.long_name, auto_create=False)
            if existing_author is None:
                if author.author.name in author_names:
                    existing_author = author_names[author.author.long_name]
                    existing_author.import_date = datetime.date.today()
            if existing_author is not None:
                author.author = existing_author
            else:
                author.author.import_date = datetime.date.today()

    def _update_institutions(self, document, institution_names):
        for author in document.authors:
            if author.institution is None:
                continue
            institution = self._institution_by_name(author.institution.name, auto_create=False)
            if institution is None:
                if author.institution.name in institution_names:
                    institution = institution_names[author.institution.name]
                    institution.import_date = datetime.date.today()
            if institution is not None:
                author.institution = institution
            else:
                if author.institution is not None:
                    author.institution.import_date = datetime.date.today()

    def _update_keywords(self, document):
        index = 0
        while index < len(document.keywords):
            new_keyword = document.keywords[index]
            keyword = self._keyword_by_name(new_keyword.name, auto_create=False)
            if keyword is not None:
                document.keywords.remove(document.keywords[index])
                document.keywords.insert(index, keyword)
            else:
                new_keyword.import_date = datetime.date.today()
            index += 1


all_document_fields = [
            'id', 'title', 'year', 'journal', 'external_key', 'doi', 'document_type', 'kind',
            'abstract', 'pages', 'volume', 'number', 'url', 'language', 'generator', 'import_date',
            'authors', 'keywords', 'tags', 'references', 'reason', 'review_metadata', 'original_document'
        ]


def as_dict(documents, fields=None, **kwargs):
    if type(documents) is not list:
        documents = [documents]
    if fields is None:
        fields = all_document_fields
    proto_documents = {}
    for field in fields:
        proto_documents[field] = []

    for document in documents:
        for field in fields:
            value = getattr(document, field)
            if field in kwargs and callable(kwargs[field]):
                value = kwargs[field](value)
            proto_documents[field].append(value)
    return proto_documents


def as_tuple(documents, fields=None, **kwargs):
    if type(documents) is not list:
        documents = [documents]
    if fields is None:
        fields = all_document_fields
    doc_tuples = []
    for document in documents:
        values = []
        for field in fields:
            value = getattr(document, field)
            if field in kwargs and callable(kwargs[field]):
                value = kwargs[field](value)
            values.append(value)
        doc_tuples.append(tuple(values))
    return doc_tuples
