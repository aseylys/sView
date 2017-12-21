# -*- coding: utf-8 -*-
import re


def getCP(s):
    #Returns the CP if it exsists in an executable step
    if s:
        s = s.split('     ')
        try:
            cp = re.match(r'Z[ACEFGHILMNOPRSTWX]\w{10}', s[0]).group()
            return cp + '.prc'
        except AttributeError: return ''
    else: pass

def getParams(s):
    #If a CP exists in an executable step, return the passed parameters if there are any
    if getCP(s):
        s = s.split('     ')
        try:
            params = re.search(r'\(.*?\)', s[0]).group()
            return params.replace('(', '').replace(')', '')
        except AttributeError: return ''