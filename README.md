# Welcome to BiblioAlly

This is the **BiblioAlly** GitHub repository. In order to understand what BiblioAlly is all about start
reading the FAQ below.

## Frequently Asked Questions

### 1. What exactly is BiblioAlly?
BiblioAlly is a Python package containing some classes and functions dedicated to help
people to build scientific literature reviews.

### 2. Is BiblioAlly an application or computer program?
BiblioAlly is a set of classes em functions to be used in Python 3.8+, but it also includes
a GUi module written in PySimpleGui that allows the user to run the literature review with
some Graphic User Interface sugar. However, everything has to be started from a Python script of
a Jupyter Notebook.

### 3. Where is the review data saved?
BiblioAlly builds a SQLite database file and persists all the data in it by using
an Object-Relational mapping provided by SqlAlchemy.

### 4. What are the features exposed by BiblioAlly?
BiblioAlly provides BibTex importers from **Scopus**, **Web of Science**, **ACM Digital Library**
and **IEEEXplore***. By using those importers a standardized database is created. The review is
conducted and the GUI module allows to manager the usually long-term process of
reading and storing metadata from the papers.

### 5. Does BiblioAlly provide metadata analysis?
No, BiblioAlly allows to store a Python dictionary that encodes the metadata extracted
from each paper and later retrieve that metadata to, for instance, feed a
Pandas DataFrame and generate MatPlotLib charts.

### 6. What is the typical use of BiblioAlly?
Install the BiblioAlly package, import it in a Jupyter Notebook, create a
**BiblioAlly Catalog**, import BibTex files, remove duplicates (if any),
perform shallow and deep scrennings bu using the **BiblioAlly Browser**,
register metatada for each of the selected papers, select data from the
Catalog and analyse it.