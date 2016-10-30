# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup

setup(name="setconf",
      version="0.7.4",
      description="Change configuration settings in text files",
      url="http://setconf.roboticoverlords.org/",
      author="Alexander F Rødseth",
      author_email="xyproto@archlinux.org",
      license="GPLv2",
      py_modules=["setconf"],
      entry_points={
        "console_scripts" : [
            "setconf = setconf:main",
        ]
      },
      classifiers=[
          "Environment :: Console",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Programming Language :: Python",
          "Topic :: System :: Shells",
      ]
)
