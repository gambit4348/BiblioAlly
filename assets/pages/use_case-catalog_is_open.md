# BiblioAlly use cases

## Testing if a Catalog is open

After a **BiblioAlly** Catalog is created or loaded, is will report as *is open* until the method
[`close()`](use_case-close.md) is called.
While the Catalog is open, operations can be issued on the domain objects maintained by the
Catalog. This consumes memory resources that will be returned to the system only when the Catalog is closed. 

The code for testing the state of a **BiblioAlly** Catalog is below
```
# Instantiating the Catalog
catalog_path = ".\\My review\\"
catalog_file = catalog_path + 'MyReview.db'
catalog = cat.Catalog(catalog_file)

if catalog.is_open:
    print('The Catalog is open')
else:
    print('The Catalog is NOT open')
```

The message `The Catalog is open` will be printed in the Python console.