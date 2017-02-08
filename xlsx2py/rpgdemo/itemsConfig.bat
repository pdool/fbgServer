call basePath.bat
@echo off
set pydatas=%ktpydatas%/itemsConfig.py
set excel1=%ktexcels%/xlsxs/itemsConfig.xlsx
echo on
echo pydatas
echo excel1
python ../xlsx2py/xlsx2py.py %pydatas% %excel1%

if not defined ktall (ping -n 30 127.1>nul)

