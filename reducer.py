#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-16 16:13:15
# @Author  : Nessaj (fourierrr@gmail.com)
# @Link    : http://www.csdn.com/fourierrr



"""resucer.py"""
import os
import sys
from operator import itemgetter
current_word = None
current_count = 0
word = None

for line in sys.stdin:
	word = line.split('\t',1)[0]
	count = line.split('\t',1)[1]
	count = int(count)
	if current_word == word:
		current_count+=count
	else:
		if current_word:
			print("{0}\t{1}".format(current_word,current_count))
		current_word = word
		current_count = count

if word:
	print("{0}\t{1}".format(current_word,current_count))

