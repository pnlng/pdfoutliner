# pdfoutliner
Command line tool for generating [`pdftk`-style](https://www.pdflabs.com/blog/export-and-import-pdf-bookmarks/) bookmark files in a user-friendly way, and (optionally) outputs a PDF file with the specified outline. 

## Table of Contents
<!-- MarkdownTOC -->

- [pdfoutliner](#pdfoutliner)
  - [Table of Contents](#table-of-contents)
  - [Why](#why)
  - [Installation](#installation)
  - [Sample Usage](#sample-usage)
      - [With PDF I/O:](#with-pdf-io)
      - [Writing a pdftk bookmark file only:](#writing-a-pdftk-bookmark-file-only)
  - [TOC Format](#toc-format)
    - [Specifying structure by subheading numbering](#specifying-structure-by-subheading-numbering)
    - [Specifying structure by indentation](#specifying-structure-by-indentation)
    - [Keeping PDF flat](#keeping-pdf-flat)
  - [Additional Options](#additional-options)
  - [Dependency](#dependency)

<!-- /MarkdownTOC -->

## Why
Instead of requiring a TOC file like this, as `pdftk` does

    BookmarkBegin
    BookmarkTitle: PDF Reference (Version 1.5)
    BookmarkLevel: 1
    BookmarkPageNumber: 1
    BookmarkBegin
    BookmarkTitle: Contents
    BookmarkLevel: 2
    BookmarkPageNumber: 3

To create a PDF file with a structured/nested outline with the script, you only need a TOC file that looks like this: 

    PDF Reference (Version 1.5) 1
      Contents 3

or perhaps better, this: 

    1 PDF Reference (Version 1.5) 1
    1.1 Contents 3

## Installation

    pip3 install pdfoutliner

## Sample Usage

#### With PDF I/O:

    pdfoutliner TOC --inpdf in.pdf -s START

where 

- `START` is the page in the PDF where p. 1 is supposed to start, and 
- `TOC` is the path to a table of contents file. 

See section [TOC Format](#toc-format) for details on the syntax. 

#### Writing a pdftk bookmark file only:

    pdfoutliner TOC

For more options, see section [Additional Options](#additional-options), or use

    pdfoutliner -h

## TOC Format
The default table of contents format is

    1 Heading 1
    1.2 Subheading 3
    1.2.3 Subsubheading 5

Each line has a numbering (not necessarily numerical), a title, and a page number, separated by space characters. 

The script will infer that "1 Heading" is level 1, "1.1 Subheading" is level 2, and so on. 

Alternatively, you can [specify the structure by indentation](#specifying-structure-by-indentation), or [keep the PDF flat](#keeping-pdf-flat). 

### Specifying structure by subheading numbering
This is the default option. As mentioned, the format is

    1 Heading 1
    1.1 Subheading 3
    1.1.1 Subsubheading 5

And the script will infer the structure from the numbering. 

If your TOC file looks like 

    1. Heading 1
    1.1. Subheading 3
    1.1.1. Subsubheading 5

i.e., has a trailing dot after each numbering, you could specify the style of the heading with `--style 1.2.`

### Specifying structure by indentation
You could also specify the structure of the outline by indentation with `-d --indentation`, followed by an escaped regex for 1 unit of indentation. 

For example, suppose my TOC looks like

    Heading 1
      Subheading 3
        Subsubheading 5

where the unit of indentation is 2 spaces, then use
    
    pdfoutliner TOC -d \\s\\s

And the script will infer the structure from the subheading indentations. 

### Keeping PDF flat
Use `-k --keepflat` and the script will ignore any numbering or indentations. The output PDF will have a flat, unstructured outline. 

    Heading 1
    Subheading 3
    Subsubheading 5

## Additional Options
    usage: pdfoutliner [-h] [-o OUTMARKS] [-d INDENTATION] [-k]
                          [--style {1.2,1.2.}] [--outpdf OUTPDF] [--inpdf INPDF]
                          [-s START]
                          toc

    optional arguments:
      -h, --help            show this help message and exit

    bookmark I/O:
      toc                   path to TOC file
      -o OUTMARKS, --outmarks OUTMARKS
                            name for pdftk bookmarks file. default is original toc
                            name + "_outlined"

    bookmark structure:
      if both -d and -k are specified, -d will take precedence over -k

      -d INDENTATION, --indentation INDENTATION
                            escaped regex for 1 unit of indentation
      -k, --keepflat       keep outline flat
      --style {1.2,1.2.}    heading style. with or without a trailing dot. default
                            "1.2", i.e., no trailing dot

    PDF I/O:
      --outpdf OUTPDF       path to output PDF file. default is input pdf name +
                            "_outlined.pdf" in input PDF's directory
      --inpdf INPDF         path to input PDF file
      -s START, --start START
                            page in the pdf document where page 1 is. default 1

## Dependency

- [pdftk](https://www.pdflabs.com/tools/pdftk-server/)
    - on macOS 10.11+, use the build [here](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/pdftk_server-2.02-mac_osx-10.11-setup.pkg)
- (optional) [Tabula](http://tabula.technology/)
    - for extracting a usable TOC from PDF files (along with some additional [regex golfing](https://xkcd.com/1313/))
