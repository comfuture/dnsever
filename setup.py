import os
import os.path
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from dnsever import VERSION, DESCRIPTION

setup(
    name='DNSEver',
    packages=['dnsever'],
    version=VERSION,
    description='Unofficial DNSEver python client',
    long_description=DESCRIPTION,
    author='comfuture',
    author_email='comfuture@gmail.com',
    install_requires=['mechanize', 'lxml'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: Name Service (DNS)'
    ]
)
