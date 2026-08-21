import curses
import subprocess
import numpy as np
import time
from pathlib import Path


class FileItem:
    def __init__(self, ls_entry):
        rwx_props,_,owner,group,size,month,day,timestamp,filename = ls_entry.split()
        self.rwx_props = rwx_props
        self.filename = filename
        self.name = filename # TODO add formatting here?
        self.timestamp = month + day + timestamp
        self.size = size
        if rwx_props.startswith("d"):
            self.type = "dir"
        elif rwx_props.startswith("l"):
            self.type = "link"
        elif rwx_props.startswith("-"):
            self.type = "file"
        else:
            self.type = "unhandled"


    def file_preview(self):
        filetype = self.name.split(".")[-1] or "unknown"
        try:
            path.read_text(encoding="utf-8")
            # cat out text file data
            return subprocess.run(["head", "-10", self.name], capture_output=True)
        except (UnicodeDecodeError, OSError):
            return f"{filetype} file"
            


class MenuData:
    def __init__(self, current_dir):
        self.num_files = 0 # number of entries in working dir
        self.working_dir_data = []
        self.parent_dir_data = []
        self.preview = []
        self.change_dir(current_dir)


    def change_dir(self, new_dir):
        self.working_dir_data = self.dir_data(new_dir)
        self.num_files = len(self.working_dir_data)
        self.parent_dir_data = self.dir_data(new_dir.parent)
        self.update_preview(0) # start at first item

    
    def update_preview(self, item_idx):
        child_item = self.working_dir_data[item_idx]
        item_type = child_item.type
        if item_type == "dir":
            dir_info = dir_data(new_dir / child_item.name)
            self.preview = "\n".join([item.name for item in dir_info])
        elif item_type == "file":
            self.preview = child_item.file_preview()
        else:
            self.preview = []


    def dir_data(self, dir_name):
        ls_data = subprocess.run(["ls", "-lh", dir_name], capture_output=True).stdout.decode('utf-8')
        entries = []

        # raise ValueError(ls_data)
        for entry in ls_data.split("\n"):
            if entry.startswith("total"):
                continue
            entries.append(FileItem(entry))
            
        if len(entries) > 0:
            return entries
        return [FileItem("--------- 0 none none 0.0B Jan 1 00:00 Empty")]
            
        



def run_fm(stdcsr):
    working_dir = Path("/home/joeysacct") # TODO make working dir
    current_dir = working_dir

    framerate = 20.0
    menu_data = MenuData(current_dir)

    cursor_idx = 0
    selected_indices = []
    while True:
        # render file colums
        render_file_columns(menu_data, stdcsr)

        # handle input
        scroll_modulus = max(menu_data.num_files,1)
        key = stdcsr.getch()

        if key == ord("q"):
            break
        elif key == curses.KEY_UP: # idx up 1
            cursor_idx -= 1
            cursor_idx %= scroll_modulus
            menu_data.update_preview(cursor_idx)
        elif key == curses.KEY_DOWN: # idx down 1
            cursor_idx += 1
            cursor_idx %= scroll_modulus
            menu_data.update_preview(cursor_idx)
        elif key == curses.KEY_LEFT: # change working directory to parent dir
            menu_data.change_dir(current_dir.parent)
        elif key == curses.KEY_RIGHT: # change working directory to selected dir, or open file with vim
            new_dir_name = menu_data.working_dir_data[cursor_idx].name
            menu_data.change_dir(current_dir / new_dir_name)

        elif key == ord("s"): # select
            # select/deselect file/dir in current dir
            print("")
        elif key == ord("a"): # select all
            # select/deselect all files/dirs in current dir
            print("")
        elif key == ord("d"): # delete
            # give yes/no prompt to delete flie
            print("")
        elif key == ord("m"): # move
            # give prompt for directory to move the file to, then cut+paste it there
            print("")
        elif key == ord("x"): # cut
            # cut file
            print("")
        elif key == ord("c"): # copy
            # copy file
            print("")
        elif key == ord("p"): # paste
            # paste file
            print("")

        time.sleep(1/framerate)


def render_file_columns(menu_data, stdcsr):
    width, height = stdcsr.getmaxyx()

    col_locations = np.round(width*np.array([0.125, 0.625])).astype(int)

    # place bars
    for h in range(height):
        for w in col_locations:
            try:
                stdcsr.addstr(h,w,"|")
            except:
                pass

    # place parent dir view
    for h,fileitem in enumerate(menu_data.parent_dir_data):
        stdcsr.addstr(h,0,fileitem.name)

    # place current dir view
    w = col_locations[0] + 1
    for h,fileitem in enumerate(menu_data.working_dir_data):
        stdcsr.addstr(h,w,fileitem.name)

    # place preview
    w = col_locations[1] + 1
    for line in menu_data.preview:
        stdcsr.addstr(0,w,line)

