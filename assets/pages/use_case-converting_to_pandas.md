# BiblioAlly use cases

## Converting documents to Pandas DataFrames

it may be useful to have **BiblioAlly** Documents translated to Pandas DataFrames, so it will make the 
meta-analysis easier. For convenience, **BiblioAlly** provides a function named `as_dict()`.

The code for converting documents from the **BiblioAlly** Catalog is below.
```
import pandas as pd


all_documents_dict = cat.as_dict(catalog.documents_by(),
                                 fields=['id', 'title', 'year', 'tags']
                                 tags=lambda tags: [t.tag.name for t in tags])
all_documents_df = pd.DataFrame(all_documents_dict)
```
The `as_dict()` function produces a Python dictionary containing all attributes translated
into lists. The translated attributes are the ones passed as parameter to `fields`. If
no fields are specified, all of them will be translated.

For each translated attribute, a conversion code may be set so the data may be inserted in
the DataFrame as needed. The example shows the attribute `tags` (which is a collection
of `DocumentTag` instances) converted to a list of `Tag` instances by a lambda expression.
