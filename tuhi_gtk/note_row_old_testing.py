from gi.repository import Gtk, GtkSource, GObject, Gdk, Gio
from tuhi_gtk.note_row_view import NoteRow

TITLE = "Tuhi"
MARGIN = 4

# TODO: TESTING ONLY: Some NoteRow stubs for UI lnf testing before real logic
def _testing_only_list_elements(list_, test_spinners=False):
    for i in range(16):
        x = NoteRow.get_note_row(i)
        list_.add(x)

        # if test_spinners:
        #     def gen_callback(note_row):
        #         def callback():
        #             if random.choice((True, False, False)):
        #                 note_row.spinner_start()
        #             else:
        #                 note_row.spinner_stop()
        #             return True
        #         return callback
        #
        #     GObject.timeout_add(2000, gen_callback(x))
        x.spinner_start()


class NoteRowOld(Gtk.ListBoxRow):
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

        # self.set_size_request(-1, 35)

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
