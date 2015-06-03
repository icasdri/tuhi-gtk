from gi.repository import Gtk, GtkSource

TITLE = "Tuhi"

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
        # self.grid = Gtk.Table(1, 4, True)
        # self.add(self.grid)
        self.main_box = Gtk.Box()
        self.add(self.main_box)

        self.list = Gtk.ListBox()
        self.list.set_size_request(20, 20)
        self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)

        for s in [
            "Test Note", "My little pony", "Canes Chicken",
            "Blah blah blah blah blah blah blah blah blah"
                ]:
            self.list.add(NoteRow(s))

        # self.grid.attach(self.list, 0, 1, 0, 1)
        self.main_box.pack_start(self.list, expand=False, fill=True, padding=2)

        self.source_view = GtkSource.View()
        # self.grid.attach(self.source_view, 1, 4, 0, 1)
        self.main_box.pack_end(self.source_view, expand=True, fill=True, padding=0)


class NoteRow(Gtk.ListBoxRow):
    def __init__(self, s):
        Gtk.ListBoxRow.__init__(self)
        self.s = s
        self.label = Gtk.Label(s)
        self.add(self.label)
