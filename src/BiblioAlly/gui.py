"""
Declares and exports the Browser class that is a GUI based support tool for operating on a BiblioAlly Catalog.
"""

import datetime
import PySimpleGUI as sg
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PySimpleGUI import LISTBOX_SELECT_MODE_MULTIPLE
from . import catalog as cat
from . import domain

BUTTON_EXIT = '-EXIT-'

BUTTON_EDIT_DOC_METADATA = '-BUTTON-EDIT-DOC-METADATA-'
BUTTON_DOC_PRESELECT = '-DOC-PRESELECT-'
COL_OPERATIONS = '-COL-OPERATIONS-'
LABEL_DOC_METADATA = '-LABEL-DOC-METADATA-'
LABEL_DOC_REJECT = '-LABEL-DOC-REJECT-'
LIST_DOC_REJECT = '-DOC-REJECT-'
BUTTON_DOC_RESET = '-DOC-RESET-'
BUTTON_DOC_SELECT = '-DOC-SELECT-'

BUTTON_TAG_DUPLICATE = '-TAG-DUPLICATE-'
BUTTON_TAG_IMPORTED = '-TAG-IMPORTED-'
BUTTON_TAG_PRE_SELECTED = '-TAG-PRE-SELECTED-'
BUTTON_TAG_REJECTED = '-TAG-REJECTED-'
BUTTON_TAG_SELECTED = '-TAG-SELECTED-'

BUTTON_TAG_FILTERS = '-TAG-FILTERS-'

CANVAS_DOCUMENTS = '-TABLE-DOCUMENTS-'
TABLE_DOCUMENTS = '-CANVAS-DOCUMENTS-'
FIELD_ABSTRACT = '-DOC-ABSTRACT-'
FIELD_AUTHORS = '-DOC-AUTHORS-'
FIELD_DOCUMENT_TYPE = '-DOC-DOCUMENT-TYPE-'
FIELD_DOI = '-DOC-DOI-'
FIELD_EXTERNAL_KEY = '-DOC-EXTERNAL-KEY-'
FIELD_KEYWORDS = '-DOC-KEYWORDS-'
FIELD_KIND = '-DOC-KIND-'
FIELD_METADATA = '-DOC-METADATA-'
FIELD_ORIGIN = '-DOC-ORIGIN-'
FIELD_TAGS = '-DOC-TAGS-'
FIELD_TITLE = '-DOC-TITLE-'
FIELD_YEAR = '-DOC-YEAR-'

tag_for_button = {
    BUTTON_TAG_SELECTED: domain.TAG_ACCEPTED,
    BUTTON_TAG_DUPLICATE: domain.TAG_DUPLICATE,
    BUTTON_TAG_REJECTED: domain.TAG_EXCLUDED,
    BUTTON_TAG_IMPORTED: domain.TAG_IMPORTED,
    BUTTON_TAG_PRE_SELECTED: domain.TAG_PRE_ACCEPTED
}
label_for_button = {
    BUTTON_TAG_SELECTED: 'Selected',
    BUTTON_TAG_DUPLICATE: 'Duplicate',
    BUTTON_TAG_REJECTED: 'Rejected',
    BUTTON_TAG_IMPORTED: 'Imported',
    BUTTON_TAG_PRE_SELECTED: 'Pre-selected'
}
filter_buttons = [
    BUTTON_TAG_SELECTED,
    BUTTON_TAG_DUPLICATE,
    BUTTON_TAG_REJECTED,
    BUTTON_TAG_IMPORTED,
    BUTTON_TAG_PRE_SELECTED
]

metadata_font = ('Courier New', 8, '')
metadata_font_edit = ('Courier New', 9, '')
label_font = ('Arial', 10, '')
text_font = ('Arial', 10, 'bold')
text_color = '#CA8410'
button_base_font = 'Arial 10'

duplicate_color = ('#ECFFFF', '#FAB420')
reject_color = ('#ECFFFF', '#E94763')
import_color = ('#ECFFFF', '#626ED4')
preselect_color = ('#ECFFFF', '#37A4F6')
select_color = ('#ECFFFF', '#03A399')
input_color = '#DFDFDF'

background_color = '#D8D8DF'

