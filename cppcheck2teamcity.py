#!/usr/bin/env python3

#######################################################################################################################
## Translate XML output from *cppcheck* into a list of
## [TeamCity Messages](https://www.jetbrains.com/help/teamcity/build-script-interaction-with-teamcity.html#BuildScriptInteractionwithTeamCity-Inspectioninstance)
##
## Can produce alse InspectionType messages using cppcheck
#######################################################################################################################
## Run from cppcheck.xml directory:
##       ./cppckech2teamcity.py
##
## Run on no-standard file
##       ./cppckech2teamcity.py -f ../nostd_file.xml
##
## Export also types:
##       ./cppcheck2teamcity.py --print-types
#######################################################################################################################

import argparse
import os
import subprocess
import xml.etree.ElementTree as ET


TC_INSPECTION_MSG = "##teamcity[inspection " \
                    "typeId='{id}' message='{msg}' " \
                    "severity='{severity}' file='{file}' line='{line}']"
TC_INSPECTION_TYPE_MSG = "##teamcity[inspectionType id='{id}' " \
                         "name='{msg}' description='{verbose}' category='{severity}']"


def get_cppcheck_path():
    return [os.environ.get("CPPCHECK_BIN", "/usr/bin/cppcheck"), ]


def load_errortypes_xml(file):
    parser = ET.XMLPullParser(['start', 'end'])
    while True:
        l = file.readline().decode()
        parser.feed(l)

        if not l.strip():
            return parser


def tc_escape(v):
    return v.replace('|', '||') \
            .replace("'", "|'") \
            .replace("[", "|[") \
            .replace("]", "|]") \
            .replace("\\012", '|n')


def escape(v):
    return tc_escape(v).replace("\n", "|n").replace("\r", "")

def decode_attrs(el):
    data = {}
    for k, v in el.attrib.items():
        data[k] = tc_escape(v)

        if len(data[k]) > 4000:
            data[k] = data[k][:396] + "..."

    return data


def format_inspection(el, root, exclude):
    if root and root[-1] != "/":
        root += "/"

    if el.tag == "error":
        data = decode_attrs(el)

        for child in el:
            if child.tag == "location":
                data["file"] = child.attrib["file"]
                data["line"] = child.attrib["line"]

                with open(data["file"], "rb") as file:
                    for i, line in enumerate(file):
                        if (i+1) == int(data['line']):
                            data["msg"] += "|n|n" + escape(line.decode()) + "|n"
                            break

                if not root or data["file"].startswith(root) and (
                        not exclude or not data["file"].startswith(os.path.join(root, exclude))):
                    data["file"] = data["file"].replace(root, "")
                    print(TC_INSPECTION_MSG.format(**data))


def format_inspection_type(event, el):
    if event == "start" and el.tag == "error":
        data = decode_attrs(el)

        print(TC_INSPECTION_TYPE_MSG.format(**data))


def print_types():
    process = subprocess.Popen(get_cppcheck_path() + ["--errorlist", ],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

    parser = load_errortypes_xml(process.stdout)

    for event, el in parser.read_events():
        format_inspection_type(event, el)


def stream(xmlfile, root, exclude):
    xfile = ET.parse(xmlfile)
    for el in xfile.iter("error"):
        format_inspection(el, root, exclude)


def parse_args():
    parser = argparse.ArgumentParser(description="Run cppcheck")
    parser.add_argument("--print-types", dest="wtypes",
                        help="print also inspectionType messages (requires cppcheck executable)",
                        action="store_true", default=False)
    parser.add_argument("--xmlfile", "-f",
                        help="XML CppCheck output file",
                        default="cppcheck.xml")
    parser.add_argument("--root", "-r", help="project root path", default="")
    parser.add_argument("--exclude", "-e", help="exclude file by prefix", default="")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.wtypes:
        print_types()

    stream(args.xmlfile, args.root, args.exclude)
    return 0


if __name__ == "__main__":
    main()
