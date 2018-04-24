#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Date    : 2018-04-16 14:13:44
# @Author  : Nessaj (fourierrr@gmail.com)
# @Link    : http://www.csdn.com/fourierrr


"""mapper.py"""
import os
import sys
import re

for line in sys.stdin:
	line = line.strip()
	words = re.split('[,.?\s"]',line)
	for word in words:
		word = word.strip(',|.|?|\s')
		if word:

			print("{0}\t{1}".format(word,1))
