from setuptools import setup, find_packages
import os

version = '0.1'

tests_require = ['collective.testcaselayer']

setup(name='collective.contemplate',
      version=version,
      description="Add content from existing content templates",
       long_description=open(os.path.join(
          "src", "collective", "contemplate", "README.txt"
          )).read() + "\n" + open(os.path.join(
          "docs", "HISTORY.txt")).read() + "\n" + open(os.path.join(
          "docs", "TODO.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/collective.contemplate',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require={'tests': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
