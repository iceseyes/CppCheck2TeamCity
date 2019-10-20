# cppcheck2teamcity

A simple tool that takes an xml file generated with [cppcheck](http://cppcheck.sourceforge.net/) and turns
it into [teamcity inspection messages](https://www.jetbrains.com/help/teamcity/build-script-interaction-with-teamcity.html#BuildScriptInteractionwithTeamCity-Inspectioninstance).

It takes, as option, the path to xml file (use -f) and if you have to print errortypes as teamcity inspection type messages.

## install 

install zip file as tool, in administration page of teamcity

## example

Suppose you have a cmake target to build cppcheck.xml into build directory. You can create a console build step into teamcity

    set -x
    cmake .
    make cppcheck.xml
    python3 %teamcity.tool.cppcheck2teamcity%/cppcheck2teamcity.py --print-types
    
     