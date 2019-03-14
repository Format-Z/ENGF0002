# Call these commands with:
# $ doit

import doit
import glob

Python_files = glob.glob("src/*.py")

def task_test():
    """Test all fragments"""
    return {
        'actions': [r'pytest --doctest-modules %s > testreport.txt' % (" ".join(Python_files)),],
        'file_dep': Python_files,
        'targets': ["testreport.txt"],
        'verbosity': 2,
        }


def task_build():
    """build cmd """
    return {
        'actions': ['pdflatex -shell-escape 10_Development_Practices ;pdflatex -shell-escape 10_Development_Practices ; bibtex 10_Development_Practices ; pdflatex -shell-escape 10_Development_Practices',],
        'file_dep': ["testreport.txt"] + Python_files +
                     ["10_Development_Practices.tex"],
        'targets': ["10_Development_Practices.pdf"],
        'verbosity': 2,
        }
