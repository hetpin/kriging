#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
print "Hello World!"
import fileinput
import sys
cgitb.enable()

print "Content-Type: text/plain;charset=utf-8"
print

for line in fileinput.input("fileinput-example-2.py"):
    sys.stdout.write("-> ")
    sys.stdout.write(line)