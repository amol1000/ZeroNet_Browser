#!/usr/bin/env python

import gtk.gdk
from BrowserTab import *
from History import *



class Browser(gtk.Window):
    def __init__(self, *args, **kwargs):
        super(Browser, self).__init__(*args, **kwargs)
        self.connect("delete_event", lambda w, e: gtk.main_quit())

        self.notebook = gtk.Notebook()
        self.notebook.set_scrollable(True)

        self.add(self.notebook)

        self.tabs = []
        self.tabs_close = []
        self.tabs.append((self._create_tab(), gtk.Label("New Tab")))
        self.connect("key-press-event", self._key_pressed)
        self.notebook.connect("switch-page", self._tab_changed)

        self.notebook.show()
        self.show()
        self.maximize()

    def _tab_changed(self, notebook, current_page, index):
        current_page = self.tabs[index][0]
        title = current_page.webview.get_title()
        url = current_page.webview.get_main_frame().get_uri()

        if title:
            self._change_tab_label(title, current_page)

    def _change_tab_label(self, title, current_page):
        # path = download_favicon(url, target_dir='/home/abhishek/Desktop/Zeronet/ZeroNet-master/Browser/')
        # favicon_image = gtk.Image()
        # favicon_image = current_page.webview.favicon_database_get_favicon(url)
        label = self._create_tab_label(title)
        self.notebook.set_tab_label(current_page, label)
        label.show_all()

    def _title_changed(self, webview, frame, title):
        current_page = self.notebook.get_current_page()
        counter = 0
        for tab, label in self.tabs:
            if tab.webview is webview:
                label.set_text(title)
                if counter == current_page:
                    self._tab_changed(None, None, counter)
                break
            counter += 1

    def _create_tab(self):
        tab = BrowserTab()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_NEW, gtk.ICON_SIZE_MENU)
        label = self._create_tab_label("New Tab")
        self.notebook.set_tab_label_packing(tab, True, True, gtk.PACK_START)
        self.notebook.set_tab_label(tab, label)
        label.show_all()
        self.notebook.append_page(tab, label)
        tab.webview.connect("title-changed", self._title_changed)
        tab.new_tab_button.connect("clicked", self.open_new_tab)
        return tab

    def _create_tab_label(self, title):
        box = gtk.HBox()

        icon = gtk.Image()
        # icon = favicon_image

        label = gtk.Label(title)
        label.set_size_request(60, 20)

        close_button = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_button.connect("clicked", self.close_tab)
        close_button.set_image(image)
        close_button.set_relief(gtk.RELIEF_NONE)
        if close_button not in self.tabs_close:
            self.tabs_close.append(close_button)

        box.pack_start(icon, False, False)
        box.pack_start(label, True, True)
        box.pack_end(close_button, False, False)

        return box

    def _reload_tab(self):
        self.tabs[self.notebook.get_current_page()][0].webview.reload()

    def close_tab(self, widget):
        self._close_current_tab()

    def _close_current_tab(self):
        if self.notebook.get_n_pages() == 1:
            gtk.main_quit()
        page = self.notebook.get_current_page()
        current_tab = self.tabs.pop(page)
        self.notebook.remove(current_tab[0])

    def open_new_tab(self, widget):
        self._open_new_tab()

    def _open_new_tab(self):
        current_page = self.notebook.get_current_page()
        page_tuple = (self._create_tab(), gtk.Label("New Tab"))
        self.tabs.insert(current_page+1, page_tuple)
        self.notebook.set_current_page(current_page+1)

    def _focus_url_bar(self):
        current_page = self.notebook.get_current_page()
        self.tabs[current_page][0].url_textbox.grab_focus()

    def _raise_find_dialog(self):
        current_page = self.notebook.get_current_page()
        self.tabs[current_page][0].find_box.show_all()
        self.tabs[current_page][0].find_entry.grab_focus()

    def _show_history(self):
        tab = self.tabs[self.notebook.get_current_page()][0]
        tab.show_history()

    def _show_bookmarks(self):
        tab = self.tabs[self.notebook.get_current_page()][0]
        tab.show_bookmarks()

    def _key_pressed(self, widget, event):
        key_value = event.keyval
        key_value_name = gtk.gdk.keyval_name(key_value)  # gives actual key
        state = event.state
        ctrl = (state & gtk.gdk.CONTROL_MASK)  # ctrl button

        mapping = {'r': self._reload_tab,
                   'w': self._close_current_tab,
                   't': self._open_new_tab,
                   'l': self._focus_url_bar,
                   'f': self._raise_find_dialog,
                   'h': self._show_history,
                   'b': self._show_bookmarks,
                   'q': self._quit}

        if ctrl and key_value_name in mapping:
            mapping[key_value_name]()

    def _quit(self):
        gtk.main_quit()

if __name__ == "__main__":
    browser = Browser()
    gtk.main()
