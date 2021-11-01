# BiblioAlly use cases

## Closing a BiblioAlly Catalog

A **BiblioAlly** Catalog will remain open until the method `close()` is called. After closed, a Catalog
will release all system resources taken, specially the ones related to the SQLite database file.

The code for closing a **BiblioAlly** Catalog is below.
```python
# Until here BiblioAlly is consuming system resources and keeping the SQL database file open

catalog.close()

# From now on BiblioAlly released system resources and the SQLite database file
if catalog.is_open:
    print('The Catalog is open')
else:
    print('The Catalog is NOT open')
```

The message `The Catalog is NOT open` will be printed in the Python console.