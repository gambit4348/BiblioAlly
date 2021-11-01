# BiblioAlly use cases

## Loading documents by attributes

Documents in the **BiblioAlly** can be loaded by the method `document_by()` (loads a single document) or
`documents_by()` (loads a collection of documents).

Those two methods accept specifying attribute names and values as parameters. At this moment, only
the equality operator is supported.

The code for loading documents from the **BiblioAlly** Catalog is below.
```python
document = catalog.document_by(id=128)
if document is not None:
    print(f'found {document}')
else:
    print('Document for id=128 not found')

documents = catalog.documents_by(doi='098765.12345')
if len(documents) > 0:
    print(f'found {documents}')
else:
    print('Documents for doi="098765.12345" not found')

document = catalog.document_by(external_key='articleWOW')
if document is not None:
    print(f'found {document}')
else:
    print('Document for external_key="articleWOW" not found')
```
