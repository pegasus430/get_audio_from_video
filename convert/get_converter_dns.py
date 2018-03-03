#!/usr/bin/env python
from boto.ec2.connection import EC2Connection
import os
from time import sleep

AWS_KEY = "AKIAIO3ILO2MW5GQQPNQ"
AWS_SECRET = "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"

def get_region_info(name="us-east-1"):
    import boto.ec2
    for region in boto.ec2.regions():
        if region.name == name:
            return region
    return None


def get_public_dns(region=None):
    if region:
        conn = EC2Connection(AWS_KEY, AWS_SECRET, region=region)
    else:
        conn = EC2Connection(AWS_KEY, AWS_SECRET)
    print conn.region
    all = conn.get_all_instances()
    for x in all:
        print x.instances[0].public_dns_name, x.instances[0].private_dns_name

get_public_dns()
get_public_dns(get_region_info('sa-east-1'))
