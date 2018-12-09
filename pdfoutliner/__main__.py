# -*- coding: utf-8 -*-
import os
import re
import argparse

def main():
    parser = argparse.ArgumentParser()
    # bookmark I/O
    group_bookmark = parser.add_argument_group("bookmark I/O")
    group_bookmark.add_argument("toc", help="path to TOC file", type=str)
    group_bookmark.add_argument("-o", "--outmarks", 
        help="name for pdftk bookmarks file. " + 
        "default is original toc name + \"_outlined\"", type=str)
    # bookmark structure
    group_structure = parser.add_argument_group("bookmark structure",
        "if both -d and -k are specified, -d will take precedence over -k")
    group_structure.add_argument("-d", "--indentation", 
        help="escaped regex for 1 unit of indentation", type=str)
    group_structure.add_argument("-k", "--keepflat", 
        help="keep outline flat", 
        action="store_true")
    group_structure.add_argument("--style",
        choices=["1.2", "1.2."], default="1.2",
        help="heading style. with or without a trailing dot. "+
        "default \"1.2\", i.e., no trailing dot", type=str)
    # pdf I/O
    group_pdf = parser.add_argument_group("PDF I/O")
    group_pdf.add_argument("--outpdf", help="path to output PDF file. " +
        "default is input pdf name + \"_outlined.pdf\" in input PDF's directory", type=str)
    group_pdf.add_argument("--inpdf", help="path to input PDF file", type=str)
    group_pdf.add_argument("-s", "--start", default=1,
        help="page in the pdf document where page 1 is. default 1", 
        type=int)

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
    with open(args.toc, "r") as infile:
        with open(marks_path, "w") as outfile:
            line_num = 1
            if args.indentation:
                indentation = args.indentation
                # the pattern for 1 unit of indentation
                ind_unit_pattern = re.compile(indentation)
                # the composite pattern
                # e.g., "^((\s\s)+)" if indentation == "\s\s"
                ind_comp_pattern = re.compile("^((" + indentation + ")+)")
            for line in infile:
                # replace a few common non-ascii characters
                line = str.replace(line, "’", "'")
                line = str.replace(line, "“", "\"")
                line = str.replace(line, "“", "\"")
                chunk = re.match(r'(.*\s)(\d+)', line)
                if not chunk:
                    parser.error(
                        "incorrect formatting on line {}: \n {}".format(
                            str(line_num), line))
                title = chunk.group(1)
                page = int(chunk.group(2)) + start
                # infer structure from indentation
                if args.indentation:
                    indented = re.search(ind_comp_pattern, title)
                    if not indented:
                        level = 1
                    else:
                        indented = indented.group(1)
                        level = len(re.findall(ind_unit_pattern, indented)) + 1
                    # strip title of indentation
                    title = re.sub(ind_comp_pattern, "", title)
                elif args.keepflat: 
                    level = 1
                    if not args.inpdf:
                        parser.error("-k --keepflat is to be used with --inpdf")
                else:
                    # infer structure from numbering by counting the number of 
                    # dots. e.g., "1.2.3 Chapter Title" is level 3 
                    #
                    # take everything before the first space. accomodates 
                    # appendices numberings like A.1.2

                    # integrity check
                    e_temp = "subheading not in the style of \"{}\" on line {}: \n {}"
                    e_msg = e_temp.format(args.style, line_num, line)
                    if args.style == "1.2":
                        if not re.search(r'^\s*(\w|\.)*\w+\s', line):
                            parser.error(e_msg)
                    if args.style == "1.2.":
                        if not re.search(r'^\s*(\w|\.)+\.\s', line):
                            parser.error(e_msg)
                    indented_search = re.search(r'^(.*)\s?', line)
                    level_offset = 2 - len(re.findall(r'\.', args.style))
                    if indented_search:
                        indented = indented_search.group(1)
                        level = len(re.findall(r'\.', indented)) + level_offset
                    else:
                        level = 1
                outfile.writelines(["BookmarkBegin\n",
                                    "BookmarkTitle: {}\n".format(title), 
                                    "BookmarkLevel: {}\n".format(level), 
                                    "BookmarkPageNumber: {}\n".format(page)])
                line_num += 1
    if args.outpdf and not args.inpdf:
        parser.error("input PDF not specified")
    # call pdftk
    if args.inpdf: 
        if args.outpdf:
            outpdf_dir = os.path.dirname(args.outpdf)
            # if a directory is specified for the output pdf
            if outpdf_dir:
                pdf_out_path = args.outpdf
            # only output name is specified
            # defer dir to args.inpdf
            else:
                pdf_out_name = args.outpdf
        # default pdf outfile
        try:
            pdf_out_name
        # pdf_out_name hasn't been previously defined
        except NameError:
            pdf_out_name = os.path.splitext(args.inpdf)[0] + "_outlined.pdf"
        try:
            not pdf_out_path
        # pdf_out_path hasn't been previously defined
        except NameError:
            dir_path = os.path.dirname(args.inpdf)
            if dir_path:
                pdf_out_path = os.path.join(dir_path, pdf_out_name)
            else:
                pdf_out_path = pdf_out_name
        os.system("pdftk {} update_info {} output {}".format(args.inpdf, 
            marks_path, pdf_out_path))
        # delete intermediary bookmark file
        os.remove(marks_path)

if __name__ == "__main__":
    main()