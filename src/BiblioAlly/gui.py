import datetime

import PySimpleGUI as sg
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

TABLE_DOCUMENTS = '-DOCUMENTS-'
DOC_ABSTRACT = '-DOC-ABSTRACT-'
DOC_AUTHORS = '-DOC-AUTHORS-'
DOC_DOI = '-DOC-DOI-'
DOC_EXTERNAL_KEY = '-DOC-EXTERNAL-KEY-'
DOC_KEYWORDS = '-DOC-KEYWORDS-'
DOC_KIND = '-DOC-KIND-'
DOC_METADATA = '-DOC-METADATA-'
DOC_ORIGIN = '-DOC-ORIGIN-'
DOC_REASON = '-DOC-REASON-'
DOC_TITLE = '-DOC-TITLE-'
DOC_YEAR = '-DOC-YEAR-'

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
text_color = 'orange'
button_base_font = 'Arial 10'

duplicate_color = ('#ECFFFF', '#FAB420')
reject_color = ('#ECFFFF', '#E94763')
import_color = ('#ECFFFF', '#737A97')
preselect_color = ('#ECFFFF', '#37A4F6')
select_color = ('#ECFFFF', '#03A399')

doc_headings = ['Year', 'Title', 'Authors', 'Kind', 'Origin', 'Tags']
doc_widths = [4, 95, 45, 15, 15, 20]

# Add your new theme colors and settings
sg.LOOK_AND_FEEL_TABLE['BiblioAllyTheme'] = {
    'BACKGROUND': '#212735',
    'TEXT': '#737A97',
    'INPUT': '#36394C',
    'TEXT_INPUT': '#737A97',
    'SCROLL': '#737A97',
    'BUTTON': ('#F0F0F0', '#626ED4'),
    'PROGRESS': ('#D1826B', '#CC8019'),
    'BORDER': 1,
    'SLIDER_DEPTH': 0,
    'PROGRESS_DEPTH': 0,
}
sg.theme('BiblioAllyTheme')
table_alternate_color = '#36394C'
table_background_color = '#333A47'


