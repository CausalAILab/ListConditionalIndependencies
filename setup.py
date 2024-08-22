from setuptools import setup, find_packages

setup(name='ListConditionalIndependencies', packages=find_packages(), description='Lists all Conditional Independencies Implied by Causal Models with Hidden Variables in Polynomial Delay',
      author='Hyunchai Jeong', author_email='jeong3@purdue.edu', keywords=['causality', 'algorithm', 'testable implications'], url='https://github.com/CausalAILab/ListConditionalIndependencies', install_requires=['networkx', 'pydash', 'toposort', 'numpy', 'scipy', 'matplotlib', 'causal-learn'])