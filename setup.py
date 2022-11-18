from setuptools import setup, find_packages


setup(name='topython',
      version='0.1',
      description='Tools for converting scientific software from IDL to Python',
      author='Eric Grimes',
      author_email='egrimes@igpp.ucla.edu',
      url='https://github.com/supervised/topython/',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      install_requires=['openai'],
      python_requires='>=3.7',
     )