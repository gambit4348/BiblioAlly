# BiblioAlly use cases

## Updating documents

Documents in the **BiblioAlly** can be loaded and updated. After all the updates are done,
those changes must be saved to the physical database file by the method `commit()`. 

The code for committing document updates to the **BiblioAlly** Catalog is below.
```
document = catalog.document_by(id=128)
if document.doi is None:
    # for some reason, the BibTeX file didn`t bring the DOI for this document,
    # so we set it ourselves
    document.doi = '098765.123456'
    catalog.commit()
```
