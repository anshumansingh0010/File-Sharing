import gi
import os
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Pango
from backend import Sender

class SenderPage(Adw.Bin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.selected_files = []
        self.selected_folders = []

        # Use Adw.Clamp to restrict the width of the content area
        self.clamp = Adw.Clamp()
        self.clamp.set_maximum_size(450)
        self.clamp.set_tightening_threshold(300)
        self.set_child(self.clamp)

        # Main Layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.main_box.set_valign(Gtk.Align.CENTER)
        self.main_box.set_vexpand(True)
        self.main_box.set_hexpand(True)
        self.main_box.add_css_class("main-container")
        self.clamp.set_child(self.main_box)

        # Large Icon
        self.icon = Gtk.Image.new_from_icon_name("mail-send-symbolic")
        self.icon.set_pixel_size(128)
        self.icon.add_css_class("big-icon")
        self.main_box.append(self.icon)

        # Title
        self.title_lbl = Gtk.Label(label="Send File")
        self.title_lbl.add_css_class("title-label")
        self.main_box.append(self.title_lbl)

        # Description
        self.desc_lbl = Gtk.Label(label="Select the file or directory to send")
        self.desc_lbl.add_css_class("description-label")
        self.main_box.append(self.desc_lbl)

        # Status Label
        self.lbl_status = Gtk.Label(label="No files selected")
        self.lbl_status.set_margin_bottom(5)
        self.main_box.append(self.lbl_status)

        # Selection List (Scrolled)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_min_content_height(150)
        self.scrolled_window.set_min_content_width(350)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_visible(False) # Hide if empty
        self.main_box.append(self.scrolled_window)

        self.selection_list = Gtk.ListBox()
        self.selection_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.selection_list.add_css_class("selection-list")
        self.scrolled_window.set_child(self.selection_list)

        # Select File Button
        self.btn_select_file = Gtk.Button(label="Select File")
        self.btn_select_file.add_css_class("primary-button")
        self.btn_select_file.add_css_class("accent")
        self.btn_select_file.add_css_class("suggested-action")
        self.btn_select_file.set_halign(Gtk.Align.CENTER)
        self.btn_select_file.set_size_request(260, -1)
        self.btn_select_file.connect("clicked", self.on_select_file_clicked)
        self.main_box.append(self.btn_select_file)

        # Select Folder Button
        self.btn_select_folder = Gtk.Button(label="Select Folder")
        self.btn_select_folder.add_css_class("secondary-button")
        self.btn_select_folder.set_halign(Gtk.Align.CENTER)
        self.btn_select_folder.set_size_request(260, -1)
        self.btn_select_folder.connect("clicked", self.on_select_folder_clicked)
        self.main_box.append(self.btn_select_folder)

        # Send Files Button
        self.btn_send = Gtk.Button(label="Send Files")
        self.btn_send.add_css_class("primary-button")
        self.btn_send.add_css_class("accent")
        self.btn_send.add_css_class("suggested-action")
        self.btn_send.set_margin_top(20)
        self.btn_send.set_sensitive(False)
        self.btn_send.set_halign(Gtk.Align.CENTER)
        self.btn_send.set_size_request(290, -1)
        self.btn_send.connect("clicked", self.on_send_clicked)
        self.main_box.append(self.btn_send)

    def on_select_file_clicked(self, button):
        dialog = Gtk.FileDialog(title="Select files to send")
        
        # Add file filter to exclude folders (though open_multiple usually does this)
        all_files_filter = Gtk.FileFilter()
        all_files_filter.set_name("All Files")
        all_files_filter.add_pattern("*")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(all_files_filter)
        dialog.set_filters(filters)

        native = self.get_native()
        parent = native if isinstance(native, Gtk.Window) else None
        dialog.open_multiple(parent, None, self.on_files_selected)

    def on_select_folder_clicked(self, button):
        dialog = Gtk.FileDialog(title="Select folders to send")
        native = self.get_native()
        parent = native if isinstance(native, Gtk.Window) else None
        dialog.select_multiple_folders(parent, None, self.on_folders_selected)

    def add_item_to_list(self, path):
        is_dir = os.path.isdir(path)
        
        # Check for duplicates in the respective list
        if is_dir:
            if path in self.selected_folders:
                return
            self.selected_folders.append(path)
        else:
            if path in self.selected_files:
                return
            self.selected_files.append(path)
        
        row_content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row_content.set_margin_start(10)
        row_content.set_margin_end(10)
        row_content.set_margin_top(5)
        row_content.set_margin_bottom(5)

        icon_name = "folder-symbolic" if is_dir else "text-x-generic-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name)
        row_content.append(icon)

        label = Gtk.Label(label=os.path.basename(path))
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        row_content.append(label)

        remove_btn = Gtk.Button.new_from_icon_name("window-close-symbolic")
        remove_btn.add_css_class("flat")
        
        # We wrap the content in a ListBoxRow explicitly to easily remove it
        row = Gtk.ListBoxRow()
        row.set_child(row_content)
        
        remove_btn.connect("clicked", self.on_remove_item_clicked, path, is_dir, row)
        row_content.append(remove_btn)

        self.selection_list.append(row)
        self.update_ui_state()

    def on_remove_item_clicked(self, button, path, is_dir, row_widget):
        if is_dir:
            if path in self.selected_folders:
                self.selected_folders.remove(path)
        else:
            if path in self.selected_files:
                self.selected_files.remove(path)
        
        # Explicitly remove and destroy the row
        self.selection_list.remove(row_widget)
        self.update_ui_state()

        return False

    def update_ui_state(self):
        file_count = len(self.selected_files)
        folder_count = len(self.selected_folders)
        total_count = file_count + folder_count

        if total_count == 0:
            self.lbl_status.set_label("No files selected")
            self.scrolled_window.set_visible(False)
            self.btn_send.set_sensitive(False)
        else:
            status_text = []
            if file_count > 0:
                status_text.append(f"{file_count} file(s)")
            if folder_count > 0:
                status_text.append(f"{folder_count} folder(s)")
            
            self.lbl_status.set_label(f"Selected: {', '.join(status_text)}")
            self.scrolled_window.set_visible(True)
            self.btn_send.set_sensitive(True)

    def on_send_clicked(self, button):
        print(f"Sending Files: {self.selected_files}")
        print(f"Sending Folders: {self.selected_folders}")
        
        # Implementation for sending 
        user_sender=Sender(2121,*(self.selected_files))
        user_sender.start()
        
        self.lbl_status.set_label("Sending started...")

    def on_files_selected(self, dialog, result):
        try:
            files_list = dialog.open_multiple_finish(result)
            if files_list:
                count = files_list.get_n_items()
                for i in range(count):
                    file = files_list.get_item(i)
                    self.add_item_to_list(file.get_path())
        except Exception as e:
            print(f"File selection failed: {e}")

    def on_folders_selected(self, dialog, result):
        try:
            folders_list = dialog.select_multiple_folders_finish(result)
            if folders_list:
                count = folders_list.get_n_items()
                for i in range(count):
                    folder = folders_list.get_item(i)
                    self.add_item_to_list(folder.get_path())
        except Exception as e:
            print(f"Folder selection failed: {e}")
