from gi.repository import Gtk, GtkSource

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

        for s in [
            "Test Note", "My little pony", "Canes Chicken",
            "Blah blah blah blah blah blah blah blah blah"
                ]:
            self.list.add(NoteRow(s))

        self.main_paned.pack1(self._scrolled_list, resize=False, shrink=True)

        self.source_view = GtkSource.View()
        self._scrolled_source_view = Gtk.ScrolledWindow()
        self._scrolled_source_view.add(self.source_view)
        self.main_paned.pack2(self._scrolled_source_view, resize=True, shrink=True)


class NoteRow(Gtk.ListBoxRow):
    def __init__(self, s):
        Gtk.ListBoxRow.__init__(self)
        self.s = s
        self.label = Gtk.Label.new(s)
        # self.label.set_alignment()
        self.label.set_halign(Gtk.Align.START)
        self.label.set_margin_start(MARGIN)
        self.label.set_justify(Gtk.Justification.LEFT)
        self.add(self.label)
