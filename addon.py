#!/usr/bin/python
import xbmc
import xbmcaddon
import xbmcgui
import sys
import os
import xbmcvfs
import json
import urlparse

pluginhandle=int(sys.argv[1])
args = sys.argv[2]
print args
if len(args) > 1:
    params = urlparse.parse_qs(args[1:])
else:
    params = dict()

addon = xbmcaddon.Addon("plugin.video.makeoffline")
storelocation = "storelocation"
basepath = addon.getSetting(storelocation)

lastContentType = xbmc.getInfoLabel('Container.FolderPath')

dialog = xbmcgui.Dialog()

def makeRequest(call, **kwargs):
    request = {"jsonrpc": "2.0", "method": call, "id": 1, "params": kwargs}
    return json.loads(xbmc.executeJSONRPC(json.dumps(request)))

def download(newpath, title, path, confirm=True):
    global dialog
    if os.path.exists(path):
        dialog.notification("Local file", "Nothing to do")
        return
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    newpath = os.path.join(newpath, "%s.mkv" % title)

    vfsfile = xbmcvfs.File(path)
    size = vfsfile.size()

    progress = xbmcgui.DialogProgressBG()
    try:
        progress.create('Download', title)
        datalen = 0
        chunksize = 1024*1024

        if os.path.exists(newpath):
            stat = os.stat(newpath)
            if size != stat.st_size:
                os.unlink(newpath)
            else:
                dialog.notification("Download", "Previously downloaded %s" % title)
                return

        if confirm:
            answer = dialog.yesno("Download?", "Are you sure you want to download %s to" % title, newpath)
        else:
            answer = True
        if not answer:
            dialog = xbmcgui.Dialog()
            dialog.notification("Download", "Cancelled %s" % title)
            return

        with open(newpath, "w") as fd:
            data = vfsfile.read(chunksize)
            while data: # and not progress.iscanceled():
                datalen += chunksize
                percent = int((float(datalen) / size) * 100)
                progress.update(percent, '')
                fd.write(data)
                data = vfsfile.read(1024*1024)

        # if progress.iscanceled():
        #     os.remove(newpath)
        # else:
    finally:
        progress.close()

def downloadItem(x, downloadlist):
    title = xbmc.getInfoLabel("Container().ListItem(%s).Title" % x)
    if title:
        path = xbmc.getInfoLabel("Container().ListItem(%s).FileNameAndPath" % x)
        if 'movies' in lastContentType:
            newpath = os.path.join(basepath, "Movies", title)
        else:
            series = xbmc.getInfoLabel("Container().ListItem(%s).TVShowTitle" % x)
            season = "S%02d" % int(xbmc.getInfoLabel("Container().ListItem(%s).Season" % x))
            episode = "E%02d" % int(xbmc.getInfoLabel("Container().ListItem(%s).Episode" % x))
            newpath = os.path.join(basepath, "Series", series, season, )
            title = "%s%s-%s" % (season, episode, title)
        return newpath, title, path, not downloadlist


if not basepath:
    options = list()
    sources = makeRequest('Files.GetSources', media='video')
    for source in sources['result']['sources']:
        if os.path.exists(source['file']):
            options.append(source['file'])
    if options:
        options.append("Enter Manually")
        result = dialog.select("Choose Location", options)
        if result < len(options) - 1:
            basepath = options[result]
    if not basepath:
        basepath = dialog.browseSingle(3, "Select download folder", "videos")
    answer = dialog.yesno("Always use this path?", basepath)
    if answer:
        addon.setSetting(storelocation, basepath)

nritems = int(xbmc.getInfoLabel("Container().NumItems"))
folder = xbmc.getInfoLabel("Container.Foldername")
downloadlist = 'list' in params
if downloadlist:
    items = list()
    answer = dialog.yesno("Download entire folder %s with %s items" % (folder, nritems), "")
    if answer:
        for x in xrange(0, nritems + 1): # hack to jump over ..
            items.append(downloadItem(x, downloadlist))
        for item in items:
            if item:
                download(*item)
else:
    downloadItem(0, False)

makeRequest('VideoLibrary.Scan')
