#!/usr/bin/python

import xbmc
import xbmcgui
import sys
import os
import xbmcvfs

pluginhandle=int(sys.argv[1])
lastContentType = xbmc.getInfoLabel('Container.FolderPath')
path = xbmc.getInfoLabel('ListItem.FileNameAndPath')
title = xbmc.getInfoLabel('ListItem.Title')

basepath = '/home/Jo/Videos'
if os.path.exists(path):
    dialog = xbmcgui.Dialog()
    dialog.notification("Local file", "Nothing to do")
    sys.exit(0)

if 'movies' in lastContentType:
    newpath = os.path.join(basepath, "Movies", title)
else:
    series = xbmc.getInfoLabel("ListItem.TVShowTitle")
    season = "%02d" % int(xbmc.getInfoLabel("ListItem.Season"))
    episode = "%02d" % int(xbmc.getInfoLabel("ListItem.Episode"))
    newpath = os.path.join(basepath, "Series", season, )
    title = "%s-%s" % (episode, title)

if not os.path.exists(newpath):
    os.makedirs(newpath)
newpath = os.path.join(newpath, "%s.mkv" % title)

dialog = xbmcgui.Dialog()
answer = dialog.yesno("Download?", "Are you sure you want to download %s to" % title, newpath)
if not answer:
    dialog = xbmcgui.Dialog()
    dialog.notification("Download", "Cancelled %s" % title)
    sys.exit(0)

progress = xbmcgui.DialogProgress()
progress.create('Download', title)
datalen = 0
chunksize = 1024*1024
with open(newpath, "w") as fd:
    #urlopen = urllib2.urlopen(urlpath)
    vfsfile = xbmcvfs.File(path)
    size = vfsfile.size()
    data = vfsfile.read(chunksize)
    while data and not progress.iscanceled():
        datalen += chunksize
        percent = int((float(datalen) / size) * 100)
        progress.update(percent, '')
        fd.write(data)
        data = vfsfile.read(1024*1024)

if progress.iscanceled():
    os.remove(newpath)
