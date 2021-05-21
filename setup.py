import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

tests_require = ['pytest', 'pytest-cov']

setuptools.setup(
    name="hue_py",
    version="0.3.1",
    author="Matt Boran",
    author_email="mattboran@gmail.com",
    description="Python client for Philips Hue bulbs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mattboran/hue_py",
    download_url="https://github.com/mattboran/hue_py/releases/download/0.3.1/hue_py-0.3.1-py3-none-any.whl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        'requests>=2.23.0',
        'webcolors>=1.11'
    ],
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require
    },
    python_requires='>3.6.0',
)
