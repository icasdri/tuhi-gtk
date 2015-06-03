from gi.repository import Gtk, GtkSource, GObject

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

        import random
        for s in [
            "Test Note", "My little pony", "Canes Chicken",
            "Test Note 2", "Random Crap", "Welcome to Tuhi",
            "More Stuff", "Cool things!", "Blah blah blah",
            "Untitled", "Some cool note",
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
        # x.spinner_stop()

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
        # Spinner
        self.spinner = Gtk.Spinner()
        self.spinner.set_halign(Gtk.Align.START)
        self.spinner_status = False
        # Container
        # self._overlay = Gtk.Overlay()
        # self._overlay.add(self.label)
        # self._overlay.add_overlay(self.spinner)
        self._box = Gtk.Box()
        self._box.pack_end(self.label, expand=True, fill=True, padding=MARGIN)
        self.add(self._box)

    def spinner_start(self):
        if self.spinner_status is False:
            self.spinner.start()
            self._box.pack_start(self.spinner, expand=False, fill=False, padding=MARGIN)
            self.spinner_status = True
        # self.label.set_text("    " + self.s)

    def spinner_stop(self):
        if self.spinner_status is True:
            self.spinner.stop()
            self._box.remove(self.spinner)
            self.spinner_status = False
            # self.label.set_text(self.s)
