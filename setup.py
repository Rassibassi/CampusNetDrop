from distutils.core import setup
import py2exe

import sys; sys.argv.append('py2exe')

Mydata_files = [('LogoCampusNetDrop.png')]
py2exe_options = dict(
                      dll_excludes=["MSVCP90.dll"],  # Exclude msvcr71
                      compressed=True,  # Compress library.zip
                      )

setup(name='CampusNetDrop',
      version='1.0',
      description='CampusNetDrop',
      author='Rasmus Jones',
      windows=[{
      			"script": "CampusNetDrop.py",
      			#'uac_info': "requireAdministrator",
      			"icon_resources": [(1, "icon.ico")]
      			}],
      data_files = Mydata_files,
      options={'py2exe': py2exe_options},
      )