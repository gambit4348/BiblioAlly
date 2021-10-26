"""
Declares and exports the main class of BiblioAlly, the Catalog class and some utility functions.
"""
import datetime
from . import domain
from .utility import alphanum_crc32
from functools import reduce
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import select


class Catalog:
    """
    Represents a BiblioAlly database.

    The Catalog class represents a BiblioAlly database, which is a SQLite file that holds all documents and
    additional data regarding a literature review.

    When a Catalog is opened for the first time, the corresponding SQLite database file is created and setup.

    Methods are provided to import and export BibTeX files (currently the only reference format supported) from and to
    various sources and targets (we call those BibTeX "dialects", since some naming conventions make them
    incompatible with each other). Currently, recognized BibTeX dialects are from ACM Digital Library, IEEE Xplore,
    Scopus and Web of Science.

    Each BibTeX dialect is identified by a registered string name and handled by a particular translator class. A
    Translator class is an artifact that knows the particularities of a certain dialect in order to read from and
    write to correctly.

    Another dialect can be added just providing and registering a new translator for it, since BiblioAlly has
    an extensible architecture for that matter.

    A Catalog holds a number of objects that are all related to each other to describe the literature review
    database (declared in module "domain"):
        -Document: The bibliographic reference to a document that reports the results of a research;
        -Author: The author of a given Document;
        -Institution: The institution to which an author were affiliated when a research was published;
        -Keyword: A keyword related to a given Document;
        -Reference: A bibliography item listed for a given Document;
        -DocumentMetadata: Metadata describing important information about a given Document;
        -Tag: a tag related to a given Document.

    Attributes:
        _engine: SqlAlchemy engine for SQLite;
        _session: SqlAlchemy session for database operations.
    """

    translators = dict()

    def __init__(self, catalog_path=None, echo=False, future=True):
        """
        Initializes a newly created instance and set it up for operation.

        Parameters:
            catalog_path: the path and file name of the catalog file;
            echo: with True all the SQL operations issued against SQLite will be echoed to the console; it is
            useful for debug operations; default is False;
            future: just passed to the SQLite engine.
        """

        self._engine = None
        self._session = None
        self._system_tags = []
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

        Example:
            catalog.add_summary(a_summary)
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

        If no instance can be found, the return is None. On the other hand, if
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
            a list containing all the Authors, if any, that correspond to the criteria passed.

        If no parameters are passed, all instances will be returned.

        If no instance can be found, an empty list is returned.

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
                a name or a list of names of tags that are required to NOT be assigned to the document.
            **kwargs :
                a list of attribute names and values that will work as an example of the desired instance.

        Returns:
            one instance, if any, of Document that corresponds to the criteria passed.

        If no instance can be found, the return is None. On the other hand, if
        more than one instance corresponds to the criteria specified, one single instance is returned but there is
        no way to predict which one.

        Example:
            catalog.document_by(tagged_as=catalog.domain.INCLUDED, untagged_as=[catalog.domain.DUPLICATE])
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
            a list containing all the Documents, if any, that meet the criteria passed.

        If no parameters are passed, all instances will be returned.

        If no instance can be found with the criteria specified, an empty list is returned.

        Example:
            catalog.documents_by(tagged_as=catalog.domain.INCLUDED, untagged_as=[catalog.domain.DUPLICATE])
        """

        stm = self._document_by(tagged_as=tagged_as, untagged_as=untagged_as, **kwargs)
        return self._session.execute(stm).scalars().all()

    def keyword_by(self, **kwargs):
        """
        Query-by-example for one single keyword.

        Parameters:
            **kwargs :
                a list of attribute names and values that will work as an example of the desired instance.

        Returns:
            one instance, if any, of Keyword that corresponds to the criteria passed.

        If no instance can be found, the return is None. On the other hand, if
        more than one instance corresponds to the criteria specified, one single instance is returned but there is
        no way to predict which one.

        Example:
            catalog.keyword_by(name='Machine Learning')
        """

        return self._session.execute(select(domain.Keyword).filter_by(**kwargs)).scalars().first()

    def keywords_by(self, **kwargs):
        """
        Query-by-example for keywords.

        Parameters:
            **kwargs :
                a list of attribute names and values that will work as an example of the desired instances.

        Returns:
            a list containing all the Keywords, if any, that meet the criteria passed.

        If no parameters are passed, all instances will be returned.

        If no instance can be found with the criteria specified, an empty list is returned.

        Example:
            catalog.keywords_by(name='Machine Learning')
        """

        return self._session.execute(select(domain.Keyword).filter_by(**kwargs)).scalars().all()

    def tag_by(self, **kwargs):
        """
        Query-by-example for one single tag.

        Parameters:
            **kwargs :
                a list of attribute names and values that will work as an example of the desired instance.

        Returns:
            one instance, if any, of Tag that corresponds to the criteria passed.

        If no instance can be found, the return is None. On the other hand, if
        more than one instance corresponds to the criteria specified, one single instance is returned but there is
        no way to predict which one.

        Example:
            catalog.tag_by(name='accepted')
        """

        return self._session.execute(select(domain.Tag).filter_by(**kwargs)).scalars().first()

    def tags_by(self, **kwargs):
        """
        Query-by-example for tags.

        Parameters:
            **kwargs :
                a list of attribute names and values that will work as an example of the desired instances.

        Returns:
            a list containing all the Tags, if any, that meet the criteria passed.

        If no parameters are passed, all instances will be returned.

        If no instance can be found with the criteria specified, an empty list is returned.

        Example:
            catalog.tags_by(name='accepted')
        """

        return self._session.execute(select(domain.Tag).filter_by(**kwargs)).scalars().all()

    def import_from_file(self, source: str, filename: str):
        """
        Imports references from a file.

        Parameters:
            source :
                the identifier of the BibTex dialect.
            filename :
                the file name of the .bib file to be imported.

        Returns:
            the amount of documents added;
            the amount of documents present in the .bib file;
            the amount of documents in the BiblioAlly base after the import.

        BiblioAlly comes with four BibTeX translators out of the box, with the following constants as their
        identifiers:
            1. AcmDL: Translator for CMD Digital library BibTeX files.
            2. IeeeXplore: Translator for IEEE Xplore BibTeX files.
            3. Scopus: Translator for Scopus BibTeX files.
            4. WebOfScience: Translator for Web of Science BibTeX files.

        Example:
            import BiblioAlly.wos as wos
            added, loaded, total = catalog.import_from_file(wos.WebOfScience, '.\\WoS\\refs.bib')
        """

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
        added_count = 0
        try:
            session = self._session
            for loaded_document in loaded_documents:
                existing_document = session.execute(select(domain.Document).
                                                    filter_by(title_crc32=loaded_document.title_crc32))\
                    .scalars().first()
                if existing_document is not None and existing_document.generator == loaded_document.generator:
                    continue
                loaded_document.import_date = datetime.date.today()
                self._update_authors(loaded_document, author_names)
                self._update_institutions(loaded_document, institution_names)
                self._update_keywords(loaded_document)
                self._tag(loaded_document, domain.TAG_IMPORTED)
                added_count += 1
                if existing_document is not None:
                    self._tag(loaded_document, domain.TAG_DUPLICATE)
                    existing_document.duplicates.add(loaded_document)
                else:
                    session.add(loaded_document)
        finally:
            self._session.commit()
            total_count = self._session.query(domain.Document).count()
        return added_count, len(loaded_documents), total_count

    def export_to_file(self, target: str, filename: str, should_export=None):
        """
        Exports references to a file.

        Parameters:
            target :
                the identifier of the BibTex dialect.
            filename :
                the file name of the .bib file to be imported.
            should_export :
                a function or lambda that receives one Document and should return True if it is to be exported.

        Returns:
            the amount of documents exported.

        BiblioAlly comes with four BibTeX translators out of the box, with the following constants as their
        identifiers:
            1. AcmDL: Translator for CMD Digital library BibTeX files.
            2. IeeeXplore: Translator for IEEE Xplore BibTeX files.
            3. Scopus: Translator for Scopus BibTeX files.
            4. WebOfScience: Translator for Web of Science BibTeX files.

        Example:
            import BiblioAlly.catalog as ally
            import BiblioAlly.domain as domain
            import BiblioAlly.wos as wos

            total = catalog.export_to_file(wos.WebOfScience, '.\\WoS\\refs.bib',
                    export_if=lambda d: d.is_tagged(domain.TAG_ACCEPTED))
        """

        if target not in Catalog.translators:
            return 0
        translator_class = Catalog.translators[target]
        translator = translator_class()
        loaded_documents = self.documents_by()
        if should_export is not None:
            exported_documents = [d for d in loaded_documents if should_export(d)]
        else:
            exported_documents = [d for d in loaded_documents]
        exported_documents.sort(key=lambda d: d.title)
        bibtex = translator.bibtext_from_documents(exported_documents)
        with open(filename, "w", encoding="utf-8") as texFile:
            texFile.write(bibtex)
        return len(exported_documents)

    def close(self):
        """
        Closes the catalog, not allowing any other operations anymore.

        The catalog will report False in is_open property.
        """

        self._session = None
        self._engine = None
        self._system_tags = []

    def commit(self):
        """
        Commits any pending operations.

        Ignored if the catalog is not open.
        """

        if self.is_open:
            self._session.commit()

    def open(self, catalog_path: str, echo=True, future=True):
        """
        Opens the catalog and gets ready for operations.

        The catalog will report True in is_open property.
        """

        self._engine = create_engine('sqlite+pysqlite:///' + catalog_path, echo=echo, future=future)
        self._update_database(self._engine, domain.biblioally_mapper)
        self._session = Session(self._engine)
        self._system_tags = self.tags_by(system_tag=True)
        if len(self._system_tags) == 0:
            self._system_tags.append(self._tag_by_name(domain.TAG_IMPORTED, auto_create=True))
            self._system_tags.append(self._tag_by_name(domain.TAG_DUPLICATE, auto_create=True))
            self._system_tags.append(self._tag_by_name(domain.TAG_EXCLUDED, auto_create=True))
            self._system_tags.append(self._tag_by_name(domain.TAG_PRE_ACCEPTED, auto_create=True))
            self._system_tags.append(self._tag_by_name(domain.TAG_ACCEPTED, auto_create=True))
            self._session.commit()

    def tag(self, document: domain.Document, tags):
        """
        Tags a document.

        Parameters:
            document :
                the document to be tagged.
            tags :
                the tag, tag name, list of tags or list of tag names.

        Returns:
            the document after being tagged.

        If the document is already that tagged, nothing happens. If a Tag instance does not exist for the tag name
        passed, it will be created, otherwise the existing Tag will be used.
        """

        return self._tag(document, tags)

    @staticmethod
    def untag(document, tag_name):
        """
        Untags a document.

        Parameters:
            document :
                the document to be untagged.
            tag_name :
                the name of the tag.

        Returns:
            the document after being untagged.

        If the document is already that untagged, nothing happens.
        """

        document.untag(tag_name)
        return document

    @property
    def is_open(self):
        """
        Informs if the catalog is open or not.

        Returns:
            True if the catalog is open, False otherwise.
        """

        return self._session is not None

    @property
    def system_tags(self):
        """
        Returns a list with all system Tags.

        Returns:
            A list containing all the system Tags.
        """

        return self._system_tags

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

    def _tag(self, document, tags):
        if type(tags) is not list:
            tags = [tags]
        for tag in tags:
            if document.is_tagged(tag):
                continue
            if type(tag) is str:
                the_tag = self._tag_by_name(tag, auto_create=True)
            elif type(tag) is domain.Tag:
                the_tag = tag
            doc_tag = domain.DocumentTag(tag=the_tag)
            document.tags.append(doc_tag)
        return document

    def _tag_by_name(self, tag_name, auto_create=True):
        existing_tag = self.tag_by(name=tag_name)
        if existing_tag is None:
            if auto_create:
                existing_tag = domain.Tag(name=tag_name)
                existing_tag.system_tag = tag_name in [
                    domain.TAG_ACCEPTED, domain.TAG_DUPLICATE, domain.TAG_EXCLUDED, domain.TAG_IMPORTED,
                    domain.TAG_PRE_ACCEPTED
                ]
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
            'authors', 'keywords', 'tags', 'references', 'review_metadata', 'original_document'
        ]


def as_dict(documents, fields=None, **kwargs):
    """
    Translates a list of documents into a dictionary.

    Parameters:
        documents:
            the of documents to be operated;
        fields:
            the list of fields that will be translated; if None is passed, all fields will be translated;
        **kwargs:
            fields that will be pre-processed before being translated; pre-processors are functions or lambdas
            that will receive the field value and return some operated version of it.

    Returns:
        A dictionary translated from the document list.

    The format returned makes it ideal to be used to initialize a Pandas DataFrame.

    Example:
        all_documents_dict = ally.as_dict(all_documents,
                                          reason=lambda reason: reason.description if reason is not None else None,
                                          tags=lambda tags: [t.tag.name for t in tags])
    """

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
    """
    Translates a list of documents into a list of tuples.

    Parameters:
        documents:
            the of documents to be operated;
        fields:
            the list of fields that will be translated; if None is passed, all fields will be translated;
        **kwargs:
            fields that will be pre-processed before being translated; pre-processors are functions or lambdas
            that will receive the field value and return some operated version of it.

    Returns:
        A list of tuples from the document list.

    Example:
        all_documents_dict = ally.as_tuple(all_documents,
                                           reason=lambda reason: reason.description if reason is not None else None,
                                           tags=lambda tags: [t.tag.name for t in tags])
    """

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
