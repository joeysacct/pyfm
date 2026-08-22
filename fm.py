import curses
import time
from pathlib import Path
from classes import FileItem, Directory
from render import render_file_columns
from file_ops import copy_files, rename_file, move_files, delete_files

        
def get_debounced_key(stdcsr):
    key = curses.ERR
    while True:
        k = stdcsr.getch()
        if k == curses.ERR:
            break
        key = k
    return key


def run_fm(stdcsr):
    initial_path = Path("/home/joeysacct") # TODO make working dir

    framerate = 60.0

    parent_dir = Directory(initial_path.parent)
    current_dir = Directory(initial_path)
    current_dir.get_children()
    current_items = current_dir.child_names
    hovered_item = current_dir.children[0]

    cursor_idx = 0
    selected_file = 0
    selected_indices = set()
    grabbed_files = []

    while True:
        # render file colums

        # handle input
        key = get_debounced_key(stdcsr)

        if key == ord("q"):
            break

        elif key == curses.KEY_UP: # idx up 1
            cursor_idx -= 1
            cursor_idx %= current_dir.num_files

        elif key == curses.KEY_DOWN: # idx down 1
            cursor_idx += 1
            cursor_idx %= current_dir.num_files

        elif key == curses.KEY_LEFT: # change working directory to parent dir
            if len(current_dir.name) > 0:
                selected_indices = set()
                stdcsr.clear()
                cursor_idx = parent_dir.idx_of_entry(current_dir.name)
                current_dir = Directory(current_dir.path.parent)
                current_dir.get_children()
                parent_dir = Directory(current_dir.path.parent)

        elif key == curses.KEY_RIGHT: # change working directory to selected dir, or open file with vim
            if len(str(hovered_item.path)) > 0 and hovered_item.path.is_dir():
                selected_indices = set()
                stdcsr.clear()
                parent_dir = current_dir
                current_dir = Directory(current_dir.path / hovered_item.name)
                current_dir.get_children()
                cursor_idx = 0
            # TODO add file opening support 

        elif key == ord("s"): # select
            # select/deselect file/dir in current dir
            if cursor_idx in selected_indices:
                selected_indices.remove(cursor_idx)
            else:
                selected_indices.add(cursor_idx)
                
        elif key == ord("a"): # select all
            # select/deselect all files/dirs in current dir
            if len(selected_indices) == current_dir.num_files:
                selected_indices = set()
            else:
                selected_indices = set(range(current_dir.num_files))

        elif key == ord("g"): # grab selected
            if len(selected_indices) == 0:
                grabbed_files = [hovered_item]
            else:
                grabbed_files = [current_dir.children[i] for i in selected_indices]

        elif key == ord("r"): # rename
            do_rename(stdcsr, hovered_item)
        elif key == ord("d"): # delete
            # give yes/no prompt to delete files
            if len(selected_indices) > 0:
                do_delete(stdcsr, [current_dir.children[i] for i in selected_indices])
            else:
                do_delete(stdcsr, [hovered_item])
            selected_indices = set()
        elif key == ord("m"): # move
            if len(grabbed_files) > 0:
                do_move(stdcsr, grabbed_files, current_dir, copy=False)
            grabbed_files = []
        elif key == ord("c"):
            if len(grabbed_files) > 0:
                do_move(stdcsr, grabbed_files, current_dir, copy=True)

        if key in map(ord,"rdmc"):
            stdcsr.clear()
            current_dir.refresh_ls()
            current_dir.get_children()
            cursor_idx = 0

        if key is not None: # rerender 
            hovered_item = current_dir.children[cursor_idx]
            render_file_columns(parent_dir, current_dir, stdcsr, hovered_item, cursor_idx, selected_indices, grabbed_files)

        time.sleep(1/framerate)



