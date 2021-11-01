# BiblioAlly use cases

## Loading documents by tags

All documents in the **BiblioAlly** Catalog are tagged with one or more labels. Those tags
allow to understand the state of a given document and drive the process building the selected
corpus.

The code for loading documents from the **BiblioAlly** Catalog is below. Documents can be loaded
by the method `document_by()` (loads a single document) or `documents_by()` (loads a collection
of documents).

Those two methods accept specifying tags that the document must have (`tagged_as` parameter),
tags that the document must not have (`untagged_as` parameter) or specific
[attribute values](use_case-loading_by_attributes.md).
```python
non_duplicates = catalog.documents_by(untagged_as=domain.TAG_DUPLICATE)
print(f'found {len(non_duplicates)} non-duplicate documents')

only_imported = catalog.documents_by(tagged_as=domain.TAG_IMPORTED)
print(f'found {len(only_imported)} documents tagged as IMPORTED')

selected_and_pre_selected = catalog.documents_by(tagged_as=[domain.TAG_SELECTED, domain.TAG_PRE_SELECTED])
print(f'found {len(selected_and_pre_selected)} documents SELECTED and PRE-SELECTED')
```

Rejected documents are tagged as `TAG_REJECTED`. The rejection reason is also a tag, so documents
rejected by a specific reason can be loaded by the same pattern, just specifying the
reason.
```python
only_offtopic = catalog.documents_by(tagged_as='Off-topic')
print(f'found {len(only_offtopic)} documents tagged as "Off-topic"')
```
