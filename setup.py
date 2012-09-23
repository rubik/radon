from setuptools import setup
import radon


setup(name='radon',
      version=radon.__version__,
      author='Michele Lacchia',
      author_email='michelelacchia@gmail.com',
      license='MIT',
      packages=['radon'],
      tests_require=['tox'],
      entry_points={'console_scripts': ['radon = radon:main']})
