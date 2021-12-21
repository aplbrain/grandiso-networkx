import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="grandiso",
    version="2.1.1",
    author="Jordan Matelsky",
    author_email="opensource@matelsky.com",
    description="Performant subgraph isomorphism",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aplbrain/grandiso-networkx",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
