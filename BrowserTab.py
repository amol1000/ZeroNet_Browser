#!/usr/bin/env python
import glib
import os
import signal
import subprocess
import webkit
import datetime
import gtk
from pySmartDL import SmartDL
from History import *

pid = 0

bookmarks_list = []


def find(name, path):
        for root, dirs, files in os.walk(path):
                    if name in files:
                        return os.path.join(root, name)
                    elif name in dirs:
                        return os.path.join(root, name)


class BrowserTab(gtk.VBox):
    def __init__(self, *args, **kwargs):
        super(BrowserTab, self).__init__(*args, **kwargs)

        h = History()
        row = h.get_bookmark_list()
        for r in row:
            bookmarks_list.append(r[0])

        self.zeronet_button = gtk.ToggleButton()
        self.zeronet_button.set_size_request(50, 50)
        self.zeronet_button.connect("clicked", self.start_zeronet)

        self.bottom_hpan = gtk.HPaned()

        self.webview = webkit.WebView()
        scrolled_window = gtk.ScrolledWindow()
        self.webview.connect("load-finished", self.on_finish_loading)
        self.webview.connect("download-requested", self.initiate_download)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(self.webview)

        self.history_window = gtk.ScrolledWindow()
        self.history_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.history_window.set_size_request(200, 10)
        self.history_box = gtk.VBox()
        header_hbox = gtk.HBox()
        header = gtk.Label("History")
        close_button = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_button.connect("clicked", self.hide_history)
        close_button.set_image(image)
        close_button.set_relief(gtk.RELIEF_NONE)
        header_hbox.pack_start(header, True, True, 0)
        header_hbox.pack_end(close_button, False, False, 0)
        self.history_box.pack_start(header_hbox, False, False, 0)
        self.history_list_store = gtk.ListStore(str)
        self.history_tree_view = gtk.TreeView(self.history_list_store)
        self.history_box.pack_start(self.history_window, True, True, 0)
        self.history_window.add_with_viewport(self.history_tree_view)

        self.bookmarks_window = gtk.ScrolledWindow()
        self.bookmarks_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.bookmarks_box = gtk.VBox()
        self.bookmarks_window.set_size_request(200, 10)
        header_hbox = gtk.HBox()
        header = gtk.Label("Bookmarks")
        close_button = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_button.connect("clicked", self.hide_bookmarks)
        close_button.set_image(image)
        close_button.set_relief(gtk.RELIEF_NONE)
        header_hbox.pack_start(header, True, True, 0)
        header_hbox.pack_end(close_button, False, False, 0)
        self.bookmarks_box.pack_start(header_hbox, False, False, 0)
        self.bookmarks_list_store = gtk.ListStore(str)
        self.bookmarks_tree_view = gtk.TreeView(self.bookmarks_list_store)
        self.bookmarks_box.pack_start(self.bookmarks_window, True, True, 0)
        self.bookmarks_window.add_with_viewport(self.bookmarks_tree_view)

        self.find_entry = gtk.Entry()
        self.find_entry.connect("activate",
                                lambda x: self.webview.search_text(self.find_entry.get_text(),
                                                                   False, True, True))
        find_box = gtk.HBox()
        close_button = gtk.Button("Close")
        close_button.connect("clicked", lambda x: find_box.hide())
        prev_button = gtk.Button("Previous")
        next_button = gtk.Button("Next")
        prev_button.connect("clicked",
                            lambda x: self.webview.search_text(self.find_entry.get_text(),
                                                               False, False, True))
        next_button.connect("clicked",
                            lambda x: self.webview.search_text(self.find_entry.get_text(),
                                                               False, True, True))
        find_box.pack_start(close_button, False, False, 0)
        find_box.pack_start(self.find_entry, False, False, 0)
        find_box.pack_start(prev_button, False, False, 0)
        find_box.pack_start(next_button, False, False, 0)
        self.find_box = find_box
        self.pack_end(find_box, False, False, 0)

        main_hbox = gtk.HBox(False, 0)
        menu_url_vbox = gtk.VBox(False, 0)
        menu_hbox = gtk.HBox(False, 0)
        url_hbox = gtk.HBox(False, 0)

        image = gtk.Image()
        self.new_tab_button = gtk.Button()
        image.set_from_stock(gtk.STOCK_NEW, gtk.ICON_SIZE_MENU)
        self.new_tab_button.set_image(image)
        self.new_tab_button.set_relief(gtk.RELIEF_NONE)

        self.menu1 = gtk.Button("Create")
        self.menu1.connect("clicked", self.create_site)

        self.menu2 = gtk.Button("Update")
        self.menu2.connect("clicked", self.signSite)

        self.menu3 = gtk.Button("Publish")
        self.menu3.connect("clicked", self.publish_site)

        self.settings = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU)

        self.settings.set_image(image)
        self.settings.set_size_request(78, 30)
        self.settings.set_relief(gtk.RELIEF_NONE)

        self.menu = gtk.Menu()
        self.menu_items = ["New Tab", "History", "Bookmarks", "About", "Quit"]

        for i in self.menu_items:
                menu_item = gtk.MenuItem(i)
                self.menu.append(menu_item)
                menu_item.connect("activate", self.menuitem_response, i)
                menu_item.show()

        self.settings.connect("event", self.menu_show)

        self.url_textbox = gtk.Entry()

        self.go_back = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_GO_BACK, gtk.ICON_SIZE_MENU)
        self.go_back.set_image(image)
        self.go_back.connect("clicked", lambda x: self.webview.go_back())
        self.go_back.set_relief(gtk.RELIEF_NONE)
        self.url_textbox.connect("activate", self.load_url)

        image = gtk.Image()
        self.go_forward = gtk.Button()
        image.set_from_stock(gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_MENU)
        self.go_forward.set_image(image)
        self.go_forward.connect("clicked", lambda x: self.webview.go_forward())
        self.go_forward.set_relief(gtk.RELIEF_NONE)

        image = gtk.Image()
        image.set_from_file("not_bookmarked.ico")
        self.bookmark_image = gtk.ToggleButton()
        self.bookmark_image.set_image(image)
        self.bookmark_image.set_active(False)

        vertical_line = gtk.VSeparator()

        image = gtk.Image()
        self.bookmark_button = gtk.Button()
        image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        self.bookmark_button.set_image(image)
        self.bookmark_button.connect("clicked", self.add_bookmark)
        self.bookmark_button.set_relief(gtk.RELIEF_NONE)

        image = gtk.Image()
        self.refresh = gtk.Button()
        image.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU)
        self.refresh.set_image(image)
        self.refresh.connect("clicked", lambda x: self.webview.reload())
        self.refresh.set_relief(gtk.RELIEF_NONE)

        self.secure_icon = gtk.Image()
        self.secure_button = gtk.Button()
        self.secure_icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        self.secure_button.set_image(self.secure_icon)

        self.dialog = gtk.Dialog(title="ZeroNet")
        self.pbar = gtk.ProgressBar()
        self.pbar.set_text("Starting Zeronet")
        self.dialog.vbox.pack_start(self.pbar, True, True, 0)
        self.pbar.show()

        self.pack_start(main_hbox, False, False, 0)

        main_hbox.pack_start(menu_url_vbox, True, True, 0)

        menu_url_vbox.pack_start(menu_hbox, True, True, 0)

        menu_hbox.pack_start(self.new_tab_button, False, True, 0)
        menu_hbox.pack_start(self.menu1, True, True, 0)
        menu_hbox.pack_start(self.menu2, True, True, 0)
        menu_hbox.pack_start(self.menu3, True, True, 0)
        menu_hbox.pack_end(self.settings, False, False, 0)

        menu_url_vbox.pack_start(url_hbox, True, True, 0)

        url_hbox.pack_start(self.go_back, False, False, 0)
        url_hbox.pack_start(self.secure_button, False, False, 0)
        url_hbox.pack_start(self.url_textbox, True, True, 0)
        url_hbox.pack_start(self.refresh, False, False, 0)
        url_hbox.pack_start(self.go_forward, False, False, 0)
        url_hbox.pack_start(self.bookmark_image, False, False, 0)
        url_hbox.pack_start(vertical_line, False, False, 2)
        url_hbox.pack_start(self.bookmark_button, False, False, 0)

        main_hbox.pack_start(self.zeronet_button, False, False, 0)

        self.bottom_hpan.add2(scrolled_window)

        self.pack_start(self.bottom_hpan, True, True, 0)

        scrolled_window.show_all()
        main_hbox.show_all()
        self.bottom_hpan.show()

        image = gtk.Image()
        if not pid:
                image.set_from_file("2.png")
                self.zeronet_button.set_image(image)
                self.zeronet_button.set_active(False)
        else:
                image.set_from_file("1.png")
                self.zeronet_button.set_image(image)
                self.zeronet_button.set_active(True)
        self.show()

    def load_url(self, widget):
        url = self.url_textbox.get_text()
        if "://" not in url:
            url = "http://" + url
        self.webview.load_uri(url)

    def on_finish_loading(self, widget, frame):
        url = self.webview.get_main_frame().get_uri()

        # set the security icon
        if "https://" in url:
            self.secure_icon.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_MENU)
        else:
            self.secure_icon.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU)

        # set the url bar
        self.url_textbox.set_text(url)

        # add history
        title = self.webview.get_title()
        time = datetime.datetime.now().strftime("%H:%M:%S")
        date = datetime.datetime.now().date()
        h = History()
        h.insert_history(title, url, time, date)

        # check bookmark
        if title in bookmarks_list:
            image = gtk.Image()
            image.set_from_file("bookmarked.ico")
            self.bookmark_image.set_active(True)
            self.bookmark_image.set_image(image)
        else:
            image = gtk.Image()
            image.set_from_file("not_bookmarked.ico")
            self.bookmark_image.set_active(False)
            self.bookmark_image.set_image(image)

    def menu_show(self, widget, event):
            if event.type == gtk.gdk.BUTTON_PRESS:
                    self.menu.popup(None, None, None, event.button, event.time)
                    return True
            return False

    def menuitem_response(self, widget, string):
            mapping_settings = {"History": self.show_history,
                                "Bookmarks": self.show_bookmarks}
            if string in mapping_settings:
                    mapping_settings[string]()

    def show_history(self):
        if self.bookmarks_box.get_property("visible"):
            self.hide_bookmarks(self.bookmarks_box)

        if self.history_box.get_property("visible"):
            self.history_box.hide()
            self.bottom_hpan.remove(self.history_box)
            self.history_list_store.clear()
            column_list = self.history_tree_view.get_columns()
            for iter_column in column_list:
                self.history_tree_view.remove_column(iter_column)

        else:
            self.bottom_hpan.add1(self.history_box)
            h = History()
            h.cursor.execute("select title from history")
            row = h.cursor.fetchone()
            while row:
                self.history_list_store.append(row)
                row = h.cursor.fetchone()

            for i, col_title in enumerate(["Title"]):
                renderer = gtk.CellRendererText()
                column = gtk.TreeViewColumn(col_title, renderer, text=i)
                column.set_min_width(50)
                column.set_max_width(100)
                self.history_tree_view.append_column(column)

            self.history_box.show_all()

    def hide_history(self, widget):
        self.history_box.hide()
        self.bottom_hpan.remove(self.history_box)
        self.history_list_store.clear()
        column_list = self.history_tree_view.get_columns()
        for iter_column in column_list:
                self.history_tree_view.remove_column(iter_column)

    def add_bookmark(self, widget):
        h = History()
        title = self.webview.get_title()
        url = self.webview.get_main_frame().get_uri()

        if url:
            image = gtk.Image()
            if self.bookmark_image.get_active():
                image.set_from_file("not_bookmarked.ico")
                self.bookmark_image.set_image(image)
                self.bookmark_image.set_active(False)
                h.remove_bookmark(title)
            else:
                h.add_bookmark(title, url)
                image.set_from_file("bookmarked.ico")
                self.bookmark_image.set_image(image)
                self.bookmark_image.set_active(True)

    def show_bookmarks(self):
        if self.history_box.get_property("visible"):
            self.hide_history(self.history_box)

        if self.bookmarks_box.get_property("visible"):
            self.bookmarks_box.hide()
            self.bottom_hpan.remove(self.bookmarks_box)
            self.bookmarks_list_store.clear()
            column_list = self.bookmarks_tree_view.get_columns()
            for iter_column in column_list:
                self.bookmarks_tree_view.remove_column(iter_column)

        else:
            self.bottom_hpan.add1(self.bookmarks_box)
            h = History()
            h.cursor.execute("select title from bookmarks")
            row = h.cursor.fetchone()
            while row:
                self.bookmarks_list_store.append(row)
                row = h.cursor.fetchone()

            for i, col_title in enumerate(["Title"]):
                renderer = gtk.CellRendererText()
                column = gtk.TreeViewColumn(col_title, renderer, text=i)
                self.bookmarks_tree_view.append_column(column)

            self.bookmarks_box.show_all()

    def hide_bookmarks(self, widget):
        self.bookmarks_box.hide()
        self.bottom_hpan.remove(self.bookmarks_box)
        self.bookmarks_list_store.clear()
        iter_column = gtk.TreeViewColumn()
        column_list = self.bookmarks_tree_view.get_columns()
        for iter_column in column_list:
                self.bookmarks_tree_view.remove_column(iter_column)

    def start_zeronet(self, widget):
        file_name = find("zeronet.py", "/home/")
        global pid
        image = gtk.Image()
        if pid:
                os.kill(int(pid), signal.SIGTERM)
                pid = 0
                image.set_from_file("2.png")
                self.zeronet_button.set_image(image)

        else:
                zeronet_proc = subprocess.Popen(file_name)
                pid = zeronet_proc.pid
                self.dialog.show()
                image.set_from_file("1.png")
                self.zeronet_button.set_image(image)
                glib.timeout_add(100, self.progress_timeout)
                glib.timeout_add(5000, self.dialog_hide)

    def create_site(self, widget):

        filename = find("zeronet.py", "/home/")
        sitecreate_proc = subprocess.Popen([filename, 'siteCreate'], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                           shell=False)

        dialog = gtk.Dialog("Create Site",
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        label = gtk.Label("note down text from terminal")
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()

        dialog.show()

        response = dialog.run()

        if response == gtk.RESPONSE_ACCEPT :
                out = sitecreate_proc.communicate("yes")
                print out

                dialog.destroy()

    def responsetosignsite(signal, entry, dialog, response):
        dialog.response(response)

    def signSite(self, widget):
        name_dialog = gtk.Dialog("Update site",
                                 None,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        label = gtk.Label("NAME OF THE SITE TO BE UPDATED")
        entry = gtk.Entry()
        entry.connect("activate", self.responsetosignsite, name_dialog, gtk.RESPONSE_OK)
        hbox = gtk.HBox()
        hbox.pack_start(label, False, 5, 5)
        hbox.pack_end(entry, True, True, 0)
        name_dialog.vbox.pack_start(hbox, True
                                    , True, 0)
        name_dialog.show_all()
        response = name_dialog.run()

        name = entry.get_text()
        site_name = find(name, "/home")
        p = subprocess.Popen(['xdg-open', site_name])

        if response == gtk.RESPONSE_ACCEPT:
            filename = find("zeronet.py", "/home/")
        siteupdate_proc = subprocess.Popen([filename, 'siteSign', name], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                       shell=False)
        name_dialog.destroy()
        dialog = gtk.Dialog("Create Site",
                    None,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        label = gtk.Label("Enter Private Key in Terminal")
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        dialog.show()

        private_response = dialog.run()

        if private_response == gtk.RESPONSE_ACCEPT:
            dialog.destroy()

    def publish_site(self, widget):
        filename = find("zeronet.py", "/home/")
        entry_dialog = gtk.Dialog("Publish site",
                                  None,
                                  gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                  (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        label = gtk.Label("Name of the site to be Published")
        entry = gtk.Entry()
        hbox = gtk.HBox()
        hbox.pack_start(label, True, 0, 0)
        hbox.pack_end(entry, True, True, 0)
        entry_dialog.vbox.pack_start(hbox, True, True, 0)
        entry_dialog.show_all()
        response = entry_dialog.run()
        site_name = entry.get_text()

        if response == gtk.RESPONSE_ACCEPT:
            subprocess.Popen([filename, 'sitePublish', site_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             shell=False)

    def progress_timeout(self):
        self.pbar.pulse()
        return True

    def dialog_hide(self):
        self.dialog.hide()
        self.url_textbox.set_text(
            "http://127.0.0.1:43110/1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D/")
        self.webview.load_uri(
            "http://127.0.0.1:43110/1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D/")
        return False

    def initiate_download(self, webview, download):
        name = download.get_suggested_filename()
        print name
        url = download.get_uri()
        print url
        '''
        path = os.path.join('/home/amol/Downloads/test', name)
        urllib.urlretrieve(download.get_uri(), path)  # urllib.request.urlretrieve
        '''
        dest = '/home/amol/Downloads/test/'
        obj = SmartDL(url, dest)
        obj.start()
        path = obj.get_dest()
        print path
        return False
