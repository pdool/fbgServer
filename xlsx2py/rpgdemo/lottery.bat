call basePath.bat
@echo off
set pydatas=%ktpydatas%/lotteryConfig.py
set excel1=%ktexcels%/xlsxs/lotteryConfig.xlsx
echo on
echo pydatas
echo excel1
@rem python ../xlsx2py/xlsx2py.py %pydatas% %excel1%
python E:\FBG\Server\kbengine\kbe\tools\xlsx2py\xlsx2py\xlsx2py.py E:\FBG\Server\kbengine\kbe\tools\xlsx2py\rpgdemo\pydatas\ E:\FBG\Server\kbengine\kbe\tools\xlsx2py\rpgdemo\xlsxs\lotteryConfig.xlsx
if not defined ktall (ping -n 30 127.1>nul)

