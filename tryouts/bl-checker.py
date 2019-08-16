from intelhex import IntelHex
from pprint import pprint
addr_prefix= "/Users/akrv/Documents/dev/sensorfloor/addr_finder/hex_15_file/"

ih = IntelHex()

ih.fromfile(addr_prefix+"address_finder_15.simplelink.hex", format='hex')
pydict = ih.todict()
pprint(pydict)