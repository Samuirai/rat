#!/usr/bin/env python

import httplib
import httplib2
import os
import random
import sys
import time
import traceback

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import rat

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
    httplib.IncompleteRead, httplib.ImproperConnectionState,
    httplib.CannotSendRequest, httplib.CannotSendHeader,
    httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "/home/pi/rat/client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.


def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
        scope=YOUTUBE_UPLOAD_SCOPE,
        message='missing client_secrets.json')

    storage = Storage("/home/pi/rat/oauth2.json")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args(args=["--noauth_local_webserver"])
        credentials = run_flow(flow, storage, flags)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
    tags = None
    if options['keywords']:
        tags = options['keywords'].split(",")

    body=dict(
        snippet=dict(
            title=options['title'],
            description=options['description'],
            tags=tags,
            categoryId=options['category']
        ),
        status=dict(
            privacyStatus=options['privacyStatus']
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
    )

    return resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if 'id' in response:
                log("Video id '%s' was successfully uploaded." % response['id'])
                return response['id']
            else:
                log("The upload failed with an unexpected response: %s" % response)
                return None
        except HttpError, e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS, e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            log(error)
            retry += 1
            if retry > MAX_RETRIES:
                log("No longer attempting to retry.")
                return None

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            log("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

def log(msg):
    #print msg
    rat.post_log(msg)

def upload_video(file_name, title, description='', keywords='rats', category='15', privacyStatus='unlisted', log=log):
    options = {
        'file': file_name,
        'title': title,
        'description': description,
        'keywords': keywords,
        'category': category,
        'privacyStatus': privacyStatus,
    }
    youtube = get_authenticated_service()
    try:
        yt_id = initialize_upload(youtube, options)
        rat.post_log("https://www.youtube.com/watch?v={0}".format(yt_id))
        if yt_id:
            os.remove(file_name)
        return yt_id
    except HttpError, e:
        log("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

if __name__ == '__main__':
    for i in xrange(0, 3):
        if len(sys.argv)>=2:
            try:
                log("try to upload {1} video, attemp: {0}".format(i, sys.argv[1]))
                upload_video(sys.argv[1],sys.argv[2])
            except:
                rat.post_log(str(traceback.format_exc()))
            exit(0)
        else:
            try:
                get_authenticated_service()
            except:
                rat.post_log(str(traceback.format_exc()))
            exit(0)
        time.sleep(10)