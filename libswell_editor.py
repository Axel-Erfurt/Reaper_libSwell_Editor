#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from datetime import datetime
import shutil
from sys import argv

if len(argv) > 1:
    libswell_file = argv[1]
else:
    libswell_file = f"{GLib.get_user_config_dir()}/REAPER/libSwell.colortheme"
#libswell_file = "/tmp/libSwell.colortheme"
print(f"loading {libswell_file}")

now = datetime.now().strftime("%Y-%m-%d-%H-%M")
backup_file = f"{GLib.get_user_config_dir()}/REAPER/libSwell.colortheme_{now}"
print(f"creating backup {backup_file}")

shutil.copy(libswell_file, backup_file, follow_symlinks=True)

class TreeWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="libSwell Editor")

        self.set_name("mywindow")
        self.set_border_width(4)
        self.column_count = 0
        self.is_changed = False
        self.connect("delete-event", self.on_close)
        self.editable = False
        self.selected_row = 0
        
         # box
        self.vbox = Gtk.Box(orientation=1, vexpand=True)
        self.add(self.vbox)
        
        self.hbox = Gtk.Box(orientation=0)
        
        # save button
        self.btn_save = Gtk.Button.new_from_icon_name("document-save", 2)
        self.btn_save.set_name("btn_save")
        self.btn_save.set_tooltip_text("Save current File")
        self.btn_save.set_hexpand(False)
        self.btn_save.set_relief(2)
        self.btn_save.connect("clicked", self.on_save_file)
        
        self.hbox.pack_start(self.btn_save, False, False, 1)
        
        # color button
        self.btn_color = Gtk.ColorButton()
        self.btn_color.set_name("btn_color")
        self.btn_color.set_tooltip_text("change color")
        self.btn_color.set_hexpand(False)
        self.btn_color.set_relief(2)
        self.btn_color.set_sensitive(False)
        
        self.hbox.pack_start(self.btn_color, False, False, 1)
        
        # activate / deactivate button
        self.btn_active = Gtk.Button.new_from_icon_name("answer", 4)
        self.btn_active.set_tooltip_text("activate / deactivate")
        self.btn_active.set_hexpand(False)
        self.btn_active.set_relief(2)
        self.btn_active.connect("clicked", self.on_deactivate)
        
        self.hbox.pack_start(self.btn_active, False, False, 1)
        
        # entry int
        self.btn_entry_int = Gtk.SpinButton.new_with_range(0.0, 99.0, 1.0)
        self.btn_entry_int.set_numeric(True)
        self.btn_entry_int.set_tooltip_text("edit value")
        self.btn_entry_int.set_hexpand(False)
        self.btn_entry_int.connect("value-changed", self.on_change_int)
        
        self.hbox.pack_end(self.btn_entry_int, False, False, 1)
        
        # font selector
        self.btn_font_selector = Gtk.FontButton.new()
        self.btn_font_selector.set_tooltip_text("edit font")
        self.btn_font_selector.set_hexpand(False)
        self.btn_font_selector.connect("font-set", self.on_font_selector)
        
        self.hbox.pack_end(self.btn_font_selector, False, False, 1)
       
        # label
        self.sub_title_label = Gtk.Label(label="Info")
        self.sub_title_label.set_name("sublabel")
        self.hbox.pack_start(self.sub_title_label, True, False, 1)
        
        self.vbox.pack_start(self.hbox, False, False, 1)

        # treeview
        self.treeview = Gtk.TreeView()
        self.treeview.set_name("csv-view")
        self.treeview.set_grid_lines(3)
        self.treeview.set_activate_on_single_click(False)
        self.treeview.connect("row-activated", self.onSelectionChanged)
        self.treeview.connect("button-release-event", self.on_pressed)

        self.my_treelist = Gtk.ScrolledWindow()
        self.my_treelist.add(self.treeview)
        self.vbox.pack_end(self.my_treelist, True, True, 5)
        
        self.load_into_table(libswell_file)
 
    def maybe_saved(self, *args):
        print("is modified", self.is_changed)
        md = Gtk.MessageDialog(title="libSwell Editor", message_type=Gtk.MessageType.QUESTION, 
                                text="The document was changed.\n\nSave changes?", 
                                parent=None)
        md.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
             "Yes", Gtk.ResponseType.YES, "No", Gtk.ResponseType.NO)
        response = md.run()
        if response == Gtk.ResponseType.YES:
            ### save
            self.on_save_file()
            md.destroy()
            return False
        elif response == Gtk.ResponseType.NO:
            md.destroy()
            return False
        elif response == Gtk.ResponseType.CANCEL:
            md.destroy()
            return True
        md.destroy()
        
    def on_close(self, *args):
        print("goodbye ...")
        print(f"{libswell_file} changed: {self.is_changed}")
        if self.is_changed:
            b = self.maybe_saved()
            print (f"close: {b}")
            if b: 
                return True
            else:
                Gtk.main_quit()
        else:
            Gtk.main_quit()
            
    def on_deactivate(self, *args):
        model, pathlist = self.treeview.get_selection().get_selected()
        if pathlist:
            value = model[pathlist][0]
            if not value.startswith(";"):
                model[pathlist][0] = f";{value}"
            else:
                model[pathlist][0] = value[1:]
            self.is_changed = True
            
    def on_change_int(self, *args):
        model, pathlist = self.treeview.get_selection().get_selected()
        if pathlist:
            value = model[pathlist][1]
            if value.isnumeric():
                model[pathlist][1] = self.btn_entry_int.get_text()
                self.is_changed = True
            
    def on_font_selector(self, *args):
        self.treeview.set_cursor(0)
        model, pathlist = self.treeview.get_selection().get_selected()
        if pathlist:
            size = self.btn_font_selector.get_font().split(" ")[-1]
            name = self.btn_font_selector.get_font().rpartition(" ")[0]
            model[pathlist][1] = name
            self.treeview.set_cursor(1)
            model, pathlist = self.treeview.get_selection().get_selected()
            model[pathlist][1] = size
            self.is_changed = True
        
        

    def on_pressed(self, trview, event):
        if event.button == 1 and event.type == Gdk.EventType.BUTTON_RELEASE:
            model, pathlist = self.treeview.get_selection().get_selected()
            if pathlist:
                model, iter = self.treeview.get_selection().get_selected()
                self.selected_row = model.get_path(iter)
                value = model[pathlist][1]
                if value.startswith("#"):
                    color = Gdk.RGBA()
                    color.parse(value)
                    self.btn_color.set_rgba(color)
                if value.isnumeric():
                    self.btn_entry_int.set_value(float(model[pathlist][1]))
                else:
                    self.btn_entry_int.set_value(0)
        
    def onSelectionChanged(self, trview, event, *args):
        model, pathlist = self.treeview.get_selection().get_selected()
        if pathlist:
            value = model[pathlist][1]
            if value.startswith("#"):
                color = Gdk.RGBA()
                color.parse(value)
                self.btn_color.set_rgba(color)
                
                cld = Gtk.ColorChooserDialog(show_editor = False)
                cld.set_rgba(color)
                
                if cld.run() == Gtk.ResponseType.OK:
                    color = cld.get_rgba()
                    r = int(color.red * 255)
                    g = int(color.green * 255)
                    b = int(color.blue * 255)
                    new_color = self.rgb2hex(r, g, b)
                    model[pathlist][1] = f"#{new_color}"
                    self.btn_color.set_rgba(color)
                    self.is_changed = True
                    cld.close()
                else:
                    cld.close()



    def rgb2hex(self, r, g, b):
        def rgb(c):
            if c < 0: return 0
            if c > 255 : return 255
            return c
            
        r = rgb(r)
        g = rgb(g)
        b = rgb(b)
         
        val = "%02x%02x%02x" % (r, g, b)
        return(val.upper())
        
                
    def load_into_table(self, csv_file, *args):
        for column in self.treeview.get_columns():
            self.treeview.remove_column(column)
        my_list = []
        my_csv = open(csv_file, 'r').read().splitlines()
        self.column_count = 2
        self.my_liststore = Gtk.ListStore(str, str)

        renderer = Gtk.CellRendererText()
        renderer.set_property('editable', False)
        column = Gtk.TreeViewColumn("Description", renderer, text=0)
        column.colnr = 0
        self.treeview.append_column(column)
        
        renderer = Gtk.CellRendererText()
        renderer.set_property('editable', False)
        column = Gtk.TreeViewColumn("Value", renderer, text=1)
        column.colnr = 1
        self.treeview.append_column(column)

        for lines in my_csv:
            if " ; defaults to" in lines:
                lines = lines.split(" ; defaults to")[0]
            if lines.startswith("; "):
                lines = lines.replace("; ", ";", 1)
                line = lines.split(" ", 1)
            else:
                line = lines.split(" ", 1)
            col_1 = line[0]
            col_2 = line[1]
            
            my_list.append([f"{col_1}", col_2])     
                
        for line_value in my_list:
            self.my_liststore.append(list(line_value))
                 
        self.treeview.set_model(self.my_liststore)
        self.sub_title_label.set_text(csv_file)
        self.is_changed = False
        
        tree_iter = self.my_liststore.get_iter(0)
        font = self.my_liststore.get_value(tree_iter, 1)
        tree_iter = self.my_liststore.get_iter(1)
        font_size = self.my_liststore.get_value(tree_iter, 1)
        self.btn_font_selector.set_font(f"{font} {font_size}")

    def on_save_file(self, *args):
            # model to  text file
            list_string = []        
            for node in self.my_liststore:
                d = []
                for column in range(self.column_count):
                    the_node = node[column]
                    if the_node == None:
                        the_node = ""
                    d.append(the_node)
                list_string.append(d)
            with open(libswell_file, 'w') as f:
                for line in list_string:
                    value = " ".join(line)
                    f.write(f'{value}\n')   
                self.is_changed = False

        
###############################################
win = TreeWindow()
win.connect("destroy", Gtk.main_quit)
win.set_size_request(500, 500)
win.move(0, 0)
win.show_all()
win.resize(700, 700)
Gtk.main()