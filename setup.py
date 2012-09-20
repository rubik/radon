from setuptools import setup
import radon


setup(name='radon',
      version=radon.__version__,
      author='Michele Lacchia',
      author_email='michelelacchia@gmail.com',
      packages=['radon'],
      entry_points={'console_scripts': ['radon = radon:main']})
