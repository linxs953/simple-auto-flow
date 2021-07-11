from importlib_metadata import requires
from setuptools import setup, find_packages 

setup(
      name='autoflow',
      version='0.1',
      description='simple autoflow framework',
      author='linxs',
      author_email='cakelinxs@outlook.com',
      # install_requires=["httpx"],
      packages=["core","core.base","core.utils"],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
      )