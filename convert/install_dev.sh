#!/bin/bash
# == Bash script to bootstrap converter instance ==

#Uptodate everything
logger -t bootstrap "Start apt get tasks"
apt-get -y update 2>&1 | logger -t bootstrap
apt-get -y upgrade 2>&1 | logger -t bootstrap

#Install packages

logger -t bootstrap "Start apt get tasks"
apt-get -y install memcached  ffmpeg libavcodec-extra-53 libavcodec-dev python-dev python-setuptools git python-memcache python-psycopg2 python-pip ntp s3cmd 2>&1 | logger -t bootstrap
logger -t bootstrap "End apt get tasks"

# Setup AWS creds for S3cmd
echo "[default]
access_key = AKIAIO3ILO2MW5GQQPNQ
secret_key = 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" > /tmp/s3cfg

#Download fresh Converter application
logger -t bootstrap "Download fresh application"
cd ~
rm -rf gafv
rm gafv.tar.gz
s3cmd -c /tmp/s3cfg get s3://gafv-application/gafv.tar.gz 2>&1 | logger -t bootstrap
tar -xvf gafv.tar.gz 2>&1 | logger -t bootstrap
#cd gafv
mv converter_local_settings_dev.py local_settings.py
logger -t bootstrap "Application download finished"

#pip install all the requirements
pip install -r docs/requirements.txt | logger -t bootstrap

#Fetch latest youtube-dl script...
curl "https://raw.github.com/rg3/youtube-dl/master/youtube-dl" -o /tmp/youtube-dl | logger -t bootstrap
FILESIZE=$(stat -c%s "/tmp/youtube-dl")
echo "Size of /tmp/youtube-dl = $FILESIZE bytes." | logger -t bootstrap

if (( FILESIZE > 35000 ));
then
        mv /tmp/youtube-dl external/youtube-dl 
        chmod +x external/youtube-dl 
        echo "youtube-dl download success" | logger -t bootstrap
else
        echo "youtube-dl download fail" | logger -t bootstrap
fi


#curl "https://raw.github.com/rg3/youtube-dl/master/youtube-dl" -o external/youtube-dl 

#Get number of cores
numcores=$(grep -c ^processor /proc/cpuinfo)
workers=$[numcores*2]
echo "Detected $numcores cores, so will start $workers workers" | logger -t bootstrap


#Create upstart job for conversions... and start it...
echo "description	\"celery convert task\"
author		\"Sajal Kayan - http://www.sajalkayan.com/\"

start on (net-device-up
          and local-filesystems
          and runlevel [2345])
stop on shutdown

respawn
respawn limit 99 5

script
	export HOME=\"/root/\"
	exec /usr/bin/python /root/manage.py celeryd -c $workers -E -l info >> /var/log/celery.log 2>&1
end script

post-start script
end script
" > /etc/init/celery.conf
chmod +x /etc/init/celery.conf
#Some debug...
service celery start | logger -t bootstrap
service celery status | logger -t bootstrap

logger -t bootstrap "now look in /var/log/celery.log for more debugging..."
