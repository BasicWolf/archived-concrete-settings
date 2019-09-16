import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

# fmt: off
setuptools.setup(
    name="concrete_settings",
    version="0.0.1",
    author="Zaur Nasibov",
    author_email="comments@znasibov.info",
    description="concrete_settings make settings in large projects maintainable",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/basicwolf/concrete-settings",
    packages=setuptools.find_packages(),
    install_requires=[
        'sphinx>=1.8.4',
        'typeguard>=2.3.1',
    ],
    extras_require={
        'Reading settings from YAML files': 'pyyaml>=5.1.2',

        'dev': [
            'sphinxcontrib-plantuml>=0.17.1',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
