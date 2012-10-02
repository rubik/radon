from setuptools import setup
import radon


setup(name='radon',
      version=radon.__version__,
      author='Michele Lacchia',
      author_email='michelelacchia@gmail.com',
      license='MIT',
      packages=['radon', 'radon.tests'],
      tests_require=['tox'],
      extras_require={'tool': ['baker']},
      entry_points={'console_scripts': ['radon = radon:main']}
)
