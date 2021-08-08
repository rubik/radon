import os
from setuptools import setup, find_packages
import radon


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as fobj:
    readme = fobj.read()

setup(name='radon',
      version=radon.__version__,
      author='Michele Lacchia',
      author_email='michelelacchia@gmail.com',
      url='https://radon.readthedocs.org/',
      download_url='https://pypi.python.org/radon/',
      license='MIT',
      description='Code Metrics in Python',
      platforms='any',
      long_description=readme,
      packages=find_packages(),
      tests_require=['tox'],
      install_requires=[
          'mando>=0.6,<0.7',
          'colorama==0.4.1;python_version<="3.4"',
          'colorama>=0.4.1;python_version>"3.4"',
          'future',
      ],
      entry_points={
          'console_scripts': ['radon = radon:main'],
          'setuptools.installation': [
              'eggsecutable = radon:main',
          ],
          'flake8.extension': [
              'R70 = radon.contrib.flake8:Flake8Checker',
          ],
      },
      keywords='static analysis code complexity metrics',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Utilities',
      ]
)
