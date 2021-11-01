# BiblioAlly use cases

## Creating a new BiblioAlly Catalog

A **BiblioAlly** Catalog is a [SQLite](https://en.wikipedia.org/wiki/SQLite) database file containing a data schema
devoted to store all **BiblioAlly** data. It is created then the catalog is loaded by the first time. Because of the
work for creating all the tables and indexes, the very first access may last longer than the next ones.

The code for creating and loading the **BiblioAlly** Catalog is below. The last line instantiates the
Catalog and returns it. At this moment, the SQLite database file named `MyReview.db` will be created
if necessary and the data schema all prepared.
```python
# Importing dependencies
from BiblioAlly import gui
from BiblioAlly import catalog as cat


# Instantiating the Catalog
catalog_path = ".\\My review\\"
catalog_file = catalog_path + 'MyReview.db'
catalog = cat.Catalog(catalog_file)
```
