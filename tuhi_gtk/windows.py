from gi.repository import Gtk, GtkSource, GObject, Gdk

TITLE = "Tuhi"
MARGIN = 4
G = 0

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=TITLE)
        self.set_default_size(850, 600)
        self._init_headerbar()
        self._init_mainlayout()
        self._testing_only(test_spinners=False, test_searchbar=True)

    def _init_headerbar(self):
        # Side Header Bar
        self.side_hb = Gtk.HeaderBar()
        self.side_hb.set_show_close_button(False)
        # Main Header Bar
        self.main_hb = Gtk.HeaderBar()
        self.main_hb.set_show_close_button(True)
        self.main_hb.props.title = TITLE
        # Put them together in the title bar with a Gtk.Box
        self._title_bar = Gtk.Box()
        self._title_bar.pack_start(self.side_hb, expand=True, fill=True, padding=0)
        self._title_bar.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), expand=False, fill=False, padding=0)
        self._title_bar.pack_end(self.main_hb, expand=False, fill=False, padding=0)
        self.set_titlebar(self._title_bar)

    def _init_mainlayout(self):
        # Main Layout Pane
        self.main_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.add(self.main_paned)

        # Note List
        self.list = Gtk.ListBox()
        self.list.set_size_request(220, 200)
        self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        # ScrolledWindow around Note List
        self._scrolled_list = Gtk.ScrolledWindow()
        self._scrolled_list.add(self.list)
        self._scrolled_list.set_size_request(220, 50)
        self._scrolled_list.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Search Bar
        self.search_bar = Gtk.SearchBar()
        self.search_entry = Gtk.SearchEntry()
        self.search_bar.add(self.search_entry)

        # Pack List and SearchBar into a Box to add to Main Layout
        self.side_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.side_box.pack_start(self.search_bar, expand=False, fill=False, padding=0)
        self.side_box.pack_end(self._scrolled_list, expand=True, fill=True, padding=0)
        self.main_paned.pack1(self.side_box, resize=False, shrink=False)


        # SourceView
        self.source_view = GtkSource.View()
        # ScrolledWindow around SourceView
        self._scrolled_source_view = Gtk.ScrolledWindow()
        self._scrolled_source_view.add(self.source_view)
        # Add SourceView to Main Layout
        self.main_paned.pack2(self._scrolled_source_view, resize=True, shrink=True)

        # Headerbar size synchronization (SizeGroups don't auto update)
        self._scrolled_source_view.connect("size-allocate", self.synchronize_sizes_callback)
        # self.side_box.connect("size-allocate", self.synchronize_sizes_callback)
        # self.synchronize_sizes_callback(self.side_box, self.side_box.get_allocation())

    def synchronize_sizes_callback(self, side_box_widgit, allocation):
        # self.side_hb.set_size_request(allocation.width, -1)
        print(allocation.width)
        self.main_hb.set_size_request(allocation.width, -1)
        # TODO: TESTING ONLY: Debug size allocation print statements
        print(self.side_box.get_allocation().width, self.side_hb.get_allocation().width)
        # print(self.side_box.get_allocation().width, self.side_hb.get_allocation().width)

    # TODO: TESTING ONLY: Some NoteRow stubs for UI lnf testing before real logic
    def _testing_only(self, test_spinners=False, test_searchbar=False):
        self.side_hb.pack_end(Gtk.Button("S"))
        self.main_hb.pack_start(Gtk.Button("M"))

        import random
        for s in [
            "Test Note", "My little pony", "Canes Chicken",
            "Test Note 2", "Random Crap", "Welcome to Tuhi",
            "More Stuff", "Cool things!", "Blah blah blah",
            "Untitled", "Some cool note", "My not-so-little pony",
            "More and more stuff", "Hello world", "The language",
            "Blah blah blah blah blah blah blah blah blah"
        ]:
            x = NoteRow(s)
            self.list.add(x)

            if test_spinners:
                def gen_callback(note_row):
                    def callback():
                        if random.choice((True, False, False)):
                            note_row.spinner_start()
                        else:
                            note_row.spinner_stop()
                        return True
                    return callback

                # if s == "Random Crap" or s.startswith("Blah"):
                GObject.timeout_add(2000, gen_callback(x))
                x.spinner_start()
        if test_searchbar:
            self.search_bar.set_search_mode(True)


class NoteRow(Gtk.ListBoxRow):
    def __init__(self, s):
        Gtk.ListBoxRow.__init__(self)
        self.s = s
        # Label
        self.label = Gtk.Label.new(s)
        self.label.set_halign(Gtk.Align.START)
        self.label.set_margin_start(MARGIN)
        self.label.set_justify(Gtk.Justification.LEFT)
        # Label Viewport (Using Layout)
        self._label_viewport = Gtk.Layout()
        self._label_viewport.set_vscroll_policy(Gtk.ScrollablePolicy.MINIMUM)
        self._label_viewport.set_size_request(-1, 26)
        self._label_viewport.put(self.label, 0, 3)
        # Spinner
        self.spinner = Gtk.Spinner()
        self.spinner.set_halign(Gtk.Align.START)
        self.spinner_status = False
        # Container
        self._box = Gtk.Box()
        self._box.pack_start(self._label_viewport, expand=True, fill=True, padding=8)
        self.add(self._box)

    def spinner_start(self):
        if self.spinner_status is False:
            self.spinner.start()
            self._box.pack_end(self.spinner, expand=False, fill=False, padding=12)
            self.spinner_status = True

    def spinner_stop(self):
        if self.spinner_status is True:
            self.spinner.stop()
            self._box.remove(self.spinner)
            self.spinner_status = False
