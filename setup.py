from setuptools import setup


def read(fname):
    return open(fname, 'rb').read().decode('utf-8')


setup(
    name="pyzenfolio3",
    version='0.10.0',
    author='Lucas Messenger',
    description=("Light-weight Zenfolio API Python wrapper."),
    python_requires='>=3.6',
    long_description=read('README.md'),
    license="MIT",
    keywords="zenfolio",
    url="https://github.com/layertwo/pyzenfolio3",
    packages=['pyzenfolio3'],
    install_requires=['requests==2.25.1']
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python',
    ]
)
