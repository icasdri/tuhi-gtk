from gi.repository import Gtk, GtkSource, GObject, Gdk

TITLE = "Tuhi"
MARGIN = 4

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=TITLE)
        self.set_default_size(850, 600)

        # Header Bar
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.hb.props.title = TITLE
        self.set_titlebar(self.hb)

        # Main Layout
        self.main_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.add(self.main_paned)

        self.list = Gtk.ListBox()
        self.list.set_size_request(200, 200)
        self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)

        self._scrolled_list = Gtk.ScrolledWindow()
        self._scrolled_list.add(self.list)
        self._scrolled_list.set_size_request(200, 50)
        self._scrolled_list.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

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
            self.list.add(x)

        self.main_paned.pack1(self._scrolled_list, resize=False, shrink=False)

        self.source_view = GtkSource.View()
        self._scrolled_source_view = Gtk.ScrolledWindow()
        self._scrolled_source_view.add(self.source_view)
        self.main_paned.pack2(self._scrolled_source_view, resize=True, shrink=True)


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
