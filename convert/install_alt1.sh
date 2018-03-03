#!/bin/bash
# == Bash script to bootstrap converter instance ==

#Uptodate everything
logger -t bootstrap "Start apt get tasks"
apt-get -y update 2>&1 | logger -t bootstrap
apt-get -y upgrade 2>&1 | logger -t bootstrap

#Install packages

logger -t bootstrap "Start apt get tasks"
apt-get -y install memcached  ffmpeg gpac libavcodec-extra-53 libavcodec-dev python-dev python-setuptools git python-memcache python-psycopg2 python-pip ntp s3cmd make 2>&1 | logger -t bootstrap
logger -t bootstrap "End apt get tasks"

#upgrade python 2.7.3 to python 2.7.9
logger -t bootstrap "Start python upgrade to 2.7.9"
wget https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz 2>&1 | logger -t bootstrap
tar -xvf Python-2.7.9.tgz 2>&1 | logger -t bootstrap
cd Python-2.7.9
./configure 2>&1 | logger -t bootstrap
make 2>&1 | logger -t bootstrap
sudo make install 2>&1 | logger -t bootstrap
alias python=python2 2>&1 | logger -t bootstrap
logger -t bootstrap "End python upgrade to 2.7.9"

# Setup AWS creds for S3cmd
echo "[default]
access_key = AKIAIO3ILO2MW5GQQPNQ
secret_key = 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" > /tmp/s3cfg

#Download fresh Converter application
logger -t bootstrap "Download fresh application"
cd ~
rm -rf gafv
rm gafv_alt1.tar.gz
s3cmd -c /tmp/s3cfg get s3://gafv-application/gafv_alt1.tar.gz 2>&1 | logger -t bootstrap
tar -xvf gafv_alt1.tar.gz 2>&1 | logger -t bootstrap
#cd gafv
mv converter_local_settings.py local_settings.py
logger -t bootstrap "Application download finished"

#pip install all the requirements
pip install -r docs/requirements.txt | logger -t bootstrap

#Fetch latest youtube-dl script...
#curl "https://raw.github.com/rg3/youtube-dl/master/youtube-dl" -o /tmp/youtube-dl | logger -t bootstrap
#curl "http://youtube-dl.org/downloads/2013.06.30/youtube-dl" -o /tmp/youtube-dl | logger -t bootstrap
curl -L http://yt-dl.org/latest/youtube-dl -o /tmp/youtube-dl | logger -t bootstrap
#curl "https://yt-dl.org/downloads/2015.07.07/youtube-dl" -o /tmp/youtube-dl | logger -t bootstrap
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
	export C_FORCE_ROOT=\"true\"
	exec /usr/bin/python /root/manage.py celeryd -Q alt1 -c $workers -E -l info >> /var/log/celery.log 2>&1
end script

post-start script
end script
" > /etc/init/celery.conf
chmod +x /etc/init/celery.conf
#Some debug...
service celery start | logger -t bootstrap
service celery status | logger -t bootstrap

# we may need to restart celery
service celery restart | logger -t bootstrap

logger -t bootstrap "now look in /var/log/celery.log for more debugging..."

# Add auto scale cronjob
# crontab /root/convert/scale_cronjob.txt
