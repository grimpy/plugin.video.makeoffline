import xbmc

path = xbmc.getInfoLabel('ListItem.FileNameAndPath')
xbmc.executebuiltin('Notification(Item, ' + path + ', 2)')
