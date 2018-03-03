#coding: utf-8
import json
import urllib2

class Spotify:
    @classmethod
    def get_track_info(cls, uri):
        url = "http://ws.spotify.com/lookup/1/.json?uri=%s" % uri
        rq = urllib2.urlopen(url)
        ret = rq.read()
        rq.close()
        info = json.loads(ret)
        return info


