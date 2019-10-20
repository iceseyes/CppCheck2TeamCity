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


def decode_attrs(el):
    data = {}
    for k, v in el.attrib.items():
        data[k] = v.replace('|', '||') \
            .replace("'", "|'") \
            .replace("[", "|[") \
            .replace("]", "|]") \
            .replace("\\012", '|n')

        if len(data[k]) > 4000:
            data[k] = data[k][:396] + "..."

    return data


def format_inspection(el):
    if el.tag == "error":
        data = decode_attrs(el)

        for child in el:
            if child.tag == "location":
                data["file"] = child.attrib["file"]
                data["line"] = child.attrib["line"]

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


def stream(xmlfile):
    xfile = ET.parse(xmlfile)
    for el in xfile.iter("error"):
        format_inspection(el)


def parse_args():
    parser = argparse.ArgumentParser(description="Run cppcheck")
    parser.add_argument("--print-types", dest="wtypes",
                        help="print also inspectionType messages (requires cppcheck executable)",
                        action="store_true", default=False)
    parser.add_argument("--xmlfile", "-f",
                        help="XML CppCheck output file",
                        default="cppcheck.xml")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.wtypes:
        print_types()

    stream(args.xmlfile)
    return 0


if __name__ == "__main__":
    main()
