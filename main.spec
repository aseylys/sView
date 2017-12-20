# -*- mode: python -*-

#pyinstaller --noconsole --clean --onefile --icon=main.ico main.spec 

block_cipher = None

def get_pandas_path():
    import pandas
    pandas_path = pandas.__path__[0]
    return pandas_path

###########Hardcoded directory inside###########
#The path to the main project folder
#The path to the folder that contains all the uis
################################################
added_files = [
('C:\\Users\\trevor.doll\\Desktop\\sView\\Main', '.'),
('C:\\Users\\trevor.doll\\Desktop\\sView\\Main\\ui', 'ui')
]

###########Hardcoded directory inside###########
#The path to sView.py
#The path to PyQt5\Qt\bin
#The path to the destination folder for bundling
################################################
a = Analysis(['C:\\Users\\trevor.doll\\Desktop\\sView\\Main\\sView.py'],
             pathex=['C:\\Users\\trevor.doll\\AppData\\Local\\Programs\\Python\\Python36-32\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'C:\\Users\\trevor.doll\\Desktop\\sView\\App'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['matplotlib', 'FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter', 'scipy', 'sqlalchemy'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

dict_tree = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pandas' not in x[0], a.binaries)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

###########Hardcoded directory inside###########
#The path to the icon svIcon.ico
################################################
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='sView',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon= 'C:\\Users\\trevor.doll\\Desktop\\sView\\Main\\svIcon.ico' )


coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='sView')
