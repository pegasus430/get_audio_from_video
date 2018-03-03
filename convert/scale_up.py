#!/usr/bin/env python
from boto.ec2.connection import EC2Connection
import os
import commands
from time import sleep

AWS_KEY = "AKIAIO3ILO2MW5GQQPNQ"
AWS_SECRET = "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"

conn = EC2Connection(AWS_KEY, AWS_SECRET)

###### Instance setting #######
#ami = "ami-9a873ff3"
ami = "ami-65cca70c"
max_bid = '0.15'
instance_type = "c1.medium"
user_data = open(os.path.dirname(os.path.realpath(__file__)) + "/install.sh").read()
key_name = "primesite"
security_groups = ["default"]
wait_before_kill = 9 #Time in minutes to sleep before killing old instances...
num_workers = 1 #Number of converter instances to add for scaling up
CPU_USAGE_THREHOLD = 92  # percentage of cpu usage, once the current converter's cpu usage
                        # is higher than this, {num_workers} new instances will be created
CHECK_TIMES = 9        # need {CHECK_TIMES} times to have a higher cpu usage, then the scaling
                        # up will apply
CHECK_INTERVAL = 15  # seconds
MAX_WORKERS_NUM = 3    # max workers number, if the worker number is bigger than this, no more 
                        # workers will be created
###############################


def get_active_works_num():
    return len(conn.get_all_spot_instance_requests(filters={"state" : 'active'}))

def get_open_works_num():
    return len(conn.get_all_spot_instance_requests(filters={"state" : 'open'}))

def launch_new():
    for i in range(num_workers):
        sr = conn.request_spot_instances(price=max_bid,
            image_id = ami,
            count = 1,
            type = 'persistent',
            user_data = user_data,
            instance_type = instance_type,
            key_name = key_name,
            security_groups = security_groups
            )
        sp = sr[0]
        sp.add_tag("converterspot", "prod")
        print sp, sp.tags

def scale_up_if_needed(is_prod=False):
    """is_prod indicates whether it's production enviroment
    if not, then, lanuch new won't be called
    """
    current_time = 0
    need_scale_up = True
    while current_time < CHECK_TIMES:
        cmd = r"""top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%\id.*/\1/" | awk '{print 100 - $1"%"}'"""
        output = commands.getstatusoutput(cmd)
        ret, usage = output
        usage = float(usage[:-1])
        print "Current checking time:%d" % current_time
        print "Current CPU Usage is:%.2f%%" % usage
        if usage < CPU_USAGE_THREHOLD:
            need_scale_up = False
            break
        else:
            print "Sleeping %d seconds to check the usage again" % CHECK_INTERVAL
            sleep(CHECK_INTERVAL)
            current_time += 1

    if get_open_works_num() + get_active_works_num() > MAX_WORKERS_NUM:
        need_scale_up = False
    if need_scale_up and is_prod:
        print "a new converter worker is added"
        launch_new()
    else:
        print "No need to scale up yet"
        

if "__main__" in __name__:
    is_prod = True
    scale_up_if_needed(is_prod)
    
