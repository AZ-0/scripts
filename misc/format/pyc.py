import dis
import marshal

def offset(major, minor):
    if major < 3:
        return 8
    
    if minor < 7:
        return 12
    
    return 16

with open('file.pyc', 'rb') as f:
    f.seek(offset(3, 10))
    dis.dis(marshal.load(f))