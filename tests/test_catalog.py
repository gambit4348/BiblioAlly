import datetime
import unittest
from unittest import TestCase
from src.BiblioAlly import catalog as ba
from src.BiblioAlly import domain, acmdl as acm, ieee as ieee, scopus as scopus, wos as wos

bibtex_path = 'refs/'


class TestCatalog(TestCase):
    def setUp(self):
        self.catalog_path = 'BiblioAllyTests.db'

    def test_as_dict(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        all_documents = ally.documents_by()

        # Act
        all_documents_dict = ba.as_dict(all_documents,
                                        reason=lambda reason: reason.description if reason is not None else None,
                                        tags=lambda tags: [t.tag.name for t in tags])

        # Assert
        ally.close()
        self.assertIsNotNone(all_documents_dict, 'Document dict not retrieved')

    def test_import_refs_from_invalid(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)

        # Act
        load_count, file_count, base_count = ally.import_from_file('INVALID', bibtex_path + 'invalid.bib')

        # Assert
        self.assertEqual(load_count, 0, 'Unexpected load count')
        self.assertEqual(file_count, load_count, 'Unexpected file count')
        self.assertEqual(base_count, base_count, 'Unexpected base count')

    @unittest.skip("skipping ACM DL")
    def test_import_refs_from_acm_dl(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)

        # Act
        load_count, file_count, base_count = ally.import_from_file(acm.AcmDL, bibtex_path + 'acm_dl.bib')

        # Assert
        self.assertEqual(202, load_count, 'Unexpected load count')
        self.assertEqual(load_count, file_count, 'Unexpected file count')
        self.assertEqual(load_count, base_count, 'Unexpected base count')

    @unittest.skip("skipping IEEEXplore")
    def test_import_refs_from_ieee_xplore(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)

        # Act
        load_count, file_count, base_count = ally.import_from_file(ieee.IeeeXplore, bibtex_path + 'ieeexplore.bib')

        # Assert
        self.assertEqual(172, load_count, 'Unexpected load count')
        self.assertEqual(load_count, file_count, 'Unexpected file count')
        self.assertEqual(load_count, base_count, 'Unexpected base count')

    @unittest.skip("skipping Scopus")
    def test_import_refs_from_scopus(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)

        # Act
        load_count, file_count, base_count = ally.import_from_file(scopus.Scopus, bibtex_path + 'scopus.bib')

        # Assert
        self.assertEqual(125, load_count, 'Unexpected load count')
        self.assertEqual(load_count, file_count, 'Unexpected file count')
        self.assertEqual(load_count, base_count, 'Unexpected base count')

    @unittest.skip("skipping Web of Science")
    def test_import_refs_from_web_of_science(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)

        # Act
        load_count, file_count, base_count = ally.import_from_file(wos.WebOfScience, bibtex_path + 'web_of_science.bib')

        # Assert
        self.assertEqual(548, load_count, 'Unexpected load count')
        self.assertEqual(load_count, file_count, 'Unexpected file count')
        self.assertEqual(load_count, base_count, 'Unexpected base count')

    def test_retrieve_document_by_id(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        document_id = 1

        # Act
        document = ally.document_by(id=document_id)

        # Assert
        self.assertIsNotNone(document, f'Document with ID={document_id} not retrieved')
        self.assertEqual(document_id, document.id, 'Wrong document retrieved')

    def test_retrieve_document_not_tagged(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        tag = domain.TAG_PRE_ACCEPTED
        untag = domain.TAG_IMPORTED
        tagged_document_id = 121
        document = ally.document_by(id=tagged_document_id)
        updated = False
        if not document.is_tagged(tag):
            ally.tag(document, tag)
            updated = True
        if document.is_tagged(untag):
            ally.untag(document, untag)
            updated = True
        if updated:
            ally.commit()
            ally.close()
            ally = ba.Catalog(self.catalog_path)

        # Act
        documents = ally.documents_by(untagged_as=untag)

        # Assert
        self.assertIsNotNone(documents, f'Documents without TAG={untag} not retrieved')
        self.assertGreater(len(documents), 0, f'No documents not tagged as {untag} were retrieved')
        for doc in documents:
            self.assertTrue(doc.is_tagged(tag), f'Document {doc} not tagged as {tag}')

    def test_retrieve_document_tagged(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        tag = domain.TAG_PRE_ACCEPTED
        tagged_document_id = 121
        document = ally.document_by(id=tagged_document_id)
        if not document.is_tagged(tag):
            ally.tag(document, tag)
            ally.commit()
            ally.close()
            ally = ba.Catalog(self.catalog_path)

        # Act
        document = ally.document_by(tagged_as=tag, id=tagged_document_id)

        # Assert
        self.assertIsNotNone(document, f'Document with TAG={tag} not retrieved')
        self.assertTrue(document.is_tagged(tag), f'Document not tagged as {tag}')
        self.assertEqual(tagged_document_id, document.id, f'Retrieved document has id={document.id}')

    def test_retrieve_document_tagged_not_tagged(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        tag = domain.TAG_PRE_ACCEPTED
        untag = domain.TAG_IMPORTED
        tagged_document_id = 121
        document = ally.document_by(id=tagged_document_id)
        updated = False
        if not document.is_tagged(tag):
            ally.tag(document, tag)
            updated = True
        if document.is_tagged(untag):
            ally.untag(document, untag)
            updated = True
        if updated:
            ally.commit()
            ally.close()
            ally = ba.Catalog(self.catalog_path)

        # Act
        documents = ally.documents_by(tagged_as=tag, untagged_as=untag)

        # Assert
        self.assertIsNotNone(documents, f'Documents without TAG={untag} not retrieved')
        self.assertGreater(len(documents), 0, f'No documents not tagged as {untag} were retrieved')
        for doc in documents:
            self.assertTrue(doc.is_tagged(tag), f'Document {doc} not tagged as {tag}')

    def test_retrieve_all_reasons(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        all_reasons = ally.reasons_by()
        updated = False
        if len(all_reasons) == 0:
            ally.add_reason(description='No access')
            ally.add_reason(description='Off topic')
            ally.add_reason(description='Off topic the cites the topic')
            updated = True
        if updated:
            ally.commit()
            ally.close()
            ally = ba.Catalog(self.catalog_path)

        # Act
        all_reasons = ally.reasons_by()

        # Assert
        self.assertGreater(len(all_reasons), 0, f'No Reasons were retrieved')

    def test_retrieve_one_reason(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        all_reasons = ally.reasons_by()
        updated = False
        if len(all_reasons) == 0:
            ally.add_reason('No access')
            ally.add_reason('Off topic')
            ally.add_reason('Off topic the cites the topic')
            updated = True
        if updated:
            ally.commit()
            ally.close()
            ally = ba.Catalog(self.catalog_path)

        # Act
        description = 'No access'
        all_reasons = ally.reasons_by(description=description)

        # Assert
        self.assertGreater(len(all_reasons), 0, f'No Reasons were retrieved')
        self.assertEqual(len(all_reasons), 1, f'More than one Reasons were retrieved')
        the_reason = all_reasons[0]
        self.assertEqual(the_reason.description, description, f'Unexpected Reason was retrieved: {the_reason}')

    def test_add_document_metadata(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        document_id = 2
        document = ally.document_by(id=document_id)
        if document.review_metadata is not None:
            document.review_metadata = None
            ally.commit()

        # Act
        content = '$$$' + document.review_metadata.content if document.review_metadata is not None else ''
        summary = domain.DocumentMetadata(content=content)
        document.review_metadata = summary
        ally.commit()

        # Assert
        ally.close()
        ally = ba.Catalog(self.catalog_path)
        document = ally.document_by(id=document_id)
        self.assertIsNotNone(document.review_metadata, 'Document summary not retrieved')
        self.assertEqual(content, document.review_metadata.content, 'Summary not as expected')

    def test_remove_document_summary(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        document_id = 4
        document = ally.document_by(id=document_id)
        if document.review_metadata is None:
            document.review_metadata = domain.DocumentMetadata(content='OLD content')
            ally.commit()
            ally.close()
            ally = ba.Catalog(self.catalog_path)
            document = ally.document_by(id=document_id)

        # Act
        document.review_metadata = None
        ally.commit()

        # Assert
        ally.close()
        ally = ba.Catalog(self.catalog_path)
        document = ally.document_by(id=document_id)
        self.assertIsNone(document.review_metadata, 'Document summary still retrieved')

    def test_replace_document_summary(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)
        document_id = 4
        document = ally.document_by(id=document_id)
        if document.review_metadata is None:
            document.review_metadata = domain.DocumentMetadata(content='OLD content')
            ally.commit()
            ally.close()
            ally = ba.Catalog(self.catalog_path)
            document = ally.document_by(id=document_id)

        # Act
        document.review_metadata = None
        ally.commit()
        content = 'NEW content'
        document.review_metadata = domain.DocumentMetadata(content=content)
        ally.commit()

        # Assert
        ally.close()
        ally = ba.Catalog(self.catalog_path)
        document = ally.document_by(id=document_id)
        self.assertIsNotNone(document.review_metadata, 'Document summary not retrieved')
        self.assertEqual(content, document.review_metadata.content, 'Summary not as expected')

    def test_update_document_summary(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path, echo=True)
        document_id = 3
        document = ally.document_by(id=document_id)
        if document.review_metadata is None:
            document.review_metadata = domain.DocumentMetadata(content='Content')
            ally.commit()

        # Act
        content = 'NEW '+document.review_metadata.content
        document.review_metadata.content = content
        ally.commit()

        # Assert
        ally.close()
        ally = ba.Catalog(self.catalog_path)
        document = ally.document_by(id=document_id)
        self.assertIsNotNone(document.review_metadata, 'Document summary not retrieved')
        self.assertEqual(content, document.review_metadata.content, 'Summary not as expected')

    def test_create(self):
        # Arrange
        ally = ba.Catalog()

        # Act
        # Nothing here!

        # Assert
        self.assertFalse(ally.is_open, 'Catalog is open')

    def test_create_and_open(self):
        # Arrange
        ally = None

        # Act
        ally = ba.Catalog(self.catalog_path)

        # Assert
        self.assertTrue(ally.is_open, 'Catalog is not open')

    def test_open(self):
        # Arrange
        ally = ba.Catalog()

        # Act
        ally.open(self.catalog_path)

        # Assert
        self.assertTrue(ally.is_open, 'Catalog is not open')

    def test_close(self):
        # Arrange
        ally = ba.Catalog(self.catalog_path)

        # Act
        ally.close()

        # Assert
        self.assertFalse(ally.is_open, 'Catalog is not closed')
