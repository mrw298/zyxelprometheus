# zyxelprometheus
# Copyright (C) 2020 Andrew Wilkinson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zyxelprometheus", # Replace with your own username
    version="0.0.1",
    author="Andrew Wilkinson",
    author_email="andrewjwilkinson@gmail.com",
    description="Get statistics from a Zyxel router and expose them to Prometheus.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrewjw/zyxelprometheus",
    packages=setuptools.find_packages(),
    scripts=["bin/zyxelprometheus"],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
