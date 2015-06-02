from gi.repository import Gtk, GtkSource

TITLE = "Tuhi"

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=TITLE)

        # Header Bar
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.hb.props.title = TITLE
        self.set_titlebar(self.hb)

        # Main Layout
        self.grid = Gtk.Table(1, 2, False)
        self.add(self.grid)

        self.list = Gtk.ListBox()
        self.list.set_size_request(20, 20)
        self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)

        a = NoteRow("Test Note")
        b = NoteRow("My little pony")
        c = NoteRow("Canes Chicken")
        self.list.add(a)
        self.list.add(b)
        self.list.add(c)

        self.grid.attach(self.list, 0, 1, 0, 1)

        self.source_view = GtkSource.View()
        self.grid.attach(self.source_view, 1, 2, 0, 1)


class NoteRow(Gtk.ListBoxRow):
    def __init__(self, s):
        Gtk.ListBoxRow.__init__(self)
        self.s = s
        self.label = Gtk.Label(s)
        self.add(self.label)
