# coding=utf-8
"""Python Arlo setup script."""
from setuptools import setup


def readme():
    with open('README.rst') as desc:
        return desc.read()


setup(
    name='pyarlo',
    packages=['pyarlo'],
    version='0.2.2',
    description='Python Arlo is a library written in Python 2.7/3x ' +
                'that exposes the Netgear Arlo cameras as Python objects.',
    long_description=readme(),
    author='Marcelo Moreira de Mello',
    author_email='tchello.mello@gmail.com',
    url='https://github.com/tchellomello/python-arlo',
    license='LGPLv3+',
    include_package_data=True,
    install_requires=['requests', 'sseclient-py'],
    test_suite='tests',
    keywords=[
        'arlo',
        'netgear',
        'camera',
        'home automation',
        'python',
        ],
    classifiers=[
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ' +
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)
