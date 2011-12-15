from setuptools import setup, find_packages
import os


setup(name='Products.qi',
      version=open('version.txt').readline().strip(),
      description="Plone add-on for quality improvement project workspaces.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='',
      maintainer='University of Utah Department of Pediatrics, UPIQ.org',
      maintainer_email='"Sean Upton" <sean.upton@hsc.utah.edu>',
      url='http://launchpad.net/upiq',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.schema>=3.8.0',
          'plone.app.dexterity>=1.1',
          'Products.CMFPlone>=4.1',
          # -*- Extra requirements: -*-
      ],
      extras_require = {
          'test': [ 'plone.app.testing>=4.0a6', ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

