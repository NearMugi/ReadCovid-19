#!/usr/bin/env python
# coding: utf-8

# https://www.fukushihoken.metro.tokyo.lg.jp/hodo/saishin/hassei.html
# 

# In[2]:


import sys
from pathlib import Path
from subprocess import call

# pdf2txt.py のパス
py_path = Path(sys.exec_prefix) / "Scripts" / "pdf2txt.py"
pdfPath = "2258.pdf"

# pdf2txt.py の呼び出し
call(["py", str(py_path), "-o extract-sample.txt", "-p 1", pdfPath])


# In[11]:


# https://www.shibutan-bloomers.com/python_library_pdfminer-six/2124/#21PDFJupyterNotebook

from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from io import StringIO

pdfPath = "2258.pdf"
text = ""
try:
    fp = open(pdfPath, 'rb')
    outfp = StringIO()

    rmgr = PDFResourceManager()
    lprms = LAParams()
    device = TextConverter(rmgr, outfp, laparams=lprms)
    iprtr = PDFPageInterpreter(rmgr, device)

    for page in PDFPage.get_pages(fp):
        iprtr.process_page(page)
    text = outfp.getvalue()
finally:
    device.close()
    outfp.close()
    fp.close()

baseList = text.split()
print(baseList[1])
for l in baseList:
    if not l in '':
        print(l)

