import stat
import pwd
import grp
import subprocess
from pathlib import Path
import datetime

class Directory:
    def __init__(self, absolute_path: Path):
        self.name = absolute_path.stem
        self.path = absolute_path
        st = absolute_path.stat()
        self.size = st.st_size
        self.timestamp = st.st_mtime
        self.rwx_perms = stat.filemode(st.st_mode)
        self.refresh_ls()

    def refresh_ls(self):
        self.ls_data = []
        raw_ls_data = subprocess.run(["ls", "-lh", self.path], capture_output=True).stdout.decode('utf-8').split("\n")
        for entry in raw_ls_data:
            if entry.startswith("total") or len(entry) == 0:
                continue
            self.ls_data.append(entry)

    def view(self, width):
        output = []
        for entry in self.ls_data:
            rwx_props,_,owner,group,size,month,day,timestamp,name = entry.split(maxsplit=8)
            if entry.startswith("d"):
                starting_chr = "🗀 "
            elif entry.startswith("l"):
                continue
            elif entry.startswith("-"):
                starting_chr = "🖹 "
            else:
                continue

            # name handling
            if len(name)+1 > width:
                filetype = name.split(".")[-1]
                if filetype != name:
                    stop_idx = width - len(filetype) - len(starting_chr) - 2
                    output.append(starting_chr + name[:stop_idx] + "…." + filetype)
                else:
                    stop_idx = width - len(starting_chr) - 2
                    output.append(starting_chr + name[:stop_idx] + "…"  )
            else:
                output.append(starting_chr + name)

        return output
        

    def get_children(self):
        self.children = []
        self.child_names = []
        # make a hash of name to object
        for entry in self.ls_data:
            rwx_props,_,owner,group,size,month,day,timestamp,name = entry.split(maxsplit=8)
            item_path = self.path / name

            if rwx_props.startswith("d"):
                # make directory object
                self.children.append(Directory(item_path))
                self.child_names.append(name)
            elif rwx_props.startswith("l"):
                continue
            elif rwx_props.startswith("-"):
                # make FileItem object
                self.children.append(FileItem(item_path))
                self.child_names.append(name)
            else:
                continue
        if len(self.children) == 0:
            self.children = [FileItem("")]
        self.num_files = len(self.child_names)


    def idx_of_entry(self, entry_name):
        names = [e.split(maxsplit=8)[-1] for e in self.ls_data]
        for idx, name in enumerate(names):
            if name == entry_name:
                return idx
        raise ValueError(",".join(names) + "\n\n'" + entry_name + "'")
        return 0



class FileItem:
    def __init__(self, absolute_path: Path):
        if absolute_path != "":
            self.name = absolute_path.name
            self.path = absolute_path
            st = absolute_path.stat()
            self.size = st.st_size
            self.timestamp = datetime.datetime.fromtimestamp(st.st_mtime)
            self.rwx_perms = stat.filemode(st.st_mode)
        else:
            self.name = "None"
            self.size = 0
            self.path = ""
            self.timestamp = datetime.datetime.now()
            self.rwx_perms = ''

            
    def view(self, max_width):
        filetype = self.name.split(".")[-1] or "unknown"
        out = [
            "Name: " + self.name,
            "Type: " + filetype,
            "Size: " + str(self.size),
            "Modified: " + self.timestamp.strftime('%d %b %Y, %I:%M %p')
        ]
        if len(str(self.path))>0:
            with open(self.path, 'rb') as f:
                chunk = f.read(8192)
            if b'\x00' in chunk:
                return out
            try:
                filedata = [o[:max_width] for o in chunk.decode('utf-8').split("\n")]
                out.append(" ")
                out.append("Content:")
                out.append("-"*max_width)
                out.extend(filedata)
                return out
            except:
                return out
        return ""

