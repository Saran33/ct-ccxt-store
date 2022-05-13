from setuptools import setup

setup(
   name='ct_ccxt_store',
   version='1.0',
   description='A fork of Dave-Vallance\'s CCXT Store',
   url='https://github.com/Saran33/ct-ccxt-store',
   author='Saran Connolly',
   author_email='saran.c@pwecapital.com',
   license='MIT',
   packages=['ccxtct'],  
   install_requires=['cytrader @ git+https://github.com/Saran33/cytrader.git',"ccxt"],
)
