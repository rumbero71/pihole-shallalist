#!/bin/bash
SHALLA_URL="http://www.shallalist.de/Downloads/shallalist.tar.gz"
DATE=`date +%s`
TEMPDIR="/tmp/getshallalists-$DATE"
TEMPFILE=$TEMPDIR/shallacategories.txt
USAGEFILE=$TEMPDIR/BL/global_usage
USAGETEMP=$USAGEFILE.tmp
CATEGORYFILE="/var/www/shalla/shallacategories.txt"
mkdir -p $TEMPDIR
cd $TEMPDIR
curl -sSL $SHALLA_URL | tar xzf -
cat $USAGEFILE | egrep -v "^#" | egrep -v "^NAME [A-Z]" | egrep -v "^DESC [A-D|F-Z]" | grep -v "^SOURCE" | grep -v "^DEFAULT" | sed -e "s/^NAME:[[:space:]]\+//g" -e "s/^$/%%%/g" | tr -d '\012\015' | sed -e "s/%%%/\n/g" -e "s/DESC EN://g" | egrep -v "^$" >$USAGETEMP

cp -f $USAGETEMP $CATEGORYFILE
rm -rf $TEMPDIR
