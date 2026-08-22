import curses
from pathlib import Path
from classes import FileItem, Directory
import numpy as np

def render_file_columns(parent_dir, current_dir, stdcsr, hovered_item, cursor_idx, selected_indices, grabbed_files):
    height, width = stdcsr.getmaxyx()
    max_count = height-2
    if cursor_idx > max_count-5:
        start_idx = cursor_idx - max_count + 5
    else:
        start_idx = 0
    end_idx =  start_idx + max_count

    col_locations = np.round(width*np.array([0.125, 0.625])).astype(int)

    # place bars
    for h in range(height):
        for w in col_locations:
            try:
                stdcsr.addstr(h,w,"|")
            except:
                pass

    stdcsr.addstr(0,0,parent_dir.name, curses.color_pair(5))
    max_length = col_locations[0] - 1
    # place parent dir view
    for h,line in enumerate(parent_dir.view(max_length)[:max_count]):
        stdcsr.addstr(h+2,1,line)

    # place current dir view
    w = col_locations[0] + 1
    stdcsr.addstr(0,w,current_dir.path.as_posix(), curses.color_pair(5))
    max_length = col_locations[1] - col_locations[0] - 1
    for h in range(max_count):
        stdcsr.addstr(h+2,w," "*(max_length))
    for h,line in enumerate(current_dir.view(max_length)[start_idx:end_idx]):
        if h + start_idx == cursor_idx:
            color = 3
        elif h + start_idx in selected_indices:
            color = 5
        else:
            color = 1

        try:
            stdcsr.addstr(h+2,w,line, curses.color_pair(color))
        except:
            raise ValueError(str(h) + fileitem.name + str(height))

    # place preview
    w = col_locations[1] + 1
    max_length = width - col_locations[1] - 1
    lines = hovered_item.view(max_length)
    for h in range(max_count-1):
        stdcsr.addstr(h,w," "*(max_length))
        if h < len(lines):
            stdcsr.addstr(h,w,lines[h][:max_length-2])


    # place grabbed file corner
    if len(grabbed_files) > 0:
        files = grabbed_files[:10]
        msg = ["Grabbed "+str(len(grabbed_files))+" Files:"]
        msg.extend([f.name for f in files])
        
        h_range = range(height-len(msg)-2, max_count)
        if len(grabbed_files) > 10:
            msg[-1] = "..."
        for h in h_range:
            stdcsr.addstr(h+1,w," "*max_length)
        for h,line in zip(h_range,msg):
            stdcsr.addstr(h+1,w,line[:max_length])

