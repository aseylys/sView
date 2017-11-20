import sqlite3
import pandas as pd
import os, re

#REPLACE ASTERISKS IN EXCEL USING 
#CTRL+H
#~*~*~*
#Replace Row # with Step

#Choose Excel file to load
EXCEL_PATH = 'excels/TF10_AEW_2017108.xlsx'
xl = pd.ExcelFile(EXCEL_PATH)
df = xl.parse(xl.sheet_names[-1], verbose = True)

#Adds Notes Col
df['Notes'] = ''
df['Exec'] = ''

#Just some formatting shit, nothing to look into really
def rolling_group(val):
    if pd.notnull(val): rolling_group.group +=1 #pd.notnull is signal to switch group
    return rolling_group.group
rolling_group.group = 0 #static variable

def joinFunc(g,column):
    col = g[column]
    joiner = "/" if column == "Milestone/Activity - Mnemonic" else ","
    s = joiner.join([str(each) for each in col if pd.notnull(each)])
    s = re.sub("(?<=&)" + joiner, ' ', s) #joiner = " "
    s = re.sub("(?<=-)" + joiner, '', s) #joiner = ""
    s = re.sub(joiner * 2, joiner, s)    #fixes double joiner condition
    return s

groups = df.groupby(df['Step'].apply(rolling_group), as_index = False)
groupFunct = lambda g: pd.Series([joinFunc(g, col) for col in g.columns],index = g.columns)
df = groups.apply(groupFunct)

#connects to database
dbName = xl.sheet_names[-1] + '.db'

#Edit this line to choose directory (for Windows replace '\' with '\\')
DBDIR = os.path.dirname(os.path.realpath(__file__))

conn = sqlite3.connect(os.path.join(DBDIR, dbName))

#Writes Script Table based on name of last sheet in Excel Book
df.to_sql(xl.sheet_names[-1], conn, if_exists = 'replace', index = False, chunksize = 1)

#Create PACR Table
pCols =['Created', 'Author', 'Step', 'Type', 'Resp', 'Rationale', 'Steps', 'State', 'FD']
#For Reference Script Table is:
#['Step', 'Timing', 'Milestone/Activity - Mnemonic', 'R-Description', 'Total', 'Notes', 'Exec']
pdf = pd.DataFrame(columns = pCols)
pdf = pdf.fillna('')
#Writes PACR Table
pdf.to_sql('PACR', conn, if_exists = 'replace', index = False, chunksize = 1)