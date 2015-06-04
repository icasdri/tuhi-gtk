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
        self._init_sizegroups()
        self._testing_only_noterow_stubs(test_spinners=False)

    def _init_headerbar(self):
        # Header Bar
        self.side_hb = Gtk.HeaderBar()
        self.side_hb.set_show_close_button(False)
        self.main_hb = Gtk.HeaderBar()
        self.main_hb.set_show_close_button(True)
        self.main_hb.props.title = TITLE

        self.side_hb.pack_end(Gtk.Button("S"))
        self.main_hb.pack_start(Gtk.Button("M"))
        self._title_bar = Gtk.Box()
        # self._title_bar.add(self.side_hb)
        # self._title_bar.add(self.main_hb)
        # self._title_bar = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        # self._title_bar.pack1(self.side_hb)
        # self._title_bar.pack2(self.main_hb)
        self._title_bar.pack_start(self.side_hb, expand=False, fill=False, padding=0)
        self._title_bar.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), expand=False, fill=False, padding=1)
        self._title_bar.pack_end(self.main_hb, expand=True, fill=True, padding=0)
        self.set_titlebar(self._title_bar)

    def _init_mainlayout(self):
        # Main Layout Pane
        self.main_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.add(self.main_paned)
        self.main_paned.connect("move-handle", lambda p, s: print("Hi"))

        # Note List
        self.list = Gtk.ListBox()
        self.list.set_size_request(200, 200)
        self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        # ScrolledWindow around Note List
        self._scrolled_list = Gtk.ScrolledWindow()
        self._scrolled_list.add(self.list)
        self._scrolled_list.set_size_request(210, 50)
        self._scrolled_list.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Add Note List to Main Layout
        # Search Bar
        self.side_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.search_bar = Gtk.SearchBar()
        self.search_entry = Gtk.SearchEntry()
        self.search_bar.add(self.search_entry)
        self.side_box.pack_start(self.search_bar, expand=False, fill=False, padding=0)
        self.side_box.pack_end(self._scrolled_list, expand=True, fill=True, padding=0)
        self.main_paned.pack1(self.side_box, resize=False, shrink=False)
        self.search_bar.set_search_mode(True)
        # self.main_paned.pack1(self._scrolled_list, resize=False, shrink=False)

        self.side_box.connect("size-allocate", self.synchronize_sizes)

        # SourceView
        self.source_view = GtkSource.View()
        # ScrolledWindow around SourceView
        self._scrolled_source_view = Gtk.ScrolledWindow()
        self._scrolled_source_view.add(self.source_view)
        # Add SourceView to Main Layout
        self.main_paned.pack2(self._scrolled_source_view, resize=True, shrink=True)

    def _init_sizegroups(self):
        # side_sizegroup = Gtk.SizeGroup.new(Gtk.SizeGroupMode.HORIZONTAL)
        # side_sizegroup.add_widget(self.side_hb)
        # side_sizegroup.add_widget(self._scrolled_list)
        # main_sizegroup = Gtk.SizeGroup.new(Gtk.SizeGroupMode.HORIZONTAL)
        # main_sizegroup.add_widget(self.main_hb)
        # main_sizegroup.add_widget(self._scrolled_source_view)
        pass

    # TODO: TESTING ONLY: Some NoteRow stubs for UI lnf testing before real logic
    def _testing_only_noterow_stubs(self, test_spinners=False):
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

    def synchronize_sizes(self, side_box_widgit, allocation):
        print(allocation.width)
        self.side_hb.set_size_request(allocation.width-2, -1)


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