# Add your new theme colors and settings
sg.LOOK_AND_FEEL_TABLE['BiblioAllyTheme'] = {
    'BACKGROUND': background_color,
    'TEXT': '#737A97',
    'INPUT': input_color,
    'TEXT_INPUT': '#636A87',
    'SCROLL': '#737A97',
    'BUTTON': ('#F0F0F0', '#626ED4'),
    'PROGRESS': ('#D1826B', '#CC8019'),
    'BORDER': 1,
    'SLIDER_DEPTH': 0,
    'PROGRESS_DEPTH': 0,
}
sg.theme('BiblioAllyTheme')
table_alternate_color = '#626ED4'
table_background_color = input_color


class Browser:
    """
    Provides a convenient yet limited visual support for handling the BiblioAlly catalog.

    To invoke the browser just call the method show().
    """

    def __init__(self, catalog: cat.Catalog):
        """
        Initializes the instance with the catalog that will be handled.

        Parameters:
             catalog: the BiblioAlly catalog that will be handled.
        """

        self._catalog = catalog
        self._doc_fields = ['year', 'title', 'authors', 'kind', 'generator', 'tags']
        self._reject_reasons = []
        self._all_documents = []
        self._visible_documents = []
        self._active_tags = [
            domain.TAG_ACCEPTED, domain.TAG_DUPLICATE, domain.TAG_EXCLUDED, domain.TAG_IMPORTED, domain.TAG_PRE_ACCEPTED
        ]
        self._additional_tags = []
        self._selected_document = None
        self._window = None
        self._fig = None
        self._ax = None
        self._figure_canvas = None


    def show(self):
        """
        Sets up the catalog Browser and shows it.

        Example:
            from BiblioAlly import catalog as ally
            from BiblioAlly import gui

            catalog = ally.Catalog("my_research.db")
            browser = gui.Browser(catalog)

            browser.show()
        """

        self._fig = plt.figure.Figure(figsize=(6.5, 6.5), dpi=75, facecolor=background_color)
        self._ax = self._fig.add_subplot(111)

        self._load_documents()
        self._filter_documents()

        self._window = self._main_window().Finalize()
        self._window.maximize()
        self._update_table()
        self._update_reject_reasons()
        self._update_mini_dashboard()
        self._select_document_by_index(0)
        self._window[TABLE_DOCUMENTS].expand(True, True)
        self._window[COL_OPERATIONS].expand(True, True)
        self._window[FIELD_METADATA].expand(True, True)
        self._window[FIELD_METADATA].update(visible=False)
        self._window[LIST_DOC_REJECT].expand(True, True)
        self._window[LIST_DOC_REJECT].update(visible=False)

        row_index = -1
        while True:
            event, values = self._window.read()
            if event == sg.WINDOW_CLOSED or event == BUTTON_EXIT:
                break
            if event == TABLE_DOCUMENTS and values[TABLE_DOCUMENTS]:
                row_index = values[TABLE_DOCUMENTS][0]
                self._select_document_by_index(row_index)
            elif event == BUTTON_TAG_FILTERS:
                if self._handle_filters():
                    self._filter_documents()
                    self._update_table()
                    self._select_document_by_index(0)
            elif event in filter_buttons:
                self._toggle_filter_button(event)
                self._filter_documents()
                self._update_table()
                self._select_document_by_index(0)
            elif event == LIST_DOC_REJECT:
                self._handle_reject(values[LIST_DOC_REJECT], row_index)
            elif event == BUTTON_EDIT_DOC_METADATA:
                self._edit_metadata()
            elif self._selected_document is not None:
                if event == BUTTON_DOC_PRESELECT:
                    self.pre_select_document(self._selected_document)
                    self._filter_documents()
                    self._update_mini_dashboard()
                    self._update_table(row_index)
                    self._select_document_by_index(row_index)
                elif event == BUTTON_DOC_SELECT:
                    self.select_document(self._selected_document)
                    self._filter_documents()
                    self._update_mini_dashboard()
                    self._update_table(row_index)
                    self._select_document_by_index(row_index)
                elif event == BUTTON_DOC_RESET:
                    self.reset_document(self._selected_document)
                    self._filter_documents()
                    self._update_mini_dashboard()
                    self._update_table(row_index)
                    self._select_document_by_index(row_index)
        self._window.close()
        self._window = None

    def author_names(self, authors):
        return '; '.join([au.author.short_name for au in authors])

    def keyword_names(self, keywords):
        return '; '.join([kw.name for kw in keywords])

    def pre_select_document(self, document: domain.Document):
        self._catalog.tag(document, domain.TAG_PRE_ACCEPTED)
        self._catalog.untag(document, domain.TAG_IMPORTED)
        document.reason = None
        self._catalog.commit()

    def reject_document(self, document: domain.Document, reason_tags):
        if type(reason_tags) is not list:
            reason_tags = [reason_tags]
        document.untag(domain.TAG_IMPORTED)
        self._catalog.tag(document, [domain.TAG_EXCLUDED] + reason_tags)
        self._catalog.commit()
        return [document_tag.tag for document_tag in document.tags]

    def select_document(self, document: domain.Document):
        self._catalog.tag(document, domain.TAG_ACCEPTED)
        self._catalog.untag(document, domain.TAG_PRE_ACCEPTED)
        document.reason = None
        self._catalog.commit()

    def reset_document(self, document: domain.Document):
        self._catalog.untag(document, [document_tag.tag for document_tag in document.tags])
        self._catalog.tag(document, domain.TAG_IMPORTED)
        document.reason = None
        self._catalog.commit()

    def _document_is_in_filter(self, document: domain.Document, active_tags):
        document_tags = [document_tag.tag.name for document_tag in document.tags]
        same_tags = list(filter(lambda tag: tag in active_tags, document_tags))
        in_filter = len(same_tags) > 0
        if len(self._additional_tags) > 0:
            same_tags = list(filter(lambda tag: tag in self._additional_tags, document_tags))
            in_filter = in_filter and len(same_tags) > 0
        return in_filter

    def _document_tuples(self, documents):
        tuples = cat.as_tuple(documents, fields=self._doc_fields, authors=self.author_names,
                              tags=lambda value: ' '.join([f'[{dt.tag.name}]' for dt in value]))
        return tuples

    def _edit_metadata(self):
        if self._selected_document is None:
            return

        BUTTON_METADATA_CANCEL = '-EDIT-METADATA-CANCEL-'
        BUTTON_METADATA_CONFIRM = '-EDIT-METADATA-CONFIRM-'
        METADATA_CONTENT = '-EDIT-METADATA-CONTENT-'
        METADATA_DOC_AUTHORS = '-EDIT-METADATA-AUTHORS-'
        METADATA_DOC_DOI = '-EDIT-METADATA-DOI-'
        METADATA_DOC_EXTERNAL_KEY = '-EDIT-METADATA-EXTERNAL-KEY-'
        METADATA_DOC_ID = '-EDIT-METADATA-ID-'
        METADATA_DOC_TITLE = '-EDIT-METADATA-TITLE-'
        METADATA_DOC_YEAR = '-EDIT-METADATA-YEAR-'
        edit_metadata_layout = [
            [
                sg.Text('ID:', font=label_font),
                sg.Input('', key=METADATA_DOC_ID, size=(5, 1), readonly=True),
                sg.Text('Year:', font=label_font),
                sg.Input('', key=METADATA_DOC_YEAR, size=(4, 1), readonly=True),
                sg.Text('Title:', font=label_font),
                sg.Input('', key=METADATA_DOC_TITLE, size=(130, 1), readonly=True),
            ],
            [
                sg.Text('Authors:', font=label_font),
                sg.Input('', key=METADATA_DOC_AUTHORS, size=(60, 1), readonly=True),
                sg.Text('DOI:', font=label_font),
                sg.Input('', key=METADATA_DOC_DOI, size=(35, 1), readonly=True),
                sg.Text('External key:', font=label_font),
                sg.Input('', key=METADATA_DOC_EXTERNAL_KEY, size=(25, 1), readonly=True),
            ],
            [
                sg.Multiline(default_text='', key=METADATA_CONTENT, size=(160, 40), font=metadata_font_edit,
                             autoscroll=True)
            ],
            [
                sg.Button('Cancel', key=BUTTON_METADATA_CANCEL),
                sg.Button('Confirm', key=BUTTON_METADATA_CONFIRM)
            ]
        ]

        doc = self._selected_document
        window = sg.Window('Edit Metadata', edit_metadata_layout, resizable=True, element_padding=1).finalize()
        window[METADATA_DOC_AUTHORS].update(self.author_names(doc.authors))
        window[METADATA_DOC_DOI].update(doc.doi)
        window[METADATA_DOC_EXTERNAL_KEY].update(doc.external_key)
        window[METADATA_DOC_ID].update(doc.id)
        window[METADATA_DOC_TITLE].update(doc.title)
        window[METADATA_DOC_YEAR].update(doc.year)
        window[METADATA_CONTENT].expand(True, True)

        if doc.review_metadata is not None:
            window[METADATA_CONTENT].update(doc.review_metadata.content)
        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == BUTTON_METADATA_CANCEL:
                break
            elif event == BUTTON_METADATA_CONFIRM:
                content = values[METADATA_CONTENT]
                if doc.review_metadata is not None:
                    doc.review_metadata.content = content
                    doc.review_metadata.import_date = datetime.date.today()
                else:
                    doc.review_metadata = domain.DocumentMetadata(content)
                self._catalog.commit()
                self._window[FIELD_METADATA].update(content)
                break
        window.close()

    def _handle_filters(self):
        filter_tags = [tag.name for tag in self._reject_reasons]
        LIST_ADDITIONAL_TAGS = '-LIST-FILTER-TAGS-'
        BUTTON_CANCEL = '-BUTTON-FILTER-CANCEL-'
        BUTTON_CONFIRM = '-BUTTON-FILTER-CONFIRM-'
        panel_layout = [
            [
                sg.Listbox(filter_tags, default_values=self._additional_tags, key=LIST_ADDITIONAL_TAGS,
                           size=(94, 24), select_mode=LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                           expand_x=True, expand_y=True),
            ],
            [
                sg.Button('Cancel', key=BUTTON_CANCEL),
                sg.Button('Confirm', key=BUTTON_CONFIRM)
            ]
        ]
        filter_changed = False
        window = sg.Window('Aditional Filters', panel_layout, resizable=True, element_padding=1, modal=True)
        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == BUTTON_CANCEL:
                break
            elif event == BUTTON_CONFIRM:
                filter_changed = True
                self._additional_tags = values[LIST_ADDITIONAL_TAGS]
                break
        window.close()
        return filter_changed

    def _handle_reject(self, selected_items, document_row_index):
        if document_row_index < 0:
            return
        selected_tags = list(filter(lambda tag: tag.name in selected_items, self._reject_reasons))
        if len(selected_tags) == 0:
            new_reason_text = sg.popup_get_text('Enter your new rejection reason:')
            if new_reason_text is not None:
                self.reject_document(self._selected_document, new_reason_text)
                self._update_reject_reasons()
        else:
            self.reject_document(self._selected_document, selected_tags)
        self._filter_documents()
        self._update_table(document_row_index)
        self._update_mini_dashboard()
        self._select_document_by_index(document_row_index)

    def _main_window(self):
        doc_headings = ['Year', 'Title', 'Authors', 'Origin']
        doc_widths = [4, 95, 45, 10]

        main_layout = [
            [
                sg.Column([
                    [
                        sg.Button('Imported ON', key=BUTTON_TAG_IMPORTED, button_color=import_color),
                        sg.Button('Duplicate ON', key=BUTTON_TAG_DUPLICATE, button_color=duplicate_color),
                        sg.Button('Rejected ON', key=BUTTON_TAG_REJECTED, button_color=reject_color),
                        sg.Button('Pre-selected ON', key=BUTTON_TAG_PRE_SELECTED, button_color=preselect_color),
                        sg.Button('Selected ON', key=BUTTON_TAG_SELECTED, button_color=select_color),
                    ]
                ], element_justification='left', expand_x=True),
                sg.Column([
                    [
                        sg.Button('Rejection filters...', key=BUTTON_TAG_FILTERS),
                    ]
                ], element_justification='left', expand_x=True),
                sg.Column([
                    [
                        sg.Button('Exit!', key=BUTTON_EXIT)
                    ],
                ], element_justification='right')

            ],
            [
                sg.Table([], key=TABLE_DOCUMENTS, enable_events=True, headings=doc_headings,
                         alternating_row_color=table_background_color,
                         auto_size_columns=False, col_widths=doc_widths, justification='left',
                         visible_column_map=[h[0] != '~' for h in doc_headings], num_rows=20),
                sg.Canvas(key=CANVAS_DOCUMENTS)
            ],
            [
                sg.Text(text='', key=FIELD_TAGS, size=(200, 1), font=text_font, text_color=text_color,
                        background_color=input_color, expand_x=True),
            ],
            [
                sg.Column([
                    [
                        sg.Text('Year:', font=label_font),
                        sg.Text(text='', key=FIELD_YEAR, size=(4, 1), font=text_font, text_color=text_color,
                                background_color=input_color),
                        sg.Text('Title:', font=label_font),
                        sg.Text(text='', key=FIELD_TITLE, size=(114, 1), font=text_font, text_color=text_color,
                                background_color=input_color, expand_x=True),
                    ],
                    [
                        sg.Text('Authors:', font=label_font),
                        sg.Text(text='', key=FIELD_AUTHORS, size=(121, 1), font=text_font, text_color=text_color,
                                background_color=input_color, expand_x=True),
                    ],
                    [
                        sg.Text('Kind:', font=label_font),
                        sg.Text(text='', key=FIELD_KIND, size=(20, 1), font=text_font, text_color=text_color,
                                background_color=input_color),
                        sg.Text('DOI:', font=label_font),
                        sg.Text(text='', key=FIELD_DOI, size=(30, 1), font=text_font, text_color=text_color,
                                background_color=input_color),
                    ],
                    [
                        sg.Text('Origin:', font=label_font),
                        sg.Text(text='', key=FIELD_ORIGIN, size=(20, 1), font=text_font, text_color=text_color,
                                background_color=input_color),
                        sg.Text('Document type:', font=label_font),
                        sg.Text(text='', key=FIELD_DOCUMENT_TYPE, size=(20, 1), font=text_font, text_color=text_color,
                                background_color=input_color),
                        sg.Text('External key:', font=label_font),
                        sg.Text(text='', key=FIELD_EXTERNAL_KEY, size=(20, 1), font=text_font, text_color=text_color,
                                background_color=input_color),
                    ],
                    [
                        sg.Column([
                            [sg.Text('Abstract', font=label_font)],
                            [sg.Multiline(key=FIELD_ABSTRACT, default_text='', size=(100, 20), disabled=True,
                                          autoscroll=True, expand_x=True, expand_y=True)]
                        ], expand_x=True, expand_y=True),
                        sg.Column([
                            [sg.Text('Keywords', font=label_font)],
                            [sg.Multiline(key=FIELD_KEYWORDS, default_text='', size=(40, 20), disabled=True,
                                          autoscroll=True, expand_y=True)]
                        ], expand_y=True),
                    ]
                ], expand_x=True, expand_y=True),
                sg.VSeparator(),
                sg.Column([
                    [
                        sg.Button('Pre-Select!', key=BUTTON_DOC_PRESELECT, button_color=preselect_color),
                        sg.Button('Select!', key=BUTTON_DOC_SELECT, button_color=select_color),
                        sg.Button('Reset!', key=BUTTON_DOC_RESET, button_color=import_color),
                    ],
                    [
                        sg.Text('Reject reason', key=LABEL_DOC_REJECT, visible=False),
                        sg.Text('Metadata', key=LABEL_DOC_METADATA, visible=False)
                    ],
                    [
                        sg.Listbox([], key=LIST_DOC_REJECT, size=(94, 24), enable_events=True, visible=False,
                                   expand_x=True, expand_y=True),
                        sg.Multiline(default_text='', key=FIELD_METADATA, size=(94, 24), font=metadata_font,
                                     disabled=True, visible=False, autoscroll=True, expand_x=True, expand_y=True)
                    ],
                    [
                        sg.Button('Edit metadata', key=BUTTON_EDIT_DOC_METADATA, visible=False)
                    ]
                ], key=COL_OPERATIONS, expand_x=True, expand_y=True),
            ],
        ]
        window = sg.Window('BiblioAlly', main_layout, resizable=True, element_padding=1)
        return window

    def _filter_documents(self):
        self._visible_documents = [document for document in self._all_documents
                                   if self._document_is_in_filter(document, self._active_tags)]

    def _load_documents(self):
        self._all_documents = self._catalog.documents_by()
        self._all_documents.sort(key=lambda doc: (doc.year, doc.title))

    def _select_document_by_index(self, index):
        if index >= len(self._visible_documents):
            self._selected_document = None
        else:
            self._selected_document = self._visible_documents[index]
        self._update_document_details(self._selected_document)

    def _toggle_filter_button(self, button):
        button_label = label_for_button[button]
        button_tag = tag_for_button[button]
        if button_tag in self._active_tags:
            self._active_tags.remove(button_tag)
            button_label += ' OFF'
        else:
            self._active_tags.append(button_tag)
            button_label += ' ON'
        self._window[button].update(text=button_label)

    def _update_document_details(self, document: domain.Document):
        if document is None:
            self._window[FIELD_ABSTRACT].update('')
            self._window[FIELD_AUTHORS].update('')
            self._window[FIELD_DOCUMENT_TYPE].update('')
            self._window[FIELD_DOI].update('')
            self._window[FIELD_EXTERNAL_KEY].update('')
            self._window[FIELD_KEYWORDS].update('')
            self._window[FIELD_KIND].update('')
            self._window[FIELD_METADATA].update('')
            self._window[FIELD_ORIGIN].update('')
            self._window[FIELD_TAGS].update('')
            self._window[FIELD_TITLE].update('')
            self._window[FIELD_YEAR].update('')
            self._window[BUTTON_DOC_PRESELECT].update(disabled=True)
            self._window[BUTTON_DOC_SELECT].update(disabled=True)
            self._window[BUTTON_DOC_RESET].update(disabled=True)
            self._window[LABEL_DOC_REJECT].update(visible=False)
            self._window[LIST_DOC_REJECT].update(visible=False)
            return
        self._window[FIELD_ABSTRACT].update(document.abstract)
        self._window[FIELD_AUTHORS].update(self.author_names(document.authors))
        self._window[FIELD_DOCUMENT_TYPE].update(document.document_type)
        self._window[FIELD_DOI].update(document.doi)
        self._window[FIELD_EXTERNAL_KEY].update(document.external_key)
        self._window[FIELD_KEYWORDS].update(self.keyword_names(document.keywords))
        self._window[FIELD_KIND].update(document.kind)
        self._window[FIELD_METADATA].update(document.review_metadata.content
                                          if document.review_metadata is not None else '')
        self._window[FIELD_ORIGIN].update(document.generator)
        self._window[FIELD_TAGS].update(' '.join([f'[{document_tag.tag.name}]' for document_tag in document.tags]))
        self._window[FIELD_TITLE].update(document.title)
        self._window[FIELD_YEAR].update(document.year)
        self._window[BUTTON_DOC_PRESELECT].update(disabled=document.is_tagged(domain.TAG_PRE_ACCEPTED))
        self._window[BUTTON_DOC_SELECT].update(disabled=not document.is_tagged(domain.TAG_PRE_ACCEPTED))
        element_visible = document.is_tagged(domain.TAG_IMPORTED) or document.is_tagged(domain.TAG_PRE_ACCEPTED)
        self._window[LABEL_DOC_REJECT].update(visible=element_visible)
        self._window[LIST_DOC_REJECT].update(visible=element_visible)
        element_visible = document.is_tagged(domain.TAG_ACCEPTED)
        self._window[LABEL_DOC_METADATA].update(visible=element_visible)
        self._window[FIELD_METADATA].update(visible=element_visible)
        self._window[BUTTON_EDIT_DOC_METADATA].update(visible=element_visible)

    def _update_mini_dashboard(self):
        doc_tags = dict()
        for doc in self._all_documents:
            for tag in self._catalog.system_tags:
                if tag in doc_tags:
                    doc_tags[tag] += 1 if tag in [dt.tag for dt in doc.tags] else 0
                else:
                    doc_tags[tag] = 1
        sort_order = [domain.TAG_PRE_ACCEPTED, domain.TAG_DUPLICATE, domain.TAG_ACCEPTED, domain.TAG_EXCLUDED,
                      domain.TAG_IMPORTED]
        colors = [preselect_color[1], duplicate_color[1], select_color[1], reject_color[1], import_color[1]]
        doc_tags = sorted(list(doc_tags.items()), key=lambda dt: sort_order.index(dt[0].name))
        labels = [t[0].name.capitalize() for t in doc_tags]
        sizes = [t[1] for t in doc_tags]

        self._ax.clear()
        self._ax.pie(sizes, labels=labels, colors=colors, wedgeprops=dict(width=0.5), startangle=-40,
                     autopct=lambda p: f'{p:.2f}%\n({p*sum(sizes)/100 :.0f})',
                     pctdistance=0.85)
        canvas = self._window[CANVAS_DOCUMENTS].TKCanvas
        if self._figure_canvas is None:
            self._figure_canvas = FigureCanvasTkAgg(self._fig, canvas)
        self._figure_canvas.draw()
        self._figure_canvas.get_tk_widget().pack(side="top", fill="both", expand=0)

    def _update_reject_reasons(self):
        self._reject_reasons = self._catalog.tags_by(system_tag=False)
        self._reject_reasons.sort(key=lambda tag: tag.name)
        tag_names = [tag.name for tag in self._reject_reasons]
        self._window[LIST_DOC_REJECT].update(values=['Click me to add NEW reason...'] + tag_names)

    def _update_table(self, select_row=None):
        if select_row is not None:
            select_rows = [select_row]
        else:
            select_rows = None
        self._window[TABLE_DOCUMENTS].update(self._document_tuples(self._visible_documents), select_rows=select_rows)

