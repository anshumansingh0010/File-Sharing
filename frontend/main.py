import gi
import os
import threading
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, GLib
from frontend.send import SenderPage
from frontend.receive import ReceivePage
from backend import Receiver

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(450, 800)
        self.set_title("File Transfer")

        # ToolbarView
        self.toolbar_view = Adw.ToolbarView()
        self.set_content(self.toolbar_view)

        # Header Bar
        self.header_bar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header_bar)

        # View Stack as the main content
        self.view_stack = Adw.ViewStack()
        self.view_stack.connect("notify::visible-child-name", self.on_view_changed)
        
        self.view_switcher = Adw.ViewSwitcher()
        self.view_switcher.set_stack(self.view_stack)
        self.view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        self.header_bar.set_title_widget(self.view_switcher)

        # Add Pages
        self.sender_page = SenderPage()
        self.receive_page = ReceivePage()

        self.view_stack.add_titled_with_icon(
            self.sender_page, 
            "sender", 
            "Send", 
            "mail-send-symbolic"
        )
        self.view_stack.add_titled_with_icon(
            self.receive_page, 
            "receive", 
            "Receive", 
            "folder-download-symbolic"
        )

        self.toolbar_view.set_content(self.view_stack)
        
    def on_view_changed(self,stack,pspec):
        current_page=stack.get_visible_child_name()
        if current_page == "receive":
            self.sender_page.stop_search()
            self.receiver_stop_signal=threading.Event()
            user_receiver_thread=threading.Thread(target=self.receiver_thread,args=(self.receiver_stop_signal,),daemon=True)
            user_receiver_thread.start()
        elif current_page == "sender":
            self.receiver_stop_signal.set()
            self.sender_page.start_search()
            
    def get_otp(self):
        while not self.receive_page.recieve_event.is_set():
            pass
        self.receive_page.recieve_event.clear()
        return   self.receive_page.get_otp()   
    def receiver_thread(self):
        try:
            user_receiver = Receiver()
            user_receiver.start(self.get_otp)
            # All files received — show the completion dialog on the main thread
            GLib.idle_add(self.show_receive_complete_dialog)
        except Exception as e:
            print(f"Receiver error: {e}")

    def show_receive_complete_dialog(self):
        dialog = Adw.AlertDialog(
            heading="Transfer Complete",
            body="All files have been received successfully.",
        )
        dialog.add_response("send", "Send")
        dialog.add_response("receive_again", "Receive Again")
        dialog.set_response_appearance("send", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_response_appearance("receive_again", Adw.ResponseAppearance.SUGGESTED)
        dialog.add_css_class("complete-dialog")
        dialog.set_default_response("receive_again")
        dialog.connect("response", self.on_receive_complete_response)
        dialog.present(self)
        return GLib.SOURCE_REMOVE

    def on_receive_complete_response(self, dialog, response):
        if response == "receive_again":
            # Reset the receive page UI and start listening again
            self.receive_page.reset()
            new_thread = threading.Thread(target=self.receiver_thread, daemon=True)
            new_thread.start()
        elif response == "send":
            # Switch to the Send tab
            self.view_stack.set_visible_child_name("sender")
              

class FileTransferApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.anshuman.FileSharing",
                         flags=Gio.ApplicationFlags.NON_UNIQUE)

    def do_startup(self):
        Adw.Application.do_startup(self)
        
        # Load CSS at application level
        self.load_css()

        # AdwStyleManager handles the theme scheme automatically.
        style_manager = self.get_style_manager()
        style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        css_provider.load_from_path(css_path)
        
        # In GTK 4, use Gdk.Display.get_default()
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()