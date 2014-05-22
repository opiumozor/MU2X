#!/usr/bin/python2.7
#
#
# Filename: mu2x.py
# Description: Simple script used to send online medias on a xbmc device.
#
# Author: Alexis Bernard
# Email: alexis.bernard33@gmail.com
#
# Created: Wed May 21 17:40:01 2014 (+0200)
# Last-Updated: Thu May 22 17:26:42 2014 (+0200)
#           By: Alexis Bernard
#     Update #: 106
#
#

import sys
import re
import urlparse
import urllib2
import base64
import json
import argparse

HOST = '192.168.1.28'
PORT = '80'
USER = ''
PWD = ''

def check_url(url):
    if urlparse.urlparse(url).hostname == 'www.youtube.com':
        regex_youtube = r'.*(?:v=|/v/|^)(?P<id>[^&]*)'
        regex_youtube = re.compile(regex_youtube)
        vid_id = regex_youtube.match(url)
        vid_id = vid_id.group('id')
        return vid_id, 'youtube'
    elif urlparse.urlparse(url).hostname == 'vimeo.com':
        regex_vimeo = r'.*/(?P<id>\d+)'
        regex_vimeo = re.compile(regex_vimeo)
        vid_id = regex_vimeo.match(url)
        vid_id = vid_id.group('id')
        return vid_id, 'vimeo'
    print "[ERROR] Bad url"
    sys.exit(-1)

def send_request(url, data_json):
    req = urllib2.Request(url)
    b64auth = base64.encodestring('%s:%s' % (USER, PWD)).replace('\n', '')
    req.add_header('Authorization', 'Basic %s' % b64auth)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, data_json)
    return response.read()

def send_to_xbmc(url):
    vid_id, service = check_url(url)
    url = 'http://' + HOST + ':' + PORT + '/jsonrpc'
    clearp = ('{"jsonrpc": "2.0", "method": "Playlist.Clear",' +
              ' "params":{"playlistid":1}, "id": 1}')
    addp = ('{"jsonrpc": "2.0", "method": "Playlist.Add",' +
            ' "params":{"playlistid":1, "item" :{ "file" : ' +
            '"plugin://plugin.video.' + service +
            '/?action=play_video&videoid=' + vid_id + '"}}, "id" : 1}')
    playp = ('{"jsonrpc": "2.0", "method": "Player.Open",' +
             ' "params":{"item":{"playlistid":1, "position" : 0}}, "id": 1}')
    print "[MU2X] Opening media on " + HOST + " ..."
    print "[MU2X] Cleaning playlist on device ..."
    api_resp = json.loads(send_request(url, clearp))
    try:
        if api_resp['result'] == 'OK':
            print "[MU2X] OK."
    except KeyError:
        print "[ERROR] Can not clear playlist."
        sys.exit(-1)
    print "[MU2X] Adding media to playlist ..."
    api_resp = json.loads(send_request(url, addp))
    try:
        if api_resp['result'] == 'OK':
            print "[MU2X] OK."
    except KeyError:
        print "[ERROR] Can not add media to playlist."
        sys.exit(-1)
    print "[MU2X] Playing playlist on device ..."
    api_resp = json.loads(send_request(url, playp))
    try:
        if api_resp['result'] == 'OK':
            print "[MU2X] OK."
    except KeyError:
        print "[ERROR] Can not play playlist."
        sys.exit(-1)

def add_to_playlist(url):
    vid_id, service = check_url(url)
    url = 'http://' + HOST + ':' + PORT + '/jsonrpc'
    addp = ('{"jsonrpc": "2.0", "method": "Playlist.Add",' +
            ' "params":{"playlistid":1, "item" :{ "file" : ' +
            '"plugin://plugin.video.' + service +
            '/?action=play_video&videoid=' + vid_id + '"}}, "id" : 1}')
    print "[MU2X] Adding media to playlist on " + HOST + " ..."
    api_resp = json.loads(send_request(url, addp))
    try:
        if api_resp['result'] == 'OK':
            print "[MU2X] OK."
    except KeyError:
        print "[ERROR] Can not add media to playlist."
        sys.exit(-1)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=('MU2X - Simple script to' +
                                                     ' send medias to XBMC.'))
    argparser.add_argument('media_url', action="store", help='')
    argparser.add_argument('-a', '--add', action="store_true", default=False,
                           help="add a media to XBMC's playlist")
    arguments = argparser.parse_args()
    if arguments.add is True:
        add_to_playlist(arguments.media_url)
    else:
        send_to_xbmc(arguments.media_url)