def do_rename(stdcsr, hovered_item):
    height, width = stdcsr.getmaxyx()
    y,x = (height - 1),0
    
    prompt = curses.newwin(1,width-2,y,x)
    prompt.keypad(True)
    
    msg = "Rename file to: "
    prompt.addstr(0,0,msg)
    prompt.refresh()

    file_to_rename = hovered_item
    buf = str(hovered_item.path)
    curses.curs_set(1)
    while True:
        prompt.addstr(0,len(msg)+1, " "*(len(buf)+1))
        prompt.addstr(0,len(msg)+1, buf[-width - len(msg) - 1:])

        key = prompt.get_wch()
        if key == "\x1b":
            curses.curs_set(0)
            break
        elif key in ("\n", "\r"):
            curses.curs_set(0)
            # handle file rename
            rename_file(hovered_item.path, buf)

            prompt.addstr(0,len(msg)+1, " "*(len(buf)+1))
            prompt.addstr(0,0,f"File renamed to {buf}")
            prompt.refresh()
            time.sleep(1)
            break
        elif key in ("\b", "\x7f", curses.KEY_BACKSPACE):
            buf = buf[:-1]
        elif isinstance(key, str) and key.isprintable():
            buf += key


def do_delete(stdcsr, items):
    height, width = stdcsr.getmaxyx()

    if len(items) < 4:
        filenames = ", ".join([i.name for i in items])
    else:
        filenames = f"{len(items)} files"
    msg = "Delete " + filenames +"? (y/n)"
    
    y,x = (height - 1),0
    
    prompt = curses.newwin(1,width-2,y,x)
    prompt.keypad(True)
    

    prompt.addstr(0,0,msg)
    prompt.refresh()

    buf = ""
    curses.curs_set(1)
    while True:
        prompt.addstr(0,len(msg)+1, " "*(len(buf)+1))
        prompt.addstr(0,len(msg)+1, buf[-width - len(msg) - 1:])

        key = prompt.get_wch()
        if key == "\x1b":
            curses.curs_set(0)
            break
        elif key in ("\n", "\r"):
            if buf.lower() in ["y", "yes"]:
                # handle file delete

                delete_files(items)
                
                # output msg
                prompt.addstr(0,0, " "*(len(buf)+len(msg)+1))
                prompt.addstr(0,0,f"File(s) deleted.")
                prompt.refresh()
                time.sleep(1)
                curses.curs_set(0)
                break
            elif buf.lower() in ["n", "no"]:
                curses.curs_set(0)
                break
            else:
                buf = ""
        elif key in ("\b", "\x7f", curses.KEY_BACKSPACE):
            buf = buf[:-1]
        elif isinstance(key, str) and key.isprintable():
            buf += key



def do_move(stdcsr, items, current_dir, copy=True):
    height, width = stdcsr.getmaxyx()

    filenames = ", ".join([i.name for i in items])
    if len(filenames) > width - 5 - 30:
        filenames = f"{len(items)} files"

    action = "copy " if copy else "move "
    msg = action + filenames + " to this directory? (y/n)"
    
    y,x = (height - 1),0
    
    prompt = curses.newwin(1,width-2,y,x)
    prompt.keypad(True)
    

    prompt.addstr(0,0,msg)
    prompt.refresh()

    buf = ""
    curses.curs_set(1)
    while True:
        prompt.addstr(0,len(msg)+1, " "*(len(buf)+1))
        prompt.addstr(0,len(msg)+1, buf[-width - len(msg) - 1:])

        key = prompt.get_wch()
        if key == "\x1b":
            curses.curs_set(0)
            break
        elif key in ("\n", "\r"):
            if buf.lower() in ["y", "yes"]:

                if copy:
                    copy_files(items, current_dir.path)
                else:
                    move_files(items, current_dir.path)
                
                # output msg
                prompt.addstr(0,0, " "*(len(buf)+len(msg)+1))
                prompt.addstr(0,0,f"File(s) {'copied' if copy else 'moved'}.")
                prompt.refresh()
                time.sleep(1)
                curses.curs_set(0)
                break
            elif buf.lower() in ["n", "no"]:
                curses.curs_set(0)
                break
            else:
                buf = ""
        elif key in ("\b", "\x7f", curses.KEY_BACKSPACE):
            buf = buf[:-1]
        elif isinstance(key, str) and key.isprintable():
            buf += key
