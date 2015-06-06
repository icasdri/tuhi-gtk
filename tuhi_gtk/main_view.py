from gi.repository import Gtk, GObject, GtkSource
from tuhi_gtk.config import get_ui_file

class Handlers:
    def __init__(self, builder):
        self.builder = builder
        self.side_hb = builder.get_object("side_hb")
        self.search_bar = builder.get_object("search_bar")
        self.list = builder.get_object("list")
        print(builder.get_objects())
        self._hb_synced_width = 0

    def synchronize_hb_size_callback(self, widget, allocation):
        if allocation.width != self._hb_synced_width:
            self.side_hb.set_size_request(allocation.width+2, -1)
            # hb_alloc = self.side_hb.get_allocation()
            # hb_alloc.width = allocation.width + 2
            # self.side_hb.set_allocation(hb_alloc)
            self._hb_synced_width = allocation.width
            # TODO: TESTING ONLY: Debug size allocation print statements
            print(allocation.width, self.side_hb.get_allocation().width)

    def toggle_search(self, toggle_button):
        self.search_bar.set_search_mode(toggle_button.get_active())


def get_window():
    GObject.type_register(GtkSource.View)
    builder = Gtk.Builder.new_from_file(get_ui_file("main_window"))
    builder.connect_signals(Handlers(builder))
    from tuhi_gtk.windows import _testing_only_list_elements
    _testing_only_list_elements(builder.get_object("list"), test_spinners=True)
    window = builder.get_object("main_window")
    window.connect("delete-event", Gtk.main_quit)
    return window

