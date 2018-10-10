import setuptools

exec(open("tabel/_version.py").read())

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tabel",
    keywords='data table',
    version=__version__,
    author="Bastiaan Bergman",
    author_email="Bastiaan.Bergman@gmail.com",
    description="Lightweight, intuitive and fast data-tables.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/BastiaanBergman/tabel",
    packages=setuptools.find_packages(),
    license='MIT',
    python_requires='>=2.6, >=3.0',
    install_requires=['numpy', 'tabulate'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "https://tabel.readthedocs.io/en/stable/",
        "Source Code": "https://github.com/BastiaanBergman/tabel",
    }
)
