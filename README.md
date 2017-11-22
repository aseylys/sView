# sView
sView Program

Documentation included
To Edit, Requirements:

    -Python 3.5+

    -PyQt5
  
  
To Run:

    -main.py

    (Load Database File)

    -File > Open Script (Example .db File included, TF10_AEW_2017108.db)
    
Current Bugs:
    
    pModel won't change when run on 2 different instances or when editted, closed and attempted to re-edit. This might have something to do with non-async database connections..
    
    To replicate error
        -Load Database
        -Go to PACR tab
        -'New PACR'
        -Click on newly created row in left table
        -Fill out the starred (*) fields
        -'Save'
        -'Push'
        -Click on the row that was created
        -Click the 'Check Mark' button next to the 'FD' label
        -This should've put 'Approved' in where 'Review' was and put in the main database on the 'Script' tab, but it doesn't
