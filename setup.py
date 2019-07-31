from setuptools import *

setup(
    name="directdemod",
    packages=find_packages(),
    version="1.0",
    license="MIT",
    author="Vinay C K, Vladyslav Mokrousov",
    author_email="",
    url="https://directdemod.readthedocs.io/en/",
    description="",
    install_requires=[
        "numpy",
        "scipy",
        "pykep",
        "pytest",
    ]
)
