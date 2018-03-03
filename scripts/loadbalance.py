#!/usr/bin/env python
import os, sys
import commands
from boto.ec2.connection import EC2Connection

AWS_KEY = "AKIAIO3ILO2MW5GQQPNQ"
AWS_SECRET = "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"
INSTANCE_TAG = "GAFV_WEB_SERVER"

LOW_THREHOLD = 30   # low threhold, which if cpu usage is lower than this, then the running spot instances will be terminated
HIGH_THREHOLD = 95  # high threhold, which if cpu usage is higher than this, then a new spot instance will be created
MAX_SPOT_INSTANCES_NUM = 1   # max spot instances num, if the current running spot instances number is equal to this, no more
                        # spot instances will be created even the usage is high
                        # -1 to remove this restriction(won't count the limit)
                        # NOT USE for now


conn = EC2Connection(AWS_KEY, AWS_SECRET)

ami = "ami-9a873ff3"
max_bid = '0.15'
instance_type = "c1.medium"
#user_data = open(os.path.dirname(os.path.realpath(__file__)) + "/install.sh").read()
key_name = "primesite"
security_groups = ["default"]
wait_before_kill = 9 #Time in minutes to sleep before killing old instances...
num_workers = 2 #Number of converter instances to mantain

need_update_apache = False
need_create = True

def loadbalance():
    cmd = """top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%\id.*/\1/" | awk '{print 100 - $1"%"}'"""
    output = commands.getstatusoutput(cmd)
    ret, usage = output
    usage = float(usage[:-1])
    if usage <= LOW_THREHOLD:
        # we need to terminate the running spot instances
        instances = get_old_requeses()
        if len(instances) > 0:
            kill_spots(instances)
            need_update_apache = True
            need_create = False
            print "The current usage is %s, lower than %d, so we terminate the running instances" % (output[1], LOW_THREHOLD)
            return
    elif usage >= HIGH_THREHOD:
        # we need to create a new instance
        instances = get_old_requeses()
        print "The current usage is %s, higher than %d, so we create new spot instance" % (output[1], HIGH_THREHOD)
        if len(instances) == 0:
            launch_new()
            need_update_apache = True
            need_create = True
            return
        else:
            print "Won't create new, since there is already a running spot instance"
            return

    else:
        #do nothing
        print "The current usage is %s, lower than %d and higher than %d, so do nothing" % (output[1], HIGH_THREHOD, LOW_THREHOLD)
        pass
        
def get_old_requeses():
    # check http://docs.amazonwebservices.com/AWSEC2/latest/APIReference/ApiReference-query-DescribeSpotInstanceRequests.html
    # for filters
    # // only query the "active" ones
    # no more "state" filter to fix the terminating instances sometimes cannot terminal some instance issue, see #67
    return conn.get_all_spot_instance_requests(filters={"tag-key": INSTANCE_TAG, "state" : "active"})


def launch_new():
    sr = conn.request_spot_instances(price=max_bid,
        image_id = ami,
        count = 1,
        type = 'persistent',
        instance_type = instance_type,
        key_name = key_name,
        security_groups = security_groups
        )
    sp = sr[0]
    sp.add_tag(INSTANCE_TAG, "gafv")
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
    MAX_TRY_TIMES = 50
    INTERVAL = 30 # 30 seconds
    i = 0
    while True:
        print "current try time:%d, sleep for %d seconds for another polling ..." % (i+1, INTERVAL)
        sleep(INTERVAL) # sleep INTERVAL seconds at first to make sure the get_all_spot_instance_requests will return the
                        # new created ones
        is_up = True
        requests = conn.get_all_spot_instance_requests(filters={"tag-key": INSTANCE_TAG})
        print "current requests: ", requests
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
    loadbalance()
    if need_update_apache:
        # update apache's config file and restart apache
        appendix = "high" if need_create else "low"
        # update the config file, Note we soft link the config to apache's config
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        os.system("cp default_ssl_%s default_ssl" % appendix)
