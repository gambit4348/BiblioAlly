"""
Declares and exports the domain objects that describe each entities existing in the BiblioAlly Catalog.

The domain classes declared in this module carry annotations specific to be worked by SQL Alchemy, the
ORM engine used to persist and retrieve the objects during a session of BiblioAlly.
"""

import datetime
from sqlalchemy import Table, ForeignKey, Column, Integer, String, Date, Boolean, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import registry, relationship

TAG_ACCEPTED = 'accepted'
TAG_DUPLICATE = 'duplicate'
TAG_EXCLUDED = 'excluded'
TAG_IMPORTED = 'imported'
TAG_PRE_ACCEPTED = 'pre-accepted'

biblioally_mapper = registry()
Base = biblioally_mapper.generate_base()


Document_Keyword = Table('Document_R_Keyword', Base.metadata,
                         Column('document_id', ForeignKey('Document.id'), primary_key=True),
                         Column('keyword_id', ForeignKey('Keyword.id'), primary_key=True),
                         )


class DocumentAuthor(Base):
    """
    Describes the relationship between a Document and an Author.

    Since a Document my have more than one Author and a given Author may be referenced by more than one Document,
    this class registers the relationship between those two classes.

    Going beyond than simply registering the relationship, instances of this class also identify which Author is the
    first one (also named "the corresponding author") and what was the Author's affiliation at the time the
    Document was published.
    """

    __tablename__ = 'Document_R_Author'
    document_id = Column(ForeignKey('Document.id'), primary_key=True)
    document = relationship('Document')
    author_id = Column(ForeignKey('Author.id'), primary_key=True)
    author = relationship('Author')
    first = Column(Boolean, nullable=False)
    institution = relationship('Institution')
    institution_id = Column(Integer, ForeignKey('Institution.id'))

    def __repr__(self):
        return f'DocumentAuthor(author={self.author!r}, first={self.first!r})' +\
               f'institution={self.institution!r})'


class DocumentTag(Base):
    """
    Describes the relationship between a Document and a Tag.
    """

    __tablename__ = 'Document_R_Tag'
    document_id = Column(ForeignKey('Document.id'), primary_key=True)
    document = relationship('Document')
    tag_id = Column(ForeignKey('Tag.id'), primary_key=True)
    tag = relationship('Tag')

    def __repr__(self):
        return f'DocumentTag(document={self.document!r}, tag={self.tag!r})'


class Author(Base):
    """
    The author of a given Document.
    """

    __tablename__ = 'Author'
    id = Column(Integer, primary_key=True)
    short_name = Column(String(30), nullable=False, index=True)
    long_name = Column(String(255))

    def __init__(self, short_name, long_name=None):
        Base.__init__(self)
        self.short_name = short_name
        self.long_name = long_name

    @staticmethod
    def short_name_from_name(name):
        pieces = name.split(' ')
        names = []
        if len(pieces) == 1:
            return name
        for index in range(1, len(pieces)):
            names.append(pieces[index][0] + '.')
        return pieces[0] + ' ' + ' '.join(names)

    @property
    def name(self):
        return self.long_name if self.long_name != '' else self.short_name

    def __hash__(self):
        return hash(self.short_name)

    def __repr__(self):
        return f'Author(id={self.id!r}, short_name={self.short_name!r}, long_name={self.long_name!r})'


