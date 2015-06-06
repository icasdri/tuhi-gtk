from pkg_resources import resource_filename
import os.path

DATA_BASEDIR = ""
UI_BASEDIR = os.path.join(DATA_BASEDIR, "ui")
UI_EXTENSION = ".xml"

def get_ui_file(ui_name):
    return resource_filename(__name__, os.path.join(UI_BASEDIR, ui_name + UI_EXTENSION))
