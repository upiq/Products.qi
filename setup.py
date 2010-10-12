import os
here = os.path.split(__file__)[0]

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

def _readFile(filename):
    path = os.path.join(here, filename)
    return open(path).read()

version = _readFile('Products/qi/version.txt')
README = _readFile('README.txt')
CHANGES = _readFile('CHANGES.txt')

setup(name='Products.qi',
      version = version,
      description = "QIWorkspace",
      long_description='\n\n'.join((README, CHANGES)),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords = '',
      author = 'Ursa Logic Corporation',
      author_email='mailto:qiworkspace-dev@ursa3.user.openhosting.com',
      url='http://ursadev.user.openhosting.com/qiworkspace',
      license='Proprietary',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      """,
      )
