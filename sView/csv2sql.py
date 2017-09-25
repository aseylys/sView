import sqlite3
import pandas as pd
import os, re

#REPLACE ASTERISKS IN EXCEL USING 
#CTRL+H
#~*~*~*
xl = pd.ExcelFile('goes15yf.xlsm')
df = xl.parse(xl.sheet_names[-1], verbose = True)
def rolling_group(val):
    if pd.notnull(val): rolling_group.group +=1 #pd.notnull is signal to switch group
    return rolling_group.group
rolling_group.group = 0 #static variable

def joinFunc(g,column):
    col =g[column]
    joiner = "/" if column == "Milestone/Activity - Mnemonic" else ","
    s = joiner.join([str(each) for each in col if pd.notnull(each)])
    s = re.sub("(?<=&)"+joiner," ",s) #joiner = " "
    s = re.sub("(?<=-)"+joiner,"",s) #joiner = ""
    s = re.sub(joiner*2,joiner,s)    #fixes double joiner condition
    return s

groups = df.groupby(df['Row #'].apply(rolling_group), as_index = False)
groupFunct = lambda g: pd.Series([joinFunc(g,col) for col in g.columns],index=g.columns)
df = groups.apply(groupFunct)
conn = sqlite3.connect(xl.sheet_names[-1] + '.db')
df.to_sql(xl.sheet_names[-1], conn, if_exists = 'replace', index = False, chunksize = 1)
