from setuptools import setup, find_packages

setup(name='ListConditionalIndependencies', packages=find_packages(), description='Lists all Conditional Independencies Implied by Causal Models with Hidden Variables in Polynomial Delay',
      author='', author_email='', keywords=['causality', 'algorithm', 'testable implications'], url='', requires=['networkx', 'pydash', 'toposort', 'numpy', 'scipy', 'matplotlib', 'causal-learn'])