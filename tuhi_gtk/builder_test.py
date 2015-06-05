from gi.repository import Gtk
from tuhi_gtk.main_view import get_window

def main():
    get_window().show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
