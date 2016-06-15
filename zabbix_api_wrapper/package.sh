#!/bin/bash
pkgdir=build

cd ./zabbix_api_wrapper/
rm ./build/ -rf
# clean the build space first
debuild clean || true


while getopts "t:" opt; do
    case $opt in
        t)
            releasetype=$OPTARG
            ;;
    esac
done

build_ops="nocheck"
case $releasetype in
    debug)
        build_ops+=" debug nostrip noopt"
        ;;
    gcov)
        build_ops+=" gcov debug nostrip noopt"
        ;;
    release)
        ;;
    *)
        build_ops+=" debug nostrip noopt"
        ;;
esac

changelogfile=debian/changelog

if [ -n "$(which git-changelog.sh)" ]; then
    git-changelog.sh --auto -n ${BUILD_NUMBER:-0} -p $changelogfile
else
    touch $changelogfile
fi


DEB_BUILD_OPTIONS="${build_ops}" debuild -us -uc -b -nc
if [ $? -ne 0 ] ; then
    echo "ERROR! Build tdn_monitor failed!"
    exit 1
fi

mkdir -p $pkgdir
source_package_name=`dpkg-parsechangelog -l$changelogfile | awk '/^Source:/ { print $2}'`
version=`dpkg-parsechangelog -l$changelogfile | awk '/^Version:/ {print $2}'`
build_arch=`dpkg --print-architecture`
changebase=${source_package_name}_${version}_${build_arch}
changes=../$changebase.changes
buildlog=../$changebase.build
for debpkg in `sed -n '/^Files:/,$ { /^Files:/ d ; p ;} ' $changes  | awk '{print $5}'`
do
    mv ../$debpkg $pkgdir/
done
mv $changes $buildlog $pkgdir/
