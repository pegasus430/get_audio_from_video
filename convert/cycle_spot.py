#!/usr/bin/env python
from boto.ec2.connection import EC2Connection
import os
from time import sleep

AWS_KEY = "AKIAIO3ILO2MW5GQQPNQ"
AWS_SECRET = "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"

conn = EC2Connection(AWS_KEY, AWS_SECRET)

###### Instance setting #######
#ami = "ami-9a873ff3"
#ami = "ami-65cca70c"
ami = "ami-8fed22e4" #us-east-1 trusty 12.04 LTS amd64 instance-type:instance-store 20150707
max_bid = '0.15'
instance_type = "c1.medium"
user_data = open(os.path.dirname(os.path.realpath(__file__)) + "/install.sh").read()
key_name = "primesite"
security_groups = ["default"]
WAIT_TIME = 450 # Time in seconds to sleep before killing old instances...
num_workers = 2 #Number of converter instances to mantain
###############################


def get_old_requeses():
    
    # check http://docs.amazonwebservices.com/AWSEC2/latest/APIReference/ApiReference-query-DescribeSpotInstanceRequests.html
    # for filters
    # // only query the "active" ones
    # no more "state" filter to fix the terminating instances sometimes cannot terminal some instance issue, see #67
    return conn.get_all_spot_instance_requests(filters={"state": "active"})

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

def kill_spots(spot_requests):
    for req in spot_requests:
        instance_id = req.instance_id
        print "Canceling Spot request: %s" %(req.id)
        req.cancel()
        for reservation in conn.get_all_instances(filters={"instance-id": instance_id}):
            for instance in reservation.instances:
                print "Terminating instance: %s" %(instance.id)
                instance.terminate()

def is_new_created_instances_up():
    """check the new created instances' status
    """
    MAX_TRY_TIMES = 150
    INTERVAL = 10 # 10 seconds
    i = 0
    while True:
        print "current try time:%d, sleep for %d seconds for another polling ..." % (i+1, INTERVAL)
        sleep(INTERVAL) # sleep INTERVAL seconds at first to make sure the get_all_spot_instance_requests will return the
                        # new created ones
        is_up = True
        #requests = conn.get_all_spot_instance_requests(filters={"tag-key": "converterspot"})
        requests = conn.get_all_spot_instance_requests()
        #print "current requests: ", requests
        for req in requests:
            print req.state
            if req.state == "open": # means not yet active, wait and poll again
                is_up = False
                break   # no need to check other requests
        if is_up:
            break
        i += 1
        if i > MAX_TRY_TIMES: return False
    return True
                
        
if "__main__" in __name__:
    print "Taking inventory"
    old = get_old_requeses()
    print "Inventory", old
    print "Launching new"
    launch_new()
    if is_new_created_instances_up():
        print "wait for %d seconds to terminate the old instances" % WAIT_TIME 
        sleep(WAIT_TIME)
        print "Killing old inventory"
        kill_spots(old)
        print "Done"
    else:
        print "Failed"
