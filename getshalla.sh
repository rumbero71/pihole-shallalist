#!/bin/bash
SHALLA_URL="http://www.shallalist.de/Downloads/shallalist.tar.gz"
#SHALLA_GROUPS="/etc/pihole/shallagroups.txt"
SHALLA_GROUPS="/var/www/shalla/shallablock.txt"
SHALLA_LOC="/var/www/html/shalla.txt"
BLACKLIST="/var/www/shalla/blacklist.txt"
WHITELIST="/var/www/shalla/whitelist.txt"
SYSWHITELIST="/etc/pihole/whitelist.txt"
LISTCONFIG="/etc/pihole/adlists.list"
DATE=`date +%s`
TEMPDIR="/tmp/getshalla-$DATE"
TEMPFILE=$TEMPDIR/shalla.txt

if [ ! -f $SHALLA_GROUPS ]; then
	echo "Error: No Filter file !!"
	exit 1;
fi
BLACKCREATE=0
if [ ! -f $BLACKLIST ]; then
	touch $BLACKLIST
	chown www-data.www-data $BLACKLIST
	BLACKCREATE=1
fi
if [ -f $BLACKLIST.old ]; then
	sum=`md5sum $BLACKLIST | awk '{ print $1 }'`
	oldsum=`md5sum $BLACKLIST.old | awk '{ print $1 }'`
	if [ "$sum" != "$oldsum" ]; then
		BLACKCREATE=1
	fi
else
	BLACKCREATE=1
fi
WHITECREATE=0
if [ ! -f $WHITELIST ]; then
	touch $WHITELIST
	chown www-data.www-data $WHITELIST
	WHITECREATE=1
fi
if [ -f $WHITELIST.old ]; then
	sum=`md5sum $WHITELIST | awk '{ print $1 }'`
	oldsum=`md5sum $WHITELIST.old | awk '{ print $1 }'`
	if [ "$sum" != "$oldsum" ]; then
		WHITECREATE=1
	fi
else
	WHITECREATE=1
fi

if [ -f $SHALLA_GROUPS.old ]; then
	sum=`md5sum $SHALLA_GROUPS | awk '{ print $1 }'`
	oldsum=`md5sum $SHALLA_GROUPS.old | awk '{ print $1 }'`
	if [ "$sum" == "$oldsum" ] && [ $BLACKCREATE -eq 0 ] && [ $WHITECREATE -eq 0 ]; then
		echo "Filter Rules are equal...exiting"
		exit 0
	fi
fi

mkdir -p $TEMPDIR
cd $TEMPDIR
grep -v "^#" $LISTCONFIG | grep -v localhost | awk -F"//" '{ print $2 }' | awk -F/ '{ print $1 }' | sort -u | sed -e 1d >whitelist.txt
cat $WHITELIST >>whitelist.txt
cat $BLACKLIST | awk '{ print "127.0.0.1\t"$0 }' >$TEMPFILE
curl -sSL $SHALLA_URL | tar xzf -
for i in `cat $SHALLA_GROUPS | awk -F" " '{ print $1 }'`; do
	echo BL/$i/domains
	cat BL/$i/domains | egrep -v '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | awk '{ print "127.0.0.1\t"$0 }' >>$TEMPFILE
	cat BL/$i/domains | egrep -v '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | awk '{ print "127.0.0.1\twww."$0 }' | sed -e s/www.www/www/g >>$TEMPFILE
done
cd
cp -f $TEMPFILE $SHALLA_LOC
cp -f $TEMPDIR/whitelist.txt $SYSWHITELIST
cp -f $SHALLA_GROUPS $SHALLA_GROUPS.old
cp -f $BLACKLIST $BLACKLIST.old
cp -f $WHITELIST $WHITELIST.old
chown www-data.www-data $SHALLA_GROUPS $SHALLA_GROUPS.old $BLACKLIST $BLACKLIST.old $WHITELIST $WHITELIST.old
rm -rf $TEMPDIR
/usr/local/bin/pihole -g
