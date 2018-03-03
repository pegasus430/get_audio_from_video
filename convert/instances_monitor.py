#!/usr/bin/env python
from boto.ec2.connection import EC2Connection
import os
import commands
from time import sleep

AWS_KEY = "AKIAIO3ILO2MW5GQQPNQ"
AWS_SECRET = "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"

conn = EC2Connection(AWS_KEY, AWS_SECRET)


def get_active_works_num():
    return len(conn.get_all_spot_instance_requests(filters={"state" : 'active'}))

def get_open_works_num():
    return len(conn.get_all_spot_instance_requests(filters={"state" : 'open'}))


if "__main__" in __name__:
    print "current active instances number: %d" % get_active_works_num()
    # open means the request is pending and will be active once fullfilling
    print "current open instances number: %d" % get_active_works_num()
