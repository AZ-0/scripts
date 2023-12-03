from shlex import quote
import os

NAME = quote('coined')      # Name of the smuggler file (the one that is copied by Docker)
MAIN = quote('proxy.sh')    # Name of the file that should be run after the extractor
WRAPPED = 'wrapped'         # Name of the directory containing the smuggled files
MAX_SHELL_SIZE = 512        # Size of the shell script

shell = f'''
#!/bin/sh
cp {NAME} /tmp/{NAME}
'''.strip()

packed = bytearray()
length = 0

for name in os.listdir(WRAPPED):
    with open(WRAPPED + '/' + name, 'rb') as file:
        data = file.read()
        packed.extend(data)
    shell += f'\ndd if=/tmp/{NAME} of={quote(name)} bs=1 count={len(data)} skip={MAX_SHELL_SIZE + length}'

shell += f'''
chmod +x {MAIN}
exec ./{MAIN} "$@"
'''

shell = shell.encode()

with open(NAME, 'wb') as file:
    file.write(shell)
    file.write(bytes(MAX_SHELL_SIZE - len(shell)))
    file.write(packed)
