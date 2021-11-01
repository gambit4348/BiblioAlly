# BiblioAlly use cases

## Invoking the Catalog Browser

For convenience, **BiblioAlly** provides a [GUI-based interface](browser.md).

The code for instantiating and invoking the **BiblioAlly** Catalog Browser is below. The last two lines
show 1. Instantiating the Browser and passing the catalog it will work on; and 2. Showing the
Browser main window.
```
catalog = cat.Catalog(catalog_file)

# Invoking the Browser
browser = gui.Browser(catalog)
browser.show()
```

Besides the main window, the Browser shows a pop-up dialog to let the user add a new rejection
reason and anoather is showed to allow the user choosing the reasons to filter the documents.