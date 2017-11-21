# -*- coding: utf-8 -*-
import re


def getCP(s):
    if s:
        s = s.split('     ')
        try:
            cp = re.match(r'Z[NARXTFEISL]\w{10}', s[0]).group()
            return cp + '.prc'
        except AttributeError: return 'No CP Passed'
    else: pass

def getParams(s):
    if getCP(s):
        s = s.split('     ')
        try:
            params = re.search(r'\(.*?\)', s[0]).group()
            return params.replace('(', '').replace(')', '')
        except AttributeError: return 'No Params Passed'