class Browser:
    def __init__(self, catalog: cat.Catalog):
        self._catalog = catalog
        self._doc_fields = ['year', 'title', 'authors', 'kind', 'generator', 'tags']
        self._reject_reasons = []
        self._all_documents = []
        self._visible_documents = []
        self._active_tags = [
            domain.TAG_ACCEPTED, domain.TAG_DUPLICATE, domain.TAG_EXCLUDED, domain.TAG_IMPORTED, domain.TAG_PRE_ACCEPTED
        ]
        self._selected_document = None
        self._window = None


    def show(self):
        self._load_documents()
        self._filter_documents()

        self._window = self._main_window()
        self._window.read(timeout=1)
        self._update_table()
        self._update_reject_reasons()
        self._select_document_by_index(0)
        self._window[TABLE_DOCUMENTS].expand(True, True)
        self._window[COL_OPERATIONS].expand(True, True)
        self._window[DOC_METADATA].expand(True, True)
        self._window[DOC_METADATA].update(visible=False)
        self._window[LIST_DOC_REJECT].expand(True, True)
        self._window[LIST_DOC_REJECT].update(visible=False)

        while True:
            event, values = self._window.read()
            if event == sg.WINDOW_CLOSED or event == BUTTON_EXIT:
                break
            if event == TABLE_DOCUMENTS and values[TABLE_DOCUMENTS]:
                row_index = values[TABLE_DOCUMENTS][0]
                self._select_document_by_index(row_index)
            elif event in filter_buttons:
                self._toggle_filter_button(event)
                self._filter_documents()
                self._update_table()
                self._select_document_by_index(0)
            elif event == LIST_DOC_REJECT:
                reject_reason = values[LIST_DOC_REJECT][0]
                if type(reject_reason) is str:
                    new_reason_text = sg.popup_get_text('Enter your new rejection reason:')
                    if new_reason_text is not None:
                        self.reject_document(self._selected_document, new_reason_text)
                        self._update_reject_reasons()
                elif type(reject_reason) is domain.Reason:
                    self.reject_document(self._selected_document, reject_reason)
                self._filter_documents()
                self._update_table(row_index)
                self._select_document_by_index(row_index)
            elif event == BUTTON_EDIT_DOC_METADATA:
                self._edit_metadata()
            elif self._selected_document is not None:
                if event == BUTTON_DOC_PRESELECT:
                    self.pre_select_document(self._selected_document)
                    self._filter_documents()
                    self._update_table(row_index)
                    self._select_document_by_index(row_index)
                elif event == BUTTON_DOC_SELECT:
                    self.select_document(self._selected_document)
                    self._filter_documents()
                    self._update_table(row_index)
                    self._select_document_by_index(row_index)
                elif event == BUTTON_DOC_RESET:
                    self.reset_document(self._selected_document)
                    self._filter_documents()
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

    def reject_document(self, document: domain.Document, reason: domain.Reason):
        self._catalog.tag(document, domain.TAG_EXCLUDED)
        document.untag(domain.TAG_IMPORTED)
        if type(reason) is str:
            new_reason = domain.Reason(reason)
            reason = new_reason
        document.reason = reason
        self._catalog.commit()
        return reason

    def select_document(self, document: domain.Document):
        self._catalog.tag(document, domain.TAG_ACCEPTED)
        self._catalog.untag(document, domain.TAG_PRE_ACCEPTED)
        document.reason = None
        self._catalog.commit()

    def reset_document(self, document: domain.Document):
        self._catalog.tag(document, domain.TAG_IMPORTED)
        self._catalog.untag(document, domain.TAG_ACCEPTED)
        self._catalog.untag(document, domain.TAG_EXCLUDED)
        self._catalog.untag(document, domain.TAG_PRE_ACCEPTED)
        document.reason = None
        self._catalog.commit()

    def _document_is_in_filter(self, document: domain.Document, active_tags):
        tags = [t.tag.name for t in document.tags]
        in_filter = all(f in active_tags for f in tags)
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
        window = sg.Window('Edit Metadata', edit_metadata_layout, resizable=True, element_padding=1)
        event, values = window.read(timeout=1)
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
                self._window[DOC_METADATA].update(content)
                break
        window.close()

    def _main_window(self):
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
                        sg.Button('Exit!', key=BUTTON_EXIT)
                    ],
                ], element_justification='right')

            ],
            [
                sg.Table([], key=TABLE_DOCUMENTS, enable_events=True, headings=doc_headings,
                         alternating_row_color=table_background_color,
                         auto_size_columns=False, col_widths=doc_widths, justification='left',
                         visible_column_map=[h[0] != '~' for h in doc_headings], num_rows=20)
            ],
            [
                sg.Column([
                    [
                        sg.Text('Year:', font=label_font),
                        sg.Text(text='', key=DOC_YEAR, size=(4, 1), font=text_font, text_color=text_color),
                        sg.Text('Title:', font=label_font),
                        sg.Text(text='', key=DOC_TITLE, size=(70, 1), font=text_font, text_color=text_color),
                    ],
                    [
                        sg.Text('Authors:', font=label_font),
                        sg.Text(text='', key=DOC_AUTHORS, size=(70, 1), font=text_font, text_color=text_color),
                    ],
                    [
                        sg.Text('Kind:', font=label_font),
                        sg.Text(text='', key=DOC_KIND, size=(20, 1), font=text_font, text_color=text_color),
                        sg.Text('Origin:', font=label_font),
                        sg.Text(text='', key=DOC_ORIGIN, size=(20, 1), font=text_font, text_color=text_color),
                        sg.Text('DOI:', font=label_font),
                        sg.Text(text='', key=DOC_DOI, size=(30, 1), font=text_font, text_color=text_color),
                        sg.Text('External key:', font=label_font),
                        sg.Text(text='', key=DOC_EXTERNAL_KEY, size=(20, 1), font=text_font, text_color=text_color),
                    ],
                    [
                        sg.Text('Rejection reason:', font=label_font),
                        sg.Text(text='', key=DOC_REASON, size=(70, 1), font=text_font, text_color=text_color),
                    ],
                    [
                        sg.Column([
                            [sg.Text('Abstract', font=label_font)],
                            [sg.Multiline(key=DOC_ABSTRACT, default_text='', size=(100, 20), disabled=True,
                                          autoscroll=True)]
                        ]),
                        sg.Column([
                            [sg.Text('Keywords', font=label_font)],
                            [sg.Multiline(key=DOC_KEYWORDS, default_text='', size=(40, 20), disabled=True,
                                          autoscroll=True)]
                        ]),
                    ]
                ]),
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
                        sg.Listbox([], key=LIST_DOC_REJECT, size=(94, 24), enable_events=True, visible=False),
                        sg.Multiline(default_text='', key=DOC_METADATA, size=(94, 24), font=metadata_font,
                                     disabled=True, visible=False, autoscroll=True)
                    ],
                    [
                        sg.Button('Edit metadata', key=BUTTON_EDIT_DOC_METADATA, visible=False)
                    ]
                ], key=COL_OPERATIONS),
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
            self._window[DOC_ABSTRACT].update('')
            self._window[DOC_AUTHORS].update('')
            self._window[DOC_DOI].update('')
            self._window[DOC_EXTERNAL_KEY].update('')
            self._window[DOC_KEYWORDS].update('')
            self._window[DOC_KIND].update('')
            self._window[DOC_METADATA].update('')
            self._window[DOC_ORIGIN].update('')
            self._window[DOC_REASON].update('')
            self._window[DOC_TITLE].update('')
            self._window[DOC_YEAR].update('')
            self._window[BUTTON_DOC_PRESELECT].update(disabled=True)
            self._window[BUTTON_DOC_SELECT].update(disabled=True)
            self._window[BUTTON_DOC_RESET].update(disabled=True)
            self._window[LABEL_DOC_REJECT].update(visible=False)
            self._window[LIST_DOC_REJECT].update(visible=False)
            return
        self._window[DOC_ABSTRACT].update(document.abstract)
        self._window[DOC_AUTHORS].update(self.author_names(document.authors))
        self._window[DOC_DOI].update(document.doi)
        self._window[DOC_EXTERNAL_KEY].update(document.external_key)
        self._window[DOC_KEYWORDS].update(self.keyword_names(document.keywords))
        self._window[DOC_KIND].update(document.kind)
        self._window[DOC_METADATA].update(document.review_metadata.content
                                          if document.review_metadata is not None else '')
        self._window[DOC_ORIGIN].update(document.generator)
        if document.reason is not None:
            self._window[DOC_REASON].update(document.reason.description)
        else:
            self._window[DOC_REASON].update('')
        self._window[DOC_TITLE].update(document.title)
        self._window[DOC_YEAR].update(document.year)
        self._window[BUTTON_DOC_PRESELECT].update(disabled=document.is_tagged(domain.TAG_PRE_ACCEPTED))
        self._window[BUTTON_DOC_SELECT].update(disabled=not document.is_tagged(domain.TAG_PRE_ACCEPTED))
        element_visible = document.is_tagged(domain.TAG_IMPORTED) or document.is_tagged(domain.TAG_PRE_ACCEPTED)
        self._window[LABEL_DOC_REJECT].update(visible=element_visible)
        self._window[LIST_DOC_REJECT].update(visible=element_visible)
        element_visible = document.is_tagged(domain.TAG_ACCEPTED)
        self._window[LABEL_DOC_METADATA].update(visible=element_visible)
        self._window[DOC_METADATA].update(visible=element_visible)
        self._window[BUTTON_EDIT_DOC_METADATA].update(visible=element_visible)

    def _update_reject_reasons(self):
        self._reject_reasons = self._catalog.reasons()
        self._reject_reasons.sort(key=lambda item: item.description)
        self._window[LIST_DOC_REJECT].update(values=['Click me to add NEW reason...'] + self._reject_reasons)

    def _update_table(self, select_row=None):
        if select_row is not None:
            select_rows = [select_row]
        else:
            select_rows = None
        self._window[TABLE_DOCUMENTS].update(self._document_tuples(self._visible_documents), select_rows=select_rows)

