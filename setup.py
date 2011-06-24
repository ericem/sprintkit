from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
README = open(path.join(here, 'README.rst')).read()
CHANGES = open(path.join(here, 'CHANGES')).read()

version = '0.1.0'

setup(
    name='sprintkit',
    version=version,
    description="Access Sprint's Network APIs Through Python",
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='communications',
    author='Eric Miller',
    author_email='eric.miller@sprint.com',
    url='https://github.com/ericem/sprintkit',
    license='MIT',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    zip_safe=False,
    setup_requires=['nose'],
    install_requires=['restkit>=3.2']
)
