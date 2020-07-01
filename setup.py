import setuptools
import sys

try:
    with open("README.md", 'r') as fh:
        long_description = fh.read()
except:
    long_description = ''

try:
    with open("requirements.txt", 'r') as reqs:
        requirements = reqs.read().split("\n")
except:
    requirements = ''

# versionName = sys.argv[1].replace("refs/tags/v", "")
# del sys.argv[1]

setuptools.setup(
    name="turnitin-cli",
    version="1.3.0",
    author="Ronak Badhe",
    author_email="ronak.badhe@gmail.com",
    description=long_description.split("\n")[1],
    long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/r2dev2bb8/Turnitin-CLI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    install_requires=requirements,
)
