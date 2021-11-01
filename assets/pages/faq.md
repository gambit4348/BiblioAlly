# Frequently Asked Questions

## 1. What exactly is BiblioAlly?
BiblioAlly is a Python package containing some classes and functions dedicated to help
people to build scientific literature reviews.

## 2. What is the biggest advantage of using BiblioAlly?
The biggest advantage of using BiblioAlly is having a database that records all bibliographic references
collected during the literature review and their different states during the process. Also, it records the
meta-data extracted from the selected articles and make them available for a meta-analysis based on
Python packages, like [Pandas](https://en.wikipedia.org/wiki/Pandas_(software)) and
[MatPlotLib](https://en.wikipedia.org/wiki/Matplotlib).

## 3. Is BiblioAlly an application or computer program?
BiblioAlly is a set of classes and functions to be used in Python 3.8+, but it also includes
a GUI module written in PySimpleGui that allows the user to run the literature review with
some Graphic User Interface sugar. However, everything has to be started from a Python script,
for instance, in a Jupyter Notebook.

## 4. Where is the review data saved?
BiblioAlly builds a SQLite database file and persists all the data in it by using
an Object-Relational mapping provided by SqlAlchemy.

## 5. What are the features exposed by BiblioAlly?
BiblioAlly provides BibTex importers for **Scopus**, **Web of Science**, **ACM Digital Library**
and **IEEEXplore**. By using those importers a standardized database is created. The review is
conducted and the GUI module allows to manage the usually long-term process of
reading and storing metadata from the papers.

## 6. Does BiblioAlly provide metadata analysis?
No, BiblioAlly allows to store a Python dictionary that encodes the metadata extracted
from each paper and later retrieve that metadata to, for instance, feed a
Pandas DataFrame and generate MatPlotLib charts.

## 7. What is the typical use of BiblioAlly?
1. Install the BiblioAlly package
   1. `pip install BiblioALly`
   2. `conda install BiblioAlly`
2. Import it in a Jupyter Notebook
   1. `from BiblioAlly import catalog as ally`
3. Create a **BiblioAlly Catalog** (where all data will be stored)
   1. `catalog = ally.Catalog("my_review.db")`
4. Import BibTex files into the Catalog
   1. `from BiblioAlly import wos    # Web of Science`
   2. `from BiblioAlly import scopus`
   3. `from BiblioAlly import ieee   # IEEE Xplore`
   4. `from BiblioAlly import acmdl  # ACM Digital Library`
   5. `refs_count, load_count, base_cout = catalog.import_from_file(wos.WebOfSciece, "wos.bib")`
5. Remove duplicates,if any (BiblioAlly will try to remove them automatically, but some can escape the process)
6. Perform shallow and deep screenings by using the **BiblioAlly Browser**
   1. `from BiblioAlly import gui`
   2. `browser = Browser(catalog)`
   3. `browser.show()`
7. Register metadata for each of the selected papers
   1. `catalog.add_summary(metadata_dict)`
8. select data from the Catalog and analyse it.
   1. `from BiblioAlly import domain`
   2. `import pandas as pd`
   3. `documents = catalog.documents_by(tagged_as=domain.TAG_ACCEPTED)`
   4. `documents_dict = ally.as_dict(documents)`
   5. `documents_df = pd.DataFrame(documents_dict)`

## 8. Is BiblioAlly finnished?
Far from it! There's a number of improvements BiblioAlly may receive to become more useful
and to allow better and deeper analysis for literature reviews. A few ones that come to mind are:
1. Calculating Bibliometric indicators
2. Text mining
3. Word clouds generation
4. Automatic content classification
5. Automatic generation of mind maps
6. Automatic generation of ontologies
7. Automatic metadata extraction
8. Qualitative analysis capabilities
9. Semantic similarity detection
10. Operation logging
11. Collaboration capabilities
12. Research protocol
13. Process tracking improvements
14. Automatic full text retrieval
15. And so on...