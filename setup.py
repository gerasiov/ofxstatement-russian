#!/usr/bin/python3
"""Setup
"""
from setuptools import find_packages
from distutils.core import setup

version = "0.0.2"

with open('README.rst') as f:
    long_description = f.read()

setup(name='ofxstatement-russian',
      version=version,
      author="Alexander Gerasiov",
      author_email="gq@cs.msu.su",
      url="https://github.com/gerasiov/ofxstatement-russian",
      description=("Russian banks plugins for ofxstatement"),
      long_description=long_description,
      license="GPLv3",
      keywords=["ofxstatement", "russian", "avangard", "tinkoff", "sberbank", "alfabank", "vtb"],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License v3'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=["ofxstatement", "ofxstatement.plugins"],
      entry_points={
          'ofxstatement':
              [
                  'avangard = ofxstatement.plugins.avangard:AvangardPlugin',
                  'tinkoff = ofxstatement.plugins.tinkoff:TinkoffPlugin',
                  'sberbank_csv = ofxstatement.plugins.sberbank_csv:SberBankCSVPlugin',
                  'sberbank_txt = ofxstatement.plugins.sberbank_txt:SberBankTxtPlugin',
                  'alfabank = ofxstatement.plugins.alfabank:AlfabankPlugin',
                  'vtb = ofxstatement.plugins.vtb:VtbPlugin',
              ]
          },
      install_requires=['ofxstatement'],
      test_suite="ofxstatement.plugins.tests",
      include_package_data=True,
      zip_safe=True
      )
