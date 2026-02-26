from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in cpcs/__init__.py
from cpcs import __version__ as version

setup(
	name="cpcs",
	version=version,
	description="construction project",
	author="john",
	author_email="johnsaolli@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
