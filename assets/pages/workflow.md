# BiblioAlly workflow

**BiblioAlly** offers some features that help the author when conducting a Literature Review.
A usual protocol is presented below. It's not the exact research protocol and such a workflow does
not intents to establish any methodological path. It is just a way of using **BiblioAlly** in order to
take the best of it and to present what are the features currently covered.

![The typical BiblioAlly Workflow](..\assets\images\BiblioAlly-workflow.jpg "BiblioAlly typical workflow")
The typical **BiblioAlly** Workflow.

The blue line at the bottom represents the time and the numbered blue circles are the major milestones of the project.
The gray icons represent the activities not supported by **BiblioAlly**. The color icons represent
activities that **BiblioAlly** somehow support.

1. **Research design**: is the phase of establishing goals and limitations of the research and the strategies
that will be used to accomplish those goals; for instance, this is where the
[PICO strategy](https://en.wikipedia.org/wiki/PICO_process) is used to create the search expressions;
2. **Reference search** : is the phase of searching and retrieving bibliographical references that are candidates
to compose the selected corpus, the set of articles, books, chapters and other scientific documents that will be
analysed; at this moment **BiblioAlly** is not able to issue the search expressions against the scientific databases
but it is capable of importing [BibTeX](https://en.wikipedia.org/wiki/BibTeX) references from
[ACM Digital Library](https://en.wikipedia.org/wiki/Association_for_Computing_Machinery#Portal_and_Digital_Library),
[IEEE Xplore](https://en.wikipedia.org/wiki/IEEE_Xplore), [Scopus](https://en.wikipedia.org/wiki/Scopus),
and [Web of Science](https://en.wikipedia.org/wiki/Web_of_Science) and store them in an integrated database
named the **BiblioAlly** Catalog; non-supported BibTeX *dialects* may be added by writing a translator Python class;
3. **Shallow screening**: is the phase of reading summaries of the retrieved references (usually the title, keywords
and abstract) and deciding if the document seem to meet the selection criteria established in
phase 1; **BiblioAlly** provides a GUI-based browser that makes it easier to navigate along the
retrieved references and deciding which ones should be rejected and which ones have potential to
be part of the selected corpus; the Catalog records the decision for further report;
4. **Documents retrieval**: is the phase of going after and downloading the full text of the candidate
references;
5. **Deep screening**: is the most time and energy-consuming phase, when the candidate documents are
full read; again the GUI-based browser helps by listing the candidates, presenting a
chart that conveys how much work is still to be done and registering which of the documents
should be kept for the final corpus; during the full-text reading, the meta-data may be extracted
and recorded in the Catalog to be further consumed by the meta-analysis;
6. **Analysing and writing**: is the phase when the author works to generate the meta-analysis and to
write the research report; **BiblioAlly** does not produce any analysis from the meta-data stored
during the previous phase, but allows to retrieve them to be used in Python scripts.

Naturally, different research goals and restrictions may determine other phases, producing a process
even more complex. For instance, research based on the [PRISMA](https://en.wikipedia.org/wiki/Preferred_Reporting_Items_for_Systematic_Reviews_and_Meta-Analyses)
methodology may require a pair review that is not natively supported by **BiblioAlly** at this moment.

The previous workflow allows to have a notion of what **BiblioAlly** has to offer as aid for
Literature Reviews and what are some gaps in its features.
