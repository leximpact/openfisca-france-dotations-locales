# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "OpenFisca-France-Dotations-Locales",
    version = "0.7.1",
    author = "LexImpact Team",
    author_email = "leximpact@an.fr",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
    description = "[EN] OpenFisca tax and benefit system for France State endowments to local authorities. \
        [FR] Modèle de microsimulation OpenFisca dédié aux dotations de l'État aux collectivités territoriales.",
    keywords = "France microsimulation local tax endowment dotations territoires",
    license ="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    url = "https://github.com/leximpact/openfisca-france-dotations-locales",
    include_package_data = True,  # Will read MANIFEST.in
    data_files = [
        ("share/openfisca/openfisca-france-dotations-locales",
        ["CHANGELOG.md", "LICENSE", "README.md"]),
        ],
    install_requires = [
        "OpenFisca-Core[web-api] >=27.0,<36.0",
        ],
    extras_require = {
        "dev": [
            "pandas >= 0.24.0, < 0.25.0",
            "autopep8 == 1.5",
            "flake8 >= 3.5.0,<3.8.0",
            "pycodestyle >= 2.3.0,<2.6.0",  # To avoid incompatibility with flake
            ]
        },
    packages=find_packages(),
    )
