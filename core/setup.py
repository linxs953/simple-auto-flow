from importlib_metadata import requires
from setuptools import setup, find_packages 

setup(
      name='simat_core',
      version='0.0.7',
      description='simple autoflow framework',
      author='linxs',
      author_email='cakelinxs@outlook.com',
      install_requires=["httpx"],
      packages=["simat_core","simat_core.base","simat_core.utils"],
      py_modules=["simat_core"],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
      )