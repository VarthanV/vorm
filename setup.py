from distutils.core import setup
from setuptools import PackageFinder, setup, setuptools, version
import os


README_PATH = os.path.join(os.path.dirname(__file__), 'README.md')

with open(README_PATH) as readme_file:
    readme = readme_file.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='vorm',
    version='0.0.2',
    package=setuptools.find_packages(),
    include_packages_data=True,
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    description="A toy ORM",
    author="Vishnu Varthan",
    author_email="vishnulatha006@gmail.com",
    url="https://github.com/VarthanV/vorm",
    install_requires=[
        "autopep8==1.5.7",
        "mysql-connector-python==8.0.25",
        "protobuf==3.17.3",
        "pycodestyle==2.7.0",
        "six==1.16.0",
        "toml==0.10.2",

    ],
    license="MIT License",
    zip_safe=False,
    keywords="orm,flask,django",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],

)
