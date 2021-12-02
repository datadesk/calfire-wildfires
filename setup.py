import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='calfire-wildfires',
    version='0.0.4',
    description="Download wildfires data from CalFire",
    long_description=read('README.md'),
    author='Los Angeles Times Data and Graphics Department',
    author_email='datagraphics@caltimes.com',
    url='http://www.github.com/palewire/calfire-wildfires',
    license="MIT",
    packages=("calfire_wildfires",),
    install_requires=[
        "click",
        "requests"
    ],
    entry_points="""
        [console_scripts]
        calfirewildfires=calfire_wildfires.cli:cmd
    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
    project_urls={
        'Maintainer': 'https://github.com/palewire',
        'Source': 'https://github.com/palewire/calfire-wildfires',
        'Tracker': 'https://github.com/palewire/calfire-wildfires/issues'
    },
)
