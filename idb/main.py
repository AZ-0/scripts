#!/usr/bin/python3
from idb import IDB
idb = IDB()
idb.load('test/exploitme.s')
idb.breakpoint(-1)
idb.run()
idb.cli()