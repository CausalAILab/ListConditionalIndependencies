from setuptools import setup, find_packages

setup(name='ListConditionalIndependencies', packages=find_packages(), description='Lists All Conditional Independencies Implied By A Causal Model',
      author='Hyunchai Jeong', author_email='jeong3@purdue.edu', keywords=['causality', 'algorithm', 'testable implications'], url='https://github.com/CausalAILab/ListConditionalIndependencies', requires=['networkx', 'pydash', 'toposort'])
