class Note:
    def __init__(self, title=None):
        self.title = title
        self.data = ""


class NotesDB:
    def __init__(self, db_url, server_url):
        # TODO: TESTING ONLY: fake note data
        fake_note_data = [
            "Test Note", "My little pony", "Canes Chicken",
            "Test Note 2", "Random Crap", "Welcome to Tuhi",
            "More Stuff", "Cool things!", "Blah blah blah",
            "Untitled", "Some cool note", "My not-so-little pony",
            "More and more stuff", "Hello world", "The language",
            "Blah blah blah blah blah blah blah blah blah"
        ]
        self.notes = {i: Note(j) for i, j in enumerate(fake_note_data)}

    def get_note(self, note_id):
        return self.notes[note_id]

db = NotesDB("", "")
