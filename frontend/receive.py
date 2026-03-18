import threading
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class ReceivePage(Adw.Bin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main Layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.set_valign(Gtk.Align.CENTER)
        self.main_box.set_halign(Gtk.Align.CENTER)
        self.main_box.add_css_class("main-container")
        self.set_child(self.main_box)

        # Large Icon
        self.icon = Gtk.Image.new_from_icon_name("folder-download-symbolic")
        self.icon.set_pixel_size(128)
        self.icon.add_css_class("big-icon")
        self.main_box.append(self.icon)

        # Title
        self.title_lbl = Gtk.Label(label="Receive File")
        self.title_lbl.add_css_class("title-label")
        self.main_box.append(self.title_lbl)

        # Description
        self.desc_lbl = Gtk.Label(label="Enter the transmit code from the sender")
        self.desc_lbl.add_css_class("description-label")
        self.main_box.append(self.desc_lbl)

        # Transmit Code Entry
        self.code_entry = Gtk.Entry()
        self.code_entry.set_placeholder_text("Transmit Code")
        self.code_entry.set_halign(Gtk.Align.CENTER)
        self.code_entry.set_width_chars(30)
        self.code_entry.add_css_class("code-entry")
        # self.code_entry.connect("")
        self.main_box.append(self.code_entry)
        # Receive File Button
        self.btn_receive = Gtk.Button(label="Receive File")
        self.btn_receive.add_css_class("primary-button")
        self.btn_receive.add_css_class("accent")
        self.btn_receive.add_css_class("suggested-action")
        self.btn_receive.set_size_request(250, -1)
        self.btn_receive.connect("clicked", self.on_receive_clicked)
        self.main_box.append(self.btn_receive)
        self.recieve_event=threading.Event()
        
    def get_otp(self):
        return self.code

    def on_receive_clicked(self, button):
        self.code = self.code_entry.get_text()
        self.recieve_event.set()

    def reset(self):
        """Clear the entry and reset the event so a new session can start."""
        self.code_entry.set_text("")
        self.recieve_event.clear()