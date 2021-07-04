# -*- coding: utf-8 -*-
import os
import re
import argparse

def main():
    parser = argparse.ArgumentParser()
    # Bookmark I/O
    group_bookmark = parser.add_argument_group("bookmark I/O")
    group_bookmark.add_argument("toc", help="path to TOC file", type=str)
    group_bookmark.add_argument("-o", "--outmarks", 
        help="name for pdftk bookmarks file. " + 
        "default is original toc name + \"_outlined\"", type=str)
    # Bookmark structure
    group_structure = parser.add_argument_group("bookmark structure",
        "if both -d and -k are specified, -d will take precedence over -k")
    group_structure.add_argument("-d", "--indentation", 
        help="escaped regex for 1 unit of indentation. please include \"\\\s\" and \"\\\\t\" only. no symbols like \"+\", \"{2}\", etc. default: \\s\\s (2 spaces)", default="\\s\\s", type=str)
    group_structure.add_argument("-k", "--keepflat", 
        action="store_true",
        help="keep outline flat")
    group_structure.add_argument("--style",
        choices=["1.2", "1.2."], default="1.2",
        help="heading style. with or without a trailing dot. "+
        "default: \"1.2\", i.e., no trailing dot", type=str)
    # PDF I/O
    group_pdf = parser.add_argument_group("PDF I/O")
    group_pdf.add_argument("--outpdf", help="path to output PDF file. " +
        "default is input pdf name + \"_outlined.pdf\" in input PDF's directory", type=str)
    group_pdf.add_argument("--inpdf", help="path to input PDF file", type=str)
    group_pdf.add_argument("-s", "--start", default=1,
        help="page in the pdf document where page 1 is. default: 1", 
        type=int)
    group_pdf.add_argument("--xml", action='store_true',
        help="use XML entities for non-ASCII characters instead of UTF-8 encoding", default=False)

    args = parser.parse_args()
    start = args.start - 1
    if args.outmarks:
        marks_name = args.outmarks
    else:
        toc_name_ext = os.path.splitext(os.path.basename(args.toc))
        toc_name, toc_ext = toc_name_ext[0], toc_name_ext[1]
        marks_name = toc_name + "_bookmarks" + toc_ext
    toc_dir = os.path.dirname(args.toc)
    if toc_dir:
        marks_path = os.path.join(toc_dir, marks_name)
    else:
        marks_path = marks_name
    if args.indentation:
        indentation = args.indentation
        if not re.match(r'^(\\s|\\t)+$', indentation):
            parser.error(f"please use \"\\\s\", \"\\\\t\", and no other symbols in the indentation pattern \"{indentation}\"")
        # The pattern for 1 unit of indentation
        ind_unit_pattern = re.compile(indentation)
        # The composite pattern,
        # e.g., "^((\\s\\s)+)" if indentation == "\\s\\s"
        ind_comp_pattern = re.compile("^((" + indentation + ")+)")

    if args.style == "1.2":
        heading_style_regex = r'^\s*(\w|\.)*\w+\s'
        heading_level_offset = 1
    else: # 1.2.
        heading_style_regex = r'^\s*(\w|\.)+\.\s'
        heading_level_offset = 2
    heading_style_pattern = re.compile(heading_style_regex)
    # Level of depth is inferred from the number of dots before the first space
    # The number of dots to ignore differ depending on the heading style
    dot_pattern = re.compile(r'\.')

    with open(args.toc, "r") as infile:
        with open(marks_path, "w") as outfile:
            line_num = 1
            for line in infile:
                # Replace a few common non-ascii characters
                line = str.replace(line, "’", "'")
                line = str.replace(line, "“", "\"")
                line = str.replace(line, "“", "\"")
                chunk = re.match(r'(.*\s)(-*\d+)', line)
                if not chunk:
                    parser.error(
                        "incorrect formatting on line {}: \n {}".format(
                            str(line_num), line))
                title = chunk.group(1)
                page = int(chunk.group(2)) + start
                if page < 1:
                    parser.error(
                        "page number out of range on line {} \n {}".format(
                        str(line_num), line))
                if args.keepflat: 
                    level = 1
                # Infer structure from indentation
                else:
                    indented = re.search(ind_comp_pattern, title)
                    if not indented:
                        heading_match = re.search(heading_style_pattern, line)
                        # TODO figure out how to mix and match heading and indentation...
                        level = 1
                    else:
                        indented = indented.group(1)
                        level = len(re.findall(ind_unit_pattern, indented)) + 1
                    # Strip title of indentation
                    title = re.sub(ind_comp_pattern, "", title)
                    # TODO
                    # Infer structure from numbering by counting the number of 
                    # dots. e.g., "1.2.3 Chapter Title" is level 3 
                    #
                    # Take everything before the first space. Accomodates 
                    # appendices numberings like A.1.2


                    if not heading_match:
                        parser.error(
                            f"subheading not in the style of \"{args.style}\" on line {line_num}: \n {line}")

                    # Allow using both indentation and heading
                    #                     
                    level = len(re.findall(dot_pattern, title)) - heading_level_offset + 1
                outfile.writelines(["BookmarkBegin\n",
                                    "BookmarkTitle: {}\n".format(title), 
                                    "BookmarkLevel: {}\n".format(level), 
                                    "BookmarkPageNumber: {}\n".format(page)])
                line_num += 1
    if args.outpdf and not args.inpdf:
        parser.error("input PDF not specified")
    # Call pdftk
    if args.inpdf: 
        if args.outpdf:
            outpdf_dir = os.path.dirname(args.outpdf)
            # If a directory is specified for the output pdf
            if outpdf_dir:
                pdf_out_path = args.outpdf
            # Only output name is specified
            # Defer dir to args.inpdf
            else:
                pdf_out_name = args.outpdf
        # Default pdf outfile
        try:
            pdf_out_name
        # `pdf_out_name` hasn't been previously defined
        except NameError:
            pdf_out_name = os.path.splitext(args.inpdf)[0] + "_outlined.pdf"
        try:
            not pdf_out_path
        # `pdf_out_path` hasn't been previously defined
        except NameError:
            dir_path = os.path.dirname(args.inpdf)
            if dir_path:
                pdf_out_path = os.path.join(dir_path, pdf_out_name)
            else:
                pdf_out_path = pdf_out_name
        if args.utf8:
            update_info = "update_info_utf8"
        else:
            update_info = "update_info"

        os.system("pdftk {} {} {} output {}".format(args.inpdf, 
            update_info, marks_path, pdf_out_path))
        # Delete intermediary bookmark file
        os.remove(marks_path)

if __name__ == "__main__":
    main()
