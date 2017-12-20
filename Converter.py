import sqlite3
from pandas import notnull, ExcelFile, Series, DataFrame
import os, re

def XL2DB(excelPath, outPath):
    try:

        #Just some formatting shit, nothing to look into really
        def _rolling_group(val):
            if notnull(val): _rolling_group.group +=1 #notnull is signal to switch group
            return _rolling_group.group
        _rolling_group.group = 0 #static variable

        def _joinFunc(g,column):
            col = g[column]
            joiner = "/" if column == "Milestone/Activity - Mnemonic" else ","
            s = joiner.join([str(each) for each in col if notnull(each)])
            s = re.sub("(?<=&)" + joiner, ' ', s) #joiner = " "
            s = re.sub("(?<=-)" + joiner, '', s) #joiner = ""
            s = re.sub(joiner * 2, joiner, s)    #fixes double joiner condition
            return s

        #Converts and excel to .db file
        xl = ExcelFile(excelPath)
        #This takes in the last sheet in the excel, it assumes the last sheet is the 
        #maneuver script
        df = xl.parse(xl.sheet_names[-1], verbose = True)

        #Adds Notes and Exec Cols
        df['Notes'] = ''
        df['Exec'] = ''

        #Automatic Cleaning
        df.columns = ['Step', 'Timing', 'Milestone/Activity - Mnemonic', 'R-Description', 'Total', 'Notes', 'Exec']
        df.replace('*', '')

        groups = df.groupby(df['Step'].apply(_rolling_group), as_index = False)
        groupFunct = lambda g: Series([_joinFunc(g, col) for col in g.columns], index = g.columns)
        df = groups.apply(groupFunct)

        #Creates Db Name to database
        dbName = os.path.basename(excelPath)
        dbName = dbName[:dbName.index('.')]

        conn = sqlite3.connect(outPath)

        #Writes Script Table 
        df.to_sql('SCRIPT', conn, if_exists = 'replace', index = False, chunksize = 1)

        #Create PACR Table
        pCols =['Created', 'Author', 'Step', 'Type', 'Resp', 'Rationale', 'Steps', 'State', 'FD']
        #For Reference Script Table is:
        #['Step', 'Timing', 'Milestone/Activity - Mnemonic', 'R-Description', 'Total', 'Notes', 'Exec']
        pdf = DataFrame(columns = pCols)
        pdf = pdf.fillna('')
        #Writes PACR Table
        pdf.to_sql('PACR', conn, if_exists = 'replace', index = False, chunksize = 1)

        return True

    except:
        #If something went wrong, we won't catch it but we'll just return False
        return False