class Document(Base):
    """
    The bibliographic reference to a document that reports the results of a research.

    A instance of Document represents a bibliographic reference, like a BibTeX entry, with a number of attributes
    that describe the published research document.

    A Document can have:
        -one or more Authors, one of them marked as the first author;
        -zero or more Keywords that hint about the themes discussed in the document;
        -zero or more References to other scientific documents used to fundament the research;
        -one or more Tags that somehow register some particular condition fo interest;
        -zero or one DocumentMetadata that record the important data extracted from the document full text.
    """

    __tablename__ = 'Document'
    id = Column(Integer, primary_key=True)
    title = Column(String(255, collation='NOCASE'), nullable=False)
    title_crc32 = Column(Integer, nullable=False, index=True)
    abstract = Column(String, nullable=False)
    external_key = Column(String(128), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    kind = Column(String(255), nullable=False)
    journal = Column(String(255))
    publisher = Column(String(64))
    address = Column(String(255))
    pages = Column(String(30))
    volume = Column(String(30))
    number = Column(String(30))
    doi = Column(String(128))
    international_number = Column(String(64))
    url = Column(String(255))
    language = Column(String(32))
    document_type = Column(String(32))
    generator = Column(String(32), nullable=False)
    import_date = Column(Date, nullable=False)
    authors = relationship('DocumentAuthor', cascade='all, delete-orphan', back_populates='document')
    keywords = relationship('Keyword', secondary=Document_Keyword)
    tags = relationship('DocumentTag', cascade='all, delete-orphan', back_populates='document')
    references = relationship('Reference', cascade='all, delete', back_populates='document')
    original_document_id = Column(Integer, ForeignKey('Document.id'))
    original_document = relationship('Document', uselist=False)
    review_metadata = relationship('DocumentMetadata', uselist=False, back_populates='document',
                                   cascade="all, delete-orphan")

    def __init__(self, external_key, kind, title, abstract, keywords, year, affiliations):
        Base.__init__(self)
        self.title = title
        self.abstract = abstract
        self.external_key = external_key
        self.kind = kind
        if type(keywords) == Keyword:
            self.keywords.append(keywords)
        elif type(keywords) == list:
            for keyword in keywords:
                self.keywords.append(keyword)
        self.year = year
        if type(affiliations) == DocumentAuthor:
            self.affiliations.append(affiliations)
        elif type(affiliations) == list:
            for affiliation in affiliations:
                self.authors.append(affiliation)

    @hybrid_property
    def first_author(self):
        if not hasattr(self, '_first_author'):
            setattr(self, '_first_author', self._the_first_author())
        return self._first_author

    def has_keyword(self, keyword_name):
        keywords = [keyword for keyword in self.keywords if keyword.name == keyword_name]
        return len(keywords) > 0

    def is_tagged(self, tag):
        if type(tag) is str:
            tags = [doc_tag.tag for doc_tag in self.tags if doc_tag.tag.name == tag]
        elif type(tag) is Tag:
            tags = [doc_tag.tag for doc_tag in self.tags if doc_tag.tag.id == tag.id]
        return len(tags) > 0

    def untag(self, tags):
        if type(tags) is not list:
            tags = [tags]
        for tag in tags:
            if type(tag) is str:
                for doc_tag in self.tags:
                    if doc_tag.tag.name == tag:
                        self.tags.remove(doc_tag)
                        break
            elif type(tag) is Tag:
                for doc_tag in self.tags:
                    if doc_tag.tag.id == tag.id:
                        self.tags.remove(doc_tag)
                        break
        return self.tags

    def _the_first_author(self) -> Author:
        for document_author in self.authors:
            if document_author.first:
                return document_author.author
        if len(self.authors) > 0:
            return self.authors[0].author
        return None

    def __repr__(self):
        return f'Document(id={self.id!r}, title={self.title!r}, year={self.year!r}, doi={self.doi!r})'


class DocumentMetadata(Base):
    """
    Describes the relationship between a Document and a DocumentMetadata.
    """

    __tablename__ = 'Document_Metadata'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    import_date = Column(Date, nullable=False)
    document_id = Column(Integer, ForeignKey('Document.id'), nullable=False, unique=True, index=True)
    document = relationship('Document', back_populates='review_metadata', foreign_keys=[document_id])

    def __init__(self, content, import_date=None):
        Base.__init__(self)
        self.content = content
        if import_date is None:
            self.import_date = datetime.date.today()

    def __repr__(self):
        return f'DocumentMetadata(id={self.id!r}, content={self.content!r})'


class Institution(Base):
    """
    Describes an institution to which an Author may be affiliated.
    """

    __tablename__ = 'Institution'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    country = Column(String(30))
    import_date = Column(Date, nullable=False)

    def __repr__(self):
        return f'Institution(id={self.id!r}, name={self.name!r}, country={self.country!r})'


class Keyword(Base):
    """
    Describes a Keyword that hints about a theme discussed by a Document.
    """

    __tablename__ = 'Keyword'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True, index=True)
    import_date = Column(Date, nullable=False)

    def __repr__(self):
        return f'Keyword(id={self.id!r}, name={self.name!r})'


class Reference(Base):
    """
    Describes a bibliographic reference listed by a given Document.
    """

    __tablename__ = 'Reference'
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    document = relationship('Document')
    document_id = Column(Integer, ForeignKey('Document.id'), index=True)

    def __repr__(self):
        return f'Reference(id={self.id!r}, name={self.description!r})'


class Tag(Base):
    """
    Describes a Tag that identifies some particular condition of a given Document.

    Some Tags are created when the Catalog is first opened:
        -accepted: informs that a Document is selected for the literature review after the deep screening;
        -duplicate: informs that a Document is a duplicate of other;
        -excluded: informs that a Document is rejected for the literature review;
        -imported: informs that a Document is just imported into the Catalog;
        -pre-accepted: informs that a Document is pre-selected for the literature review after the shallow screening;
    """

    __tablename__ = 'Tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    create_date = Column(Date, nullable=False)
    system_tag = Column(Boolean, nullable=False)

    def __init__(self, name, create_date=None):
        Base.__init__(self)
        self.name = name
        self.system_tag = False
        if create_date is None:
            self.create_date = datetime.date.today()

    def __repr__(self):
        return f'Tag(id={self.id!r}, name={self.name!r}, import_date={self.create_date!r})'
