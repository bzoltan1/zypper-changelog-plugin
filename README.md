# changelog tool for openSUSE
Simple tool to fetch the changelog of packages from the rpm repositories.
With `rpm -q --changelog` it is possible to list the changelogs of the installed packages, but there is no available tool what could list the changelogs of the packages not installed. This featureis useful before installing or upgrading a package to see what changes are going to be installed.

## Requirements

The tool is a python3 script what imports

* subprocess
* os
* sys
* re
* argparse
* datetime
* re
* requests
* rpm
* xml.etree.ElementTree

and uses zypper

## How to use
```
$ changelog.py [-h] [-d] [-v] [-e] [-p PACKAGE] [-r REPOS] [-a]
```

## Simple usecases
To show all changelog for all packages in the openSUSE-Tumbleweed-Oss repository.
This prcess may take very long time depending on how fast is the connection to the
repositories
```
$ changelog.py -a -v -r repo-oss 
```
To show the list contributors of Firefox in the openSUSE-Tumbleweed-Oss repository
```
$ changelog.py -p MozillaFirefox -r repo-oss 
```

To show the changelogs of all vim* packages the openSUSE-Tumbleweed-Oss and binary and source repositories
```
$ changelog.py -p MozillaFirefox -r repo-oss,repo-source
```


## Options and parameters
* -p, --package [PACKAGE]
  + Package name or regular expression to match packages.

* -r,--repositorie  [REPOS]
 + Comma separated list of repositores to search for changelogs.

* -h, --help            
  + Show the help message and exit
  
* -a, --all
  + Lists changelogs for all packages
  
* -v, --verbose
  + Print all the changelog text
  
* -e, --expression
  + Enable regular expression in package name
