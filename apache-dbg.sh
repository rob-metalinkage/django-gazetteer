#!/bin/bash -vx

# httpd-debug.sh
# Run apache in DEBUG mode with logging to stdout and trace of opened files
# Andres Hernandez - tonejito - 

STRACE=`which strace`

APACHE_DEBUG="/usr/sbin/apache2 -X -e debug"

cd /etc/apache2
source envvars
if [ -n "$STRACE" ]
then
  $STRACE -e trace=open $APACHE_DEBUG
else
  $APACHE_DEBUG
fi

