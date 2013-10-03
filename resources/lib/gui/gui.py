# -*- coding: utf-8 -*-
from resources.lib.gui.contextElement import cContextElement
from resources.lib.config import cConfig
#from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.pluginHandler import cPluginHandler
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.gui.guiElement import cGuiElement

import xbmc
import xbmcgui
import xbmcplugin

import urllib

class cGui:
    '''
    This class "abstracts" a list of xbmc listitems.
    '''
    def addFolder(self, oGuiElement, oOutputParameterHandler='', bIsFolder = True, iTotal = 0 ):
        '''
        add GuiElement to Gui, adds listitem to a list
        '''
        sItemUrl = self.__createItemUrl(oGuiElement, bIsFolder, oOutputParameterHandler)
        oListItem = self.createListItem(oGuiElement)
        #if not bIsFolder:
        #    oListItem.setProperty('IsPlayable', 'true')
        oListItem = self.__createContextMenu(oGuiElement, oListItem, bIsFolder, sItemUrl, oOutputParameterHandler)        
        sPluginHandle = cPluginHandler().getPluginHandle()
        xbmcplugin.addDirectoryItem(sPluginHandle, sItemUrl, oListItem, isFolder = bIsFolder, totalItems = iTotal)
        

    def addNextPage(self, site, function, oParams=''):
        guiElement = cGuiElement('Next Page -->',site,function)
        self.addFolder(guiElement, oParams)
        
        
    def createListItem(self, oGuiElement):
        itemValues= oGuiElement.getItemValues()
        itemTitle = oGuiElement.getTitle()
        if oGuiElement._sLanguage != '':
            itemTitle += ' (%s)' % oGuiElement._sLanguage
        if oGuiElement._sQuality != '':
            itemTitle += ' [%s]' % oGuiElement._sQuality
        itemValues['title'] = itemTitle
        oListItem = xbmcgui.ListItem(itemTitle, oGuiElement.getTitleSecond(), oGuiElement.getIcon(), oGuiElement.getThumbnail())
        oListItem.setInfo(oGuiElement.getType(), itemValues)     
        oListItem.setProperty('fanart_image', oGuiElement.getFanart())
        aProperties = oGuiElement.getItemProperties()
        if len(aProperties)>0:
            for sPropertyKey in aProperties.keys():
                oListItem.setProperty(sPropertyKey, aProperties[sPropertyKey])
        return oListItem
        

    def __createContextMenu(self, oGuiElement, oListItem, bIsFolder, sItemUrl, oOutputParams=''):
        sPluginPath = cPluginHandler().getPluginPath()
        aContextMenus = []
        if len(oGuiElement.getContextItems()) > 0:
          for oContextItem in oGuiElement.getContextItems():
            oOutputParameterHandler = oContextItem.getOutputParameterHandler()
            sParams = oOutputParameterHandler.getParameterAsUri()                
            sTest = "%s?site=%s&function=%s&%s" % (sPluginPath, oContextItem.getFile(), oContextItem.getFunction(), sParams)                
            aContextMenus+= [ ( oContextItem.getTitle(), "XBMC.RunPlugin(%s)" % (sTest,),)]

        oContextItem = cContextElement()
        oContextItem.setTitle("Info")
        aContextMenus+= [ ( oContextItem.getTitle(), "XBMC.Action(Info)",)]
        itemValues = oGuiElement.getItemValues()
        if 'imdb_id' in itemValues and 'title' in itemValues:
            metaParams = {} 
            if itemValues['title']:
                metaParams['title'] = itemValues['title']
            if 'mediaType' in itemValues and itemValues['mediaType']:
                metaParams['mediaType'] = itemValues['mediaType']
            elif 'TVShowTitle' in itemValues and itemValues['TVShowTitle']:
                metaParams['mediaType'] = 'tvshow'
            else:
                metaParams['mediaType'] = 'movie'
            if 'season' in itemValues and itemValues['season'] and int(itemValues['season'])>0:
                metaParams['season'] = itemValues['season']
                metaParams['mediaType'] = 'season'
            if ( 'episode' in itemValues and itemValues['episode'] and int(itemValues['episode'])>0
                and 'season' in itemValues and itemValues['season'] and int(itemValues['season']) ):
                metaParams['episode'] = itemValues['episode']
                metaParams['mediaType'] = 'episode'
            if itemValues['imdb_id']:
                metaParams['imdbID'] = itemValues['imdb_id']
                oContextItem.setTitle("gesehen/ungesehen")
                aContextMenus+= [ ( oContextItem.getTitle(), "XBMC.RunPlugin(%s?function=changeWatched&%s)" % (sPluginPath, urllib.urlencode(metaParams),),)]
            if 'year' in itemValues and itemValues['year']:
                metaParams['year'] = itemValues['year']
            oContextItem.setTitle("Suche Metainfos")
            aContextMenus+= [ ( oContextItem.getTitle(), "XBMC.RunPlugin(%s?function=updateMeta&%s)" % (sPluginPath, urllib.urlencode(metaParams),),)]
        if not bIsFolder:
            oContextItem.setTitle("add to Playlist")     
            aContextMenus+= [ ( oContextItem.getTitle(), "XBMC.RunPlugin(%s&playMode=enqueue)" % (sItemUrl,),)]
            oContextItem.setTitle("download")
            aContextMenus+= [ ( oContextItem.getTitle(), "XBMC.RunPlugin(%s&playMode=download)" % (sItemUrl,),)]
            oContextItem.setTitle("send to JDownloader")
            aContextMenus+= [ ( oContextItem.getTitle(), "XBMC.RunPlugin(%s&playMode=jd)" % (sItemUrl,),)]   
        oListItem.addContextMenuItems(aContextMenus)
        #oListItem.addContextMenuItems(aContextMenus, True)  
        return oListItem
        

    def setEndOfDirectory(self):
        '''
        mark the listing as completed, this is mandatory
        '''
        iHandler = cPluginHandler().getPluginHandle()
        xbmcplugin.setPluginCategory(iHandler, "")
        # add some sort methods, these will be present in all views         
        xbmcplugin.addSortMethod(iHandler, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(iHandler, xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.addSortMethod(iHandler, xbmcplugin.SORT_METHOD_LABEL)       
        xbmcplugin.addSortMethod(iHandler, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(iHandler, xbmcplugin.SORT_METHOD_PROGRAM_COUNT)
        xbmcplugin.addSortMethod(iHandler, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
        xbmcplugin.addSortMethod(iHandler, xbmcplugin.SORT_METHOD_GENRE) 
          
        xbmcplugin.endOfDirectory(iHandler, True)
        
 
    def setView(self, content='movies'):
        '''
        set the listing to a certain content, makes special views available
        '''
        iHandler = cPluginHandler().getPluginHandle()
        if content == 'movies':
            xbmcplugin.setContent(iHandler, 'movies')
        elif content == 'tvshows':
            xbmcplugin.setContent(iHandler, 'tvshows')
        elif content == 'seasons':
            xbmcplugin.setContent(iHandler, 'seasons')
        elif content == 'episodes':
            xbmcplugin.setContent(iHandler, 'episodes')
        if cConfig().getSetting('auto-view')=='true':
            xbmc.executebuiltin("Container.SetViewMode(%s)" % cConfig().getSetting(content+'-view') )


    def updateDirectory(self):
        '''
        update the current listing
        '''
        xbmc.executebuiltin("Container.Refresh")
        

    def __createItemUrl(self, oGuiElement, bIsFolder, oOutputParameterHandler=''):
        if (oOutputParameterHandler == ''):
            #cOutputParameterHandler
            oOutputParameterHandler = ParameterHandler()
        if not bIsFolder:
            thumbnail = oGuiElement.getThumbnail()
            if thumbnail:
                oOutputParameterHandler.setParam('thumb',thumbnail) 
            itemValues = oGuiElement.getItemValues()
            metaParams = {} 
            if 'imdb_id' in itemValues and itemValues['imdb_id']:
                oOutputParameterHandler.setParam('imdbID',itemValues['imdb_id'])
            #if itemValues['title']:
            #    metaParams['title'] = itemValues['title']
            if 'mediaType' in itemValues and itemValues['mediaType']:
                oOutputParameterHandler.setParam('mediaType',itemValues['mediaType'])
            elif 'TVShowTitle' in itemValues and itemValues['TVShowTitle']:
                oOutputParameterHandler.setParam('mediaType','tvshow')
            if 'season' in itemValues and itemValues['season'] and int(itemValues['season'])>0:
                oOutputParameterHandler.setParam('season',itemValues['season'])
                oOutputParameterHandler.setParam('mediaType','season')
            if 'episode' in itemValues and itemValues['episode'] and int(itemValues['episode'])>0:
                oOutputParameterHandler.setParam('episode',itemValues['episode'])
                oOutputParameterHandler.setParam('mediaType','episode')
            oOutputParameterHandler.setParam('playMode','play')               
        sParams = oOutputParameterHandler.getParameterAsUri()
        sPluginPath = cPluginHandler().getPluginPath()
        if len(oGuiElement.getFunction()) == 0:
            sItemUrl = "%s?site=%s&title=%s&%s" % (sPluginPath, oGuiElement.getSiteName(), urllib.quote_plus(oGuiElement.getTitle()), sParams)
        else:
            sItemUrl = "%s?site=%s&function=%s&title=%s&%s" % (sPluginPath, oGuiElement.getSiteName(), oGuiElement.getFunction(), urllib.quote_plus(oGuiElement.getTitle()), sParams)
        return sItemUrl
        

    def showKeyBoard(self, sDefaultText = ""):
        # Create the keyboard object and display it modal
        oKeyboard = xbmc.Keyboard(sDefaultText)
        oKeyboard.doModal()    
        # If key board is confirmed and there was text entered return the text
        if oKeyboard.isConfirmed():
          sSearchText = oKeyboard.getText()
          if len(sSearchText) > 0:
            return sSearchText
        return False
        

    def showNumpad(self, defaultNum = ""):
        defaultNum = str(defaultNum)
        dialog = xbmcgui.Dialog()
        num = dialog.numeric(0,'Choose page')
        return num
        

    def openSettings(self):
        cConfig().showSettingsWindow()
        

    def showNofication(self, sTitle, iSeconds=0):
        if not cConfig().isDharma():
          return
        if (iSeconds == 0):
          iSeconds = 1000
        else:
          iSeconds = iSeconds * 1000  
        xbmc.executebuiltin("Notification(%s,%s,%s)" % (cConfig().getLocalizedString(30308), (cConfig().getLocalizedString(30309) % str(sTitle)), iSeconds))
        

    def showError(self, sTitle, sDescription, iSeconds = 0):
        #if not cConfig().isDharma():
         # return
        if iSeconds == 0:
          iSeconds = 1000
        else:
          iSeconds = iSeconds * 1000
        xbmc.executebuiltin("Notification(%s,%s,%s)" % (str(sTitle), (str(sDescription)), iSeconds))
        

    def showInfo(self, sTitle, sDescription, iSeconds=0):
        if not cConfig().isDharma():
            return
        if (iSeconds == 0):
            iSeconds = 1000
        else:
            iSeconds = iSeconds * 1000
        xbmc.executebuiltin("Notification(%s,%s,%s)" % (str(sTitle), (str(sDescription)), iSeconds))