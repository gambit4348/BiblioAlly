# BiblioAlly use cases

## Importing references into the BiblioAlly Catalog

When a **BiblioAlly** Catalog open, bibliographic references can be imported. Those newly imported
references are the candidates to compose the *selected corpus* of documents, which is, the
documents chosen to be full read and analysed.

The code for importing references into the **BiblioAlly** Catalog is below. The methods must
receive an identifier for the BiBteX dialect being imported and the file name and will
return the amount of records imported, the amount existing in the file and the amount of
documents existing in the Catalog after the import is done.

**BiblioAlly** provides importers for ACM Digital Library, IEEE Xport, Scopus and Web of Science.
```
# Importing translator dependencies
import BiblioAlly.acmdl as acm
import BiblioAlly.ieee as ieee
import BiblioAlly.scopus as scopus
import BiblioAlly.wos as wos

refs_path = base_path + 'Refs\\'

load_count, file_count, base_count = catalog.import_from_file(wos.WebOfScience, refs_path + 'WoS\\refs.bib')
print(f"Web os Science: File={file_count} Load={load_count} Base={base_count}")
load_count, file_count, base_count = catalog.import_from_file(scopus.Scopus, refs_path + 'Scopus\\refs.bib')
print(f"Scopus        : File={file_count} Load={load_count} Base={base_count}")
load_count, file_count, base_count = catalog.import_from_file(acm.AcmDL, refs_path + 'AcmDL\\refs.bib')
print(f"ACM Dig Lib   : File={file_count} Load={load_count} Base={base_count}")
load_count, file_count, base_count = catalog.import_from_file(ieee.IeeeXplore, refs_path + 'IeeeXplore\\refs.bib')
print(f"IEEE Xplore   : File={file_count} Load={load_count} Base={base_count}")
```
All just imported documents are tagged as `TAG_IMPORTED`, except for the one detected as duplicates,
which are tagged as `TAG_DUPLICATE`.