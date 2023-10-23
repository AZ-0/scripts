from zipfile import ZipFile
from io import BytesIO
import os

NAME = 'coined'       # Name of the smuggler file (the one that is copied by Docker)
MAIN = 'proxy.sh'     # Name of the file that should be run after the extractor
WRAPPED = 'wrapped'   # Name of the directory containing the smuggled files
MAX_SHELL_SIZE = 256  # Max size of the shell extractor, in bytes

os.chdir(WRAPPED)
with ZipFile(pack := BytesIO(), 'w') as zip:
    for file in os.listdir('.'):
        zip.write(file)
os.chdir('..')
data = pack.getvalue()
pack.close()

with open('unzip', 'rb') as file:
    unzip = file.read()

shell = f'''
#!/bin/sh
dd if={NAME} of=unzip bs=1 count={len(unzip)} skip={MAX_SHELL_SIZE}
dd if={NAME} of=_packed.zip bs=1 count={len(data)} skip={MAX_SHELL_SIZE+len(unzip)}
chmod +x unzip
./unzip -o _packed.zip
chmod +x {MAIN}
exec ./{MAIN} "$@"
'''.encode().strip() + b'\n'

assert len(shell) < MAX_SHELL_SIZE, f'Shell file too large, ensure that MAX_SHELL_SIZE > {len(shell)}'

with open(NAME, 'wb') as file:
    file.write(shell)
    file.write(b'\0'*(MAX_SHELL_SIZE - len(shell)))
    file.write(unzip)
    file.write(data)

