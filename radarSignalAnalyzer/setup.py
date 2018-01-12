from setuptools import setup, find_packages
from setuptools.command.develop import develop
# from setuptools.command.wheel import bdist_wheel
from setuptools.command.sdist import sdist
from subprocess import check_call
import os


version = {}
with open('radarSignalAnalyzer/_version.py') as fp:
    exec(fp.read(), version)


def execute():
    pass
    # cwd = os.getcwd()
    # os.chdir('PAWrapper/Apps/papu')
    # check_call('make')
    # os.chdir(cwd)


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        execute()
        develop.run(self)


class PostSdistCommand(sdist):
    """Post-installation for sdist mode."""
    def run(self):
        execute()
        sdist.run(self)


setup(
    name='signalAnalyzer',
    version=version['__version__'],
    description='This is the PA-Wrapper',
    url='https://github.com/franciscoSoler/Radar-Simulator',
    author='Francisco Soler',
    author_email='jose.francisco.tw@gmail.com',

    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    
    entry_points={'console_scripts': ['signalAnalyzer=radarSignalAnalyzer:main',],},
    install_requires=['lxml', 'pyqt5', 'numpy', 'matplotlib', 'scipy', 'wave', 'pyaudio'],
    python_requires='>=3',

    cmdclass={
        'develop': PostDevelopCommand,
        'sdist': PostSdistCommand,
    },
)
