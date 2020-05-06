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
This prcess may take very long time (even hours) depending on how fast is the connection to the
repositories. 
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
  
 ## Hints and ideas
 * The best way to see what repositories are enabled on a system is
```
$ zypper -x ls
```
* The tool is using directly the URL of the repository server. So no mirrors are used.
* To see the contributors of a package the source repository is the way to go. As a single source package can provide several binary packages and each binary package will have the same changelog. The openSUSE Tumbleweed source repository have 13k source packages.
* The tool is using the primary.xml.gz files from the /var/cache/zypp/raw directories. If the content of those cache files are not in sync with the repository servers then the tool will fail. It is important to refresh the local repository cache:
```
$ sudo zypper ref -f
```
* There is no need to run the tool as root.

* Be prepared for long execution time even if the connection to the remote repositores are fast.Fetching the changelogs for openSUSE source repository may take 80-120 minutes even close to the servers.

* The next step is to package this tool and integrate it with zipper. It means naming the tool to zypper-changelog and put it into /usr/sbin , then it will be executable by zypper changelog. Similar to /usr/sbin/zypper-log script
