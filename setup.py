from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="pdfoutliner",
      version="0.0.4",
      author="pnlng",
      description="Command line interface for generating pdftk-style bookmark files in a user-friendly way, and (optionally) outputs a PDF file with the specified outline.",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/pnlng/pdfoutliner",
      packages=["pdfoutliner"],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      entry_points={
          "console_scripts": [
              "pdfoutliner = pdfoutliner.__main__:main"
          ]
      },
      python_requires='>=3.5'
      )
