import subprocess, random, os
import boto
from boto.s3.key import Key
from django.conf import settings
try:
    import pexpect
except:
    pass
from mutagen.easyid3 import EasyID3

def getseconds(timestampstr):
    t = timestampstr.split(":")
    if len(t) == 1:
        return float(t[0])
    else:
        return float(t[0]) * 60 * 60 + float(t[1]) * 60 + float(t[2])


def convertvid(ytid, options, convertedname, taskid, fetchandconvert, duration, id3):
    tmpfile = "/mnt/%s" %(taskid)
    tmpconverted = "/mnt/%s" %(convertedname)
    start = getseconds("00:" + options["youtube_start"])
    end = getseconds("00:" + options["youtube_end"])
    duration = end - start
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    #1) check if file exists on local disk
    if os.path.isfile(tmpfile) == False:
        # 1.1) get file from S3
        bucket = conn.get_bucket(settings.S3_YT_RAW_BUCKET)
        k = Key(bucket)
        k.key = ytid
        k.get_contents_to_filename(tmpfile)    
    # 2) Run ffmpeg - ffmpeg -i input.flv -ab 128k output.mp3
    #todo: use actual options for transcoding
    quality = options['transcoder_quality'] + 'k'
    extraargs = []
    format = tmpconverted[-3:]
    if format == "m4r":
        # m4a is same as m4r
        tmpconverted = tmpconverted[:-3] + "m4a"
        extraargs = ["-vn"]
    if format == "mp4":
        # use MP4Box to do the job, since if the original video has a not 1:1 PAR, and
        # has a small width than 360, the script will fail, so we use MP4Box instead
        import shutil
        shutil.move(tmpfile, tmpfile + ".mp4")
        tmpfile = tmpfile + ".mp4"
        ffmpegcmd = "MP4Box -add %s %s" % (tmpfile, tmpconverted)
    elif format == "flv" or format == "wmv":
        # These are video formats
        ffmpegcmd = " ".join(["ffmpeg", "-ss", str(start), "-i", tmpfile, "-y", "-t", str(duration), "-vf", '"scale=-1:360"'] + extraargs + [tmpconverted])
    elif format == "avi":
        ffmpegcmd = " ".join(["ffmpeg", "-ss", str(start), "-i", tmpfile, "-y", "-t", str(duration), "-ab", quality, "-vf", '"scale=-1:360"'] + extraargs + [tmpconverted])
    elif format == "wav":
        ffmpegcmd = " ".join(["ffmpeg", "-ss", str(start), "-i", tmpfile, "-y", "-t", str(duration)] + extraargs + [tmpconverted])
    else:
        #audio only
        ffmpegcmd = " ".join(["ffmpeg", "-ss", str(start), "-i", tmpfile, "-y", "-t", str(duration), "-ab", quality] + extraargs + [tmpconverted])
    print ffmpegcmd
    thread = pexpect.spawn(ffmpegcmd)
    cpl = thread.compile_pattern_list([
        pexpect.EOF,
        ".*time=([^\s]*)",
        '(.+)'
    ])
    while True:
        i = thread.expect_list(cpl, timeout=None)
        if i == 0: # EOF
            print "the sub process exited"
            break
        elif i == 1:
            timestamp = thread.match.group(1)
            print timestamp
            t = getseconds(timestamp)
            print t, duration
            pct = 30 + ((t/duration) * 60)
            fetchandconvert.update_state(state="CONVERTING", meta={"progress": int(pct)})
            thread.close

    #p = subprocess.Popen(["ffmpeg", "-i", tmpfile, "-y", "-ab", quality] + extraargs + [tmpconverted], stdout=subprocess.PIPE)
    #com = p.communicate()
    #print com
    # 3) Store output into S3
    # === POSTPROCESSING ===
    # ID3 tags
    if id3 is not None:
        audio = EasyID3(tmpconverted)
        for key in id3:
            audio[key] = id3[key]
        audio.save()


    bucket = conn.get_bucket(settings.S3_YT_PRO_BUCKET)
    k = Key(bucket)
    k.key = convertedname
    k.set_contents_from_filename(tmpconverted)
    newfile = bucket.get_key(k.key)
    newfile.change_storage_class('REDUCED_REDUNDANCY')
    # 4) Return
    pass
