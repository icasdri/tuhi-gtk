from gi.repository import Gtk
from tuhi_gtk.windows import MainWindow

def main():
    window = MainWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()