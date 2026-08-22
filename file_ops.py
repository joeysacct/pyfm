import subprocess

def copy_files(files, new_dir):
    cmd = ["cp","-r"]
    cmd.extend([str(f.path) for f in files])
    cmd.append(str(new_dir))
    subprocess.run(cmd)
    return 0

def move_files(files, new_dir):
    cmd = ["mv"]
    cmd.extend([str(f.path) for f in files])
    cmd.append(str(new_dir))
    subprocess.run(cmd)
    return 0

def rename_file(filepath, newpath):
    cmd = ["mv"]
    cmd.append(str(filepath))
    cmd.append(str(newpath))
    subprocess.run(cmd)
    return 0

def delete_files(files):
    cmd = ["rm","-r"]
    cmd.extend([str(f.path) for f in files])
    subprocess.run(cmd)
    return 0

def make_dir(dirname):
    cmd = ["mkdir"]
    cmd.append(dirname)
    subprocess.run(cmd)
    return 0
