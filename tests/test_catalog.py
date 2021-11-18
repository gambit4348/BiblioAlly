import unittest
from unittest import TestCase
from BiblioAlly import catalog as cat, domain, wos as wos, ieee as ieee, acmdl as acm, scopus as scopus

bibtex_path = 'refs/'


class TestCatalog(TestCase):
    def setUp(self):
        self.catalog_path = 'BiblioAllyTests.db'

    def test_as_dict(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)
        all_documents = ally.documents_by()

        # Act
        all_documents_dict = cat.as_dict(all_documents,
                                         tags=lambda tags: [t.tag.name for t in tags])

        # Assert
        ally.close()
        self.assertIsNotNone(all_documents_dict, 'Document dict not retrieved')

    def test_export_to_acm_dl(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        export_count = ally.export_to_file(acm.AcmDL, bibtex_path + 'exported_acm_dl.bib',
                                           should_export=lambda d: d.is_tagged(cat.TAG_SELECTED))

        # Assert
        self.assertEqual(export_count, 72, 'Unexpected export count')

    def test_export_to_ieee_xplore(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        export_count = ally.export_to_file(ieee.IeeeXplore, bibtex_path + 'exported_ieee_xplore.bib',
                                           should_export=lambda d: d.is_tagged(cat.TAG_SELECTED))

        # Assert
        self.assertEqual(export_count, 72, 'Unexpected export count')

    def test_export_to_scopus(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        export_count = ally.export_to_file(scopus.Scopus, bibtex_path + 'exported_scopus.bib',
                                           should_export=lambda d: d.is_tagged(cat.TAG_SELECTED))

        # Assert
        self.assertEqual(export_count, 72, 'Unexpected export count')

    def test_export_to_web_of_science(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        export_count = ally.export_to_file(wos.WebOfScience, bibtex_path + 'exported_web_of_science.bib',
                                           should_export=lambda d: d.is_tagged(cat.TAG_SELECTED))

        # Assert
        self.assertEqual(export_count, 72, 'Unexpected export count')

    def test_import_refs_from_invalid(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        added_count, file_count, base_count = ally.import_from_file('INVALID', bibtex_path + 'invalid.bib')

        # Assert
        self.assertEqual(file_count, 0, 'Unexpected load count')

    @unittest.skip("skipping ACM DL")
    def test_import_refs_from_acm_dl(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        added_count, file_count, base_count = ally.import_from_file(acm.AcmDL, bibtex_path + 'acm_dl.bib')

        # Assert
        self.assertEqual(202, file_count, 'Unexpected load count')

    @unittest.skip("skipping IEEEXplore")
    def test_import_refs_from_ieee_xplore(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        added_count, file_count, base_count = ally.import_from_file(ieee.IeeeXplore, bibtex_path + 'ieeexplore.bib')

        # Assert
        self.assertEqual(172, file_count, 'Unexpected load count')

    @unittest.skip("skipping Scopus")
    def test_import_refs_from_scopus(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        added_count, file_count, base_count = ally.import_from_file(scopus.Scopus, bibtex_path + 'scopus.bib')

        # Assert
        self.assertEqual(125, file_count, 'Unexpected load count')

    @unittest.skip("skipping Web of Science")
    def test_import_refs_from_web_of_science(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        added_count, file_count, base_count = ally.import_from_file(wos.WebOfScience, bibtex_path + 'web_of_science.bib')

        # Assert
        self.assertEqual(51, file_count, 'Unexpected load count')

    def test_retrieve_document_by_id(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)
        document_id = 1

        # Act
        document = ally.document_by(id=document_id)

        # Assert
        self.assertIsNotNone(document, f'Document with ID={document_id} not retrieved')
        self.assertEqual(document_id, document.id, 'Wrong document retrieved')

    def test_retrieve_document_not_tagged(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)
        tag = cat.TAG_PRE_SELECTED
        untag = cat.TAG_IMPORTED
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
            ally = cat.Catalog(self.catalog_path)

        # Act
        documents = ally.documents_by(untagged_as=untag)

        # Assert
        self.assertIsNotNone(documents, f'Documents without TAG={untag} not retrieved')
        self.assertGreater(len(documents), 0, f'No documents not tagged as {untag} were retrieved')
        for doc in documents:
            self.assertFalse(doc.is_tagged(untag), f'Document {doc} is tagged as {untag}')

    def test_retrieve_document_tagged(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)
        tag = cat.TAG_PRE_SELECTED
        tagged_document_id = 121
        document = ally.document_by(id=tagged_document_id)
        if not document.is_tagged(tag):
            ally.tag(document, tag)
            ally.commit()
            ally.close()
            ally = cat.Catalog(self.catalog_path)

        # Act
        document = ally.document_by(tagged_as=tag, id=tagged_document_id)

        # Assert
        self.assertIsNotNone(document, f'Document with TAG={tag} not retrieved')
        self.assertTrue(document.is_tagged(tag), f'Document not tagged as {tag}')
        self.assertEqual(tagged_document_id, document.id, f'Retrieved document has id={document.id}')

    def test_retrieve_document_tagged_not_tagged(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)
        tag = cat.TAG_PRE_SELECTED
        untag = cat.TAG_IMPORTED
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
            ally = cat.Catalog(self.catalog_path)

        # Act
        documents = ally.documents_by(tagged_as=tag, untagged_as=untag)

        # Assert
        self.assertIsNotNone(documents, f'Documents without TAG={untag} not retrieved')
        self.assertGreater(len(documents), 0, f'No documents not tagged as {untag} were retrieved')
        for doc in documents:
            self.assertTrue(doc.is_tagged(tag), f'Document {doc} not tagged as {tag}')

    def test_add_document_attachment(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)
        document_id = 2
        document = ally.document_by(id=document_id)
        if len(document.attachments) > 0:
            document.attachments = []
            ally.commit()

        # Act
        content = '$$$ Document Attachment $$$'
        summary = domain.DocumentAttachment(name='Test', content=content)
        document.attachments.append(summary)
        ally.commit()

        # Assert
        ally.close()
        ally = cat.Catalog(self.catalog_path)
        document = ally.document_by(id=document_id)
        self.assertEquals(1, len(document.attachments), 'Document attachment not retrieved')
        self.assertEquals('Test', document.attachments[0].name, 'Document attachment name not as expected')
        self.assertEquals(content, document.attachments[0].content, 'Document attachment not as expected')

    def test_remove_document_attachment(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)
        document_id = 4
        document = ally.document_by(id=document_id)
        if len(document.attachments) == 0:
            document.attachments.append(domain.DocumentAttachment(name='Test OLD', content='OLD content'))
            ally.commit()
            ally.close()
            ally = cat.Catalog(self.catalog_path)
            document = ally.document_by(id=document_id)

        # Act
        document.attachments = []
        ally.commit()

        # Assert
        ally.close()
        ally = cat.Catalog(self.catalog_path)
        document = ally.document_by(id=document_id)
        self.assertEquals(0, len(document.attachments), 'Document attachment still retrieved')

    def test_replace_document_attachment(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)
        document_id = 4
        document = ally.document_by(id=document_id)
        if document.attachments == 0:
            document.attachments.append(domain.DocumentAttachment(name='Test OLD', content='OLD content'))
            ally.commit()
            ally.close()
            ally = cat.Catalog(self.catalog_path)
            document = ally.document_by(id=document_id)

        # Act
        document.attachments = []
        ally.commit()
        content = 'NEW content'
        document.attachments.append(domain.DocumentAttachment(name='Test NEW', content=content))
        ally.commit()

        # Assert
        ally.close()
        ally = cat.Catalog(self.catalog_path)
        document = ally.document_by(id=document_id)
        self.assertGreater(len(document.attachments), 0, 'Document attachment not retrieved')
        self.assertEqual('Test NEW', document.attachments[0].name, 'Attachment name not as expected')
        self.assertEqual(content, document.attachments[0].content, 'Attachment content not as expected')

    def test_update_document_attachment(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)
        document_id = 3
        document = ally.document_by(id=document_id)
        if len(document.attachments) == 0:
            document.attachments.append(domain.DocumentAttachment(name='Test OLD', content='OLD Content'))
            ally.commit()

        # Act
        content = 'NEW Content'
        document.attachments[0].content = content
        ally.commit()

        # Assert
        ally.close()
        ally = cat.Catalog(self.catalog_path)
        document = ally.document_by(id=document_id)
        self.assertGreater(len(document.attachments), 0, 'Document attachment not retrieved')
        self.assertEqual(content, document.attachments[0].content, 'Document Attachment not as expected')

    def test_create(self):
        # Arrange
        ally = cat.Catalog()

        # Act
        # Nothing here!

        # Assert
        self.assertFalse(ally.is_open, 'Catalog is open')

    def test_create_and_open(self):
        # Arrange
        ally = None

        # Act
        ally = cat.Catalog(self.catalog_path)

        # Assert
        self.assertTrue(ally.is_open, 'Catalog is not open')

    def test_open(self):
        # Arrange
        ally = cat.Catalog()

        # Act
        ally.open(self.catalog_path)

        # Assert
        self.assertTrue(ally.is_open, 'Catalog is not open')

    def test_close(self):
        # Arrange
        ally = cat.Catalog(self.catalog_path)

        # Act
        ally.close()

        # Assert
        self.assertFalse(ally.is_open, 'Catalog is not closed')
