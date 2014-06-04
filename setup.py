import os
import codecs
from setuptools import setup, find_packages

from filebrowser import __version__

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-filebrowser-no-grappelli-nph',
    version=__version__,
    description='Media-Management',
    long_description = read('README.rst'),
    author='Nephila',
    author_email='info@nephila.it',
    download_url='',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe = False,
)