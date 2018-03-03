# Server Info
## Live webserver
   - http://www.getaudiofromvideo.com
   - Public DNS: ec2-174-129-223-145.compute-1.amazonaws.com
   - Private DNS: ip-10-42-103-131.ec2.internal
   - Public IP: 174.129.223.145

Amember
   - https://members.getaudiofromvideo.com/member/index
   - Public DNS: ec2-50-17-227-39.compute-1.amazonaws.com
   - Private DNS: ip-10-122-71-95.ec2.internal
   - Public IP: 50.17.227.39

Converter
   - 2 servers that renew every 1 hour
   - info can get in Amazon AWS EC2 dashboard

Django
   - Task list: http://getaudiofromvideo.com/admin/djcelery/taskstate

## Development webserver
   - http://dev.getaudiofromvideo.com
   - Public DNS: ec2-54-204-66-128.compute-1.amazonaws.com
   - Private DNS: ip-10-235-32-135.ec2.internal
   - Public IP: 10.235.32.135

Amember
   - https://devamember.getaudiofromvideo.com
   - Public DNS: ec2-107-22-176-197.compute-1.amazonaws.com
   - Private DNS: ip-10-235-82-140.ec2.internal
   - Public IP: 107.22.176.197

Converter
   - Public DNS: ec2-54-163-239-104.compute-1.amazonaws.com
   - Private DNS: ip-10-239-60-53.ec2.internal
   - Public IP: 54.163.239.104


## How the servers work together

The site uses Celery as a queue management library for python, to queue jobs and process them, and fetch results. and it needs a 	"broker" to manage the actual messaging. Gafv uses Rabbitmq for this message passing.

1. Server A tells Celery to put a job in queue. Celery puts it into Rabbitmq (also running on server A, but does not have to).

2. Celery on Server B is connected to Rabbitmq on server A. Its constantly asking for jobs, if there is a job pending that no other server has taken, it will take it and start processing it.

3. Once complete it will post result to Rabbitmq via Celery...

4. Celery on server A sees the result... and sends to user (we specified specific versions of celery cause some things were breaking with newer versions and i didnt have time to investigate the changes.)

## To purge RabbitMQ queue

http://stackoverflow.com/questions/5313027/rabbitmq-how-do-i-delete-all-messages-from-a-single-queue

In the webserver instance run:

1. rabbitmqctl stop_app

2. rabbitmqctl reset

3. rabbitmqctl start_app

## To see IP's associated with Celery

Navigate to /var/www/gafv then run: python manage.py celeryct1 status

* Rabbitmq needs to run on one place only (currently server A)

* Server B connects to rabbitmq on server A
* https://github.com/primesitemm/gafv/blob/master/converter_local_settings.py
Thats the settings override for server B

* BROKER_HOST = fetch_webserver_ip()
This sets BROKER_HOST to private ip of server A

* If server B is running the Celery daemon and based on the Broken host config, it will check the new messages in that 	server(angel), i.e Rabbitmq here.

## Important note about S3 gafv-application bucket with gafv.tar.gz and gafv-alt1.tar.gz

Anytime we update gafv source code (and the changes involve converter instances) we need to recompile gafv.tar.gz and upload to S3 (gafv-alt1.tar.gz is the same file but different name). 

Example: https://github.com/naterex/gafv/commit/320441435ee44c19982ed1e054d5f68879ea7316
(doc/requirements.txt is in gafv.tar.gz)


# Troubleshooting FAQ

## when converter doesn't work, how to figure that out?

1. Log into the converter server via ssh
    * check the public dns for the converter server in aws console
2. Run **sudo service celery status** to see whether celery is working
    * if not, run **sudo service celery start** to start it
3. check the celeryd is working by running **ps -ef|grep celeryd**, if the process doesn't exsit
   (means celeryd is down), then
    * change directory to the root directory in converter server, i.e **/root/**
    * run **python manage.py celeryd**
4. the above 3 steps have made sure the converter is running very well, so it should be the issue
   of gafv server
5. log into gafv server via ssh
6. check the rabbitmq is running by **sudo service rabbitmq-server status**, it should be the rabbitmq
    * if down, start it by running **sudo service rabbitmq-server start** 
7. then checking whether the converter is working now
    * check it out by making a conversion in gafv site
    * check it out in django admin's celery task 
8. if still not working, look in requirements documentation: https://github.com/naterex/gafv/blob/master/docs/requirements.txt
    * check for conflicts in python packages updates

## When converter works well, but djcelery not work, i.e no new records in django admin's celery task table

This issue is because of celerycam is not working in gafv server, so starting it should fix this issue:

1. log into gafv server via ssh
2. check whether the celerycam is running by **ps -ef|grep celerycam** to see whether the process is running
3. if not, change directory to gafv root, i.e **/var/www/gafv**
4. run **python manage.py celerycam &**
5. then go to gafv admin to see whether it works

## Gafv site is down, how to handle?

This is mostly the apache issue in gafv server, so start it should fix

1. log into gafv server via ssh
2. check whether apache is running by **sudo service apache2 status**
3. if apache is done, then start it by **sudo service apache2 start**

## Ways to fix/improve the site?

Use instance store as root volume instead of EBS ... and use EBS only for postgres database (which should be regularly snapshotted) b/c a couple of weeks ago when EBS went down in one availability zone... i had to deal with a shitstorm cause i was using it everywhere, even where i did not need it...
