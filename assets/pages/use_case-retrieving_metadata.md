# BiblioAlly use cases

## Retrieving document metadata

Some Literature Reviews may include a [meta-analysis](https://en.wikipedia.org/wiki/Meta-analysis). The **BiblioAlly**
Catalog can store those data in the form of Document Attachments. A Document can have many named
Attachments and one or more of them may be used to store the meta-data extracted from studies.

The **BiblioAlly** Catalog Browser features a simple interface that allows the user to add metatada
to a Document. That metadata is stored as an attachment named as "Metadata" (the content type for it
is the [mime type](https://en.wikipedia.org/wiki/Media_type) "text/x-python").

The code for metadata for the selected documents from the **BiblioAlly** Catalog is below. The metadata
follows the convention to be a piece of Python code, usually a dictionary.
```
selected_corpus = base.documents_by(tagged_as=cat.TAG_SELECTED)
metadata = [eval(d.attachment_by_name('Metadata').content) for d in selected_corpus]
```
The `metadata` variable is a collection of Python objects translated from the textual representation
stored in the `content` attribute.
