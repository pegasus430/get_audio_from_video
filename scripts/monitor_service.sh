#!/bin/sh
CD="/var/www/gafv/"
cd $CD
# for rabbitmq
OUT=`sudo service rabbitmq-server status|grep "Error"|grep "nodedown"|wc -l`
echo $OUT
MATCH=0
if [ "$OUT" != "$MATCH" ];
then
echo "RabbitMQ-Server is down at `date`" >> $PWD/scripts/log/monitor.err.log
sudo service rabbitmq-server start
echo "rabbitmq-server is restarted..."
else
echo "RabbitMQ-Server is running well at `date`"
fi

#CC=`sudo service celery status|grep "stop"|wc -l`
#MC=1
#if [ "$CC" = "$MC" ];
#then
#echo "Celery is down at `date`" >> /var/log/monitor.log
#sudo service celery start
#echo "celery is restarted..."
#fi

# for apache
A=`sudo service apache2 status|grep "NOT running"|wc -l`
MA=0
if [ "$A" != "$MA" ];
then
echo "Apache2 is down at `date`" >> $PWD/scripts/log/monitor.err.log
sudo service apache2 restart
echo "apache is restarted..."
else
echo "Apache2 is running well at `date`"
fi

# for celerycam
CELERY=`ps -ef|grep celerycam|wc -l`
M=2
if [ "$CELERY" != "$M" ];
then
    echo "Celerycam is down at `date`" >> $PWD/scripts/log/monitor.err.log
    cd $CD
    echo $CD
    python manage.py celerycam &
    echo "celerycam is stated ..."
else
    echo "Celerycam is running well at `date`" 
fi
