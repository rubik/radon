import os
from setuptools import setup
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
      packages=['radon', 'radon.tests'],
      tests_require=['tox'],
      install_requires=['baker', 'colorama'],
      entry_points={'console_scripts': ['radon = radon:main']},
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Utilities',
      ]
)
