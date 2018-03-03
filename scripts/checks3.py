"""
Checks total storage space consumed in a S3 bucket.
Usage: python checks3.py bucket_name
"""
import boto, sys
from boto.s3.key import Key

b = sys.argv[1]
print b
conn = boto.connect_s3("AKIAIO3ILO2MW5GQQPNQ", "bVZIAJhtM9JVfPyaYOctNMgG3ZEazWGtb9D4jOPR")

bucket = conn.lookup(b)

total_bytes = 0
for key in bucket:
    total_bytes += key.size

print total_bytes
