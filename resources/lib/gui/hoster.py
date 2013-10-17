# -*- coding: utf-8 -*-
from resources.lib.handler.jdownloaderHandler import cJDownloaderHandler
from resources.lib.download import cDownload
from resources.lib.handler.hosterHandler import cHosterHandler
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.player import cPlayer
from resources.lib.handler.requestHandler import cRequestHandler
import urlresolver
import logger

from ParameterHandler import *
import xbmc, xbmcgui
from resources.lib.config import cConfig

#test
import xbmcplugin
from resources.lib.handler.pluginHandler import cPluginHandler

class cHosterGui:

    
    SITE_NAME = 'cHosterGui'
    
    
    def __init__(self):
        # if cConfig().getSetting('autoplay')=='true':
            # self.autoPlay = True
        # else:
            # self.autoPlay = False
        self.dialog = False

    # step 1 - bGetRedirectUrl in ein extra optionsObject verpacken
    def showHoster(self, oGui, oHoster, sMediaUrl, bGetRedirectUrl = False):
        print "cHosterGui.showHoster is deprecated"
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(self.SITE_NAME)
        oGuiElement.setFunction('showHosterMenu')
        oGuiElement.setTitle(oHoster.getDisplayName())

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('sMediaUrl', sMediaUrl)
        oOutputParameterHandler.addParameter('sHosterIdentifier', oHoster.getPluginIdentifier())
        oOutputParameterHandler.addParameter('bGetRedirectUrl', bGetRedirectUrl)
        oOutputParameterHandler.addParameter('sFileName', oHoster.getFileName())

        oGui.addFolder(oGuiElement, oOutputParameterHandler)

    # step 2
    def showHosterMenu(self):
        print "cHosterGui.showHosterMenu is deprecated"
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()

        sHosterIdentifier = oInputParameterHandler.getValue('sHosterIdentifier')
        sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')
        bGetRedirectUrl = oInputParameterHandler.getValue('bGetRedirectUrl')
        #sFileName = oInputParameterHandler.getValue('sFileName')

        oHoster = cHosterHandler().getHoster(sHosterIdentifier)
        oHoster.setFileName(sFileName)
        
        self.showHosterMenuDirect(oGui, oHoster, sMediaUrl, bGetRedirectUrl)
        
        oGui.setEndOfDirectory()

    def showHosterMenuDirect(self, oGui, oHoster, sMediaUrl, bGetRedirectUrl=False, sFileName=''):
        print "cHosterGui.showHosterMenuDirect is deprecated"
        # play
        self.__showPlayMenu(oGui, sMediaUrl, oHoster, bGetRedirectUrl, sFileName)
        # playlist
        self.__showPlaylistMenu(oGui, sMediaUrl, oHoster, bGetRedirectUrl, sFileName)
        # download
        self.__showDownloadMenu(oGui, sMediaUrl, oHoster, bGetRedirectUrl, sFileName)        
        # JD
        self.__showJDMenu(oGui, sMediaUrl, oHoster, bGetRedirectUrl, sFileName)

        
    def __showPlayMenu(self, oGui, sMediaUrl, oHoster, bGetRedirectUrl, sFileName=''):
        print "cHosterGui.showPlayMenu is deprecated"
        oGuiElement = cGuiElement('play',self.SITE_NAME,'play')
        oOutputParameterHandler = ParameterHandler()
        oOutputParameterHandler.setParam('sMediaUrl', sMediaUrl)
        oOutputParameterHandler.setParam('bGetRedirectUrl', bGetRedirectUrl)
        oOutputParameterHandler.setParam('sFileName', sFileName)
        oGui.addFolder(oGuiElement, oOutputParameterHandler)

    def __showDownloadMenu(self, oGui, sMediaUrl, oHoster, bGetRedirectUrl, sFileName=''):
        print "cHosterGui.showDownloadMenu is deprecated"
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(self.SITE_NAME)
        oGuiElement.setFunction('download')
        oGuiElement.setTitle('download über XBMC')
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('sMediaUrl', sMediaUrl)
        oOutputParameterHandler.addParameter('bGetRedirectUrl', bGetRedirectUrl)
        oOutputParameterHandler.addParameter('sFileName', sFileName)
        oGui.addFolder(oGuiElement, oOutputParameterHandler)

    def __showJDMenu(self, oGui, sMediaUrl, oHoster, bGetRedirectUrl, sFileName=''):
        print "cHosterGui.showJDMenu is deprecated"
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(self.SITE_NAME)        
        oGuiElement.setTitle('an JDownloader senden')
        oGuiElement.setFunction('sendToJDownloader')
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('sMediaUrl', sMediaUrl)
        oOutputParameterHandler.addParameter('bGetRedirectUrl', bGetRedirectUrl)
        oGui.addFolder(oGuiElement, oOutputParameterHandler)

    def __showPlaylistMenu(self, oGui, sMediaUrl, oHoster, bGetRedirectUrl, sFileName=''):
        print "cHosterGui.showPlaylistMenu is deprecated"
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(self.SITE_NAME)
        oGuiElement.setFunction('addToPlaylist')
        oGuiElement.setTitle('add to playlist')
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('sMediaUrl', sMediaUrl)
        oOutputParameterHandler.addParameter('bGetRedirectUrl', bGetRedirectUrl)
        oOutputParameterHandler.addParameter('sFileName', sFileName)
        oGui.addFolder(oGuiElement, oOutputParameterHandler)

    def play(self, siteResult=False):
        oGui = cGui()
        oInputParameterHandler = ParameterHandler()
        sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')
        sFileName = oInputParameterHandler.getValue('sFileName')
        if not sFileName:
            sFileName = oInputParameterHandler.getValue('Title')
        if not sFileName:
            sFileName = oInputParameterHandler.getValue('title')
        if not sFileName: #nur vorrübergehend
            sFileName = oInputParameterHandler.getValue('sMovieTitle')
        sSeason = oInputParameterHandler.getValue('season')
        sEpisode = oInputParameterHandler.getValue('episode')
        sShowTitle = oInputParameterHandler.getValue('TvShowTitle')
        sThumbnail = oInputParameterHandler.getValue('thumb')       
        if siteResult:
            sMediaUrl = siteResult['streamUrl']
            logger.info('call play: ' + sMediaUrl)
            if siteResult['resolved']:
                sLink = sMediaUrl
            else:
                try:
                    sLink = urlresolver.resolve(sMediaUrl)
                except:
                    sLink = False
                    #raise
        elif sMediaUrl:
            logger.info('call play: ' + sMediaUrl)
            sLink = urlresolver.resolve(sMediaUrl)
        else:
            oGui.showError('xStream', 'Hosterlink not found', 5)
            return False
        if sLink != False:            
            logger.info('file link: ' + sLink)
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(self.SITE_NAME)
            oGuiElement.setMediaUrl(sLink)
            oGuiElement.setTitle(sFileName)
            if sThumbnail:
                oGuiElement.setThumbnail(sThumbnail)
            if sShowTitle:
                oGuiElement.addItemProperties('Episode',sEpisode)
                oGuiElement.addItemProperties('Season',sSeason)
                oGuiElement.addItemProperties('TvShowTitle',sShowTitle)
            #listItem = xbmcgui.ListItem(path=sLink)
            #listItem.setProperty('IsPlayable', 'true')
            #pluginHandle = cPluginHandler().getPluginHandle()
            #return xbmcplugin.setResolvedUrl(pluginHandle, True, listItem)
            oPlayer = cPlayer()
            oPlayer.clearPlayList()
            oPlayer.addItemToPlaylist(oGuiElement)
            if self.dialog:
                try:
                    self.dialog.close()
                except:
                    pass
            oPlayer.startPlayer()
        else:
            logger.info('file link: ' + str(sLink))
            oGui.showError('xStream', 'File deleted or Link could not be resolved', 5)
            return False
        return True 

        
    def addToPlaylist(self, siteResult = False):
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()

        sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')
        sFileName = oInputParameterHandler.getValue('sFileName')
        if not sFileName:
            sFileName = oInputParameterHandler.getValue('Title')
        if not sFileName:
            sFileName = oInputParameterHandler.getValue('title')
        if not sFileName: #nur vorrübergehend
            sFileName = oInputParameterHandler.getValue('sMovieTitle')
        sSeason = oInputParameterHandler.getValue('season')
        sEpisode = oInputParameterHandler.getValue('episode')
        sShowTitle = oInputParameterHandler.getValue('TvShowTitle')
        sThumbnail = oInputParameterHandler.getValue('thumb')
        if siteResult:
            sMediaUrl = siteResult['streamUrl']
            if siteResult['resolved']:
                sLink = sMediaUrl
            else:
                sLink = urlresolver.resolve(sMediaUrl)
        else:
            sLink = urlresolver.resolve(sMediaUrl)
        logger.info('call addToPlaylist: ' + sMediaUrl)
        logger.info('file link: ' + str(sLink))
        if (sLink != False):
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(self.SITE_NAME)
            oGuiElement.setMediaUrl(sLink)
            oGuiElement.setTitle(sFileName)
            if sThumbnail:
                oGuiElement.setThumbnail(sThumbnail)
            if sShowTitle:
                oGuiElement.addItemProperties('Episode',sEpisode)
                oGuiElement.addItemProperties('Season',sSeason)
                oGuiElement.addItemProperties('TvShowTitle',sShowTitle)
            if self.dialog:
                self.dialog.close()
            oPlayer = cPlayer()
            oPlayer.addItemToPlaylist(oGuiElement)
            oGui.showInfo('Playlist', 'Stream wurde hinzugefügt', 5);
        else:
            oGui.showError('Playlist', 'File deleted or Link could not be resolved', 5);
            return False
        return True
        
        
    def download(self, siteResult = False):
        #oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()

        sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')
        sFileName = oInputParameterHandler.getValue('sFileName')
        sFileName = oInputParameterHandler.getValue('sMovieTitle')
        if siteResult:
            sMediaUrl = siteResult['streamUrl']
            if siteResult['resolved']:
                sLink = sMediaUrl
            else:
                sLink = urlresolver.resolve(sMediaUrl)
        else:
            sLink = urlresolver.resolve(sMediaUrl)
        logger.info('call download: ' + sMediaUrl)
        logger.info('file link: ' + str(sLink))
        if self.dialog:
            self.dialog.close()
        if (sLink != False):
            oDownload = cDownload()
            oDownload.download(sLink, 'Stream')
        else:
            cGui().showError('Download', 'File deleted or Link could not be resolved', 5);
            return False
        return True
        
        
    def sendToJDownloader(self, sMediaUrl = False):
        #oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()

        sHosterIdentifier = oInputParameterHandler.getValue('sHosterIdentifier')
        if not sMediaUrl:            
            sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')            
        sFileName = oInputParameterHandler.getValue('sFileName')
        if self.dialog:
            self.dialog.close()
        logger.info('call send to JDownloader: ' + sMediaUrl)
        
        cJDownloaderHandler().sendToJDownloader(sMediaUrl)
        
    def __getRedirectUrl(self, sUrl):
        oRequest = cRequestHandler(sUrl)
        oRequest.request()
        return oRequest.getRealUrl()
        

    def __getPriorities(self, hosterList, filter = True):
        '''
        Sort hosters based on their resolvers priority.
        '''
        ranking = []
        for hoster in hosterList:
            #if not self.checkForResolver(hoster['name']):
            #    continue        
            found = False
            for imp in urlresolver.UrlResolver.implementors():
                if imp.valid_url('dummy',hoster['name'].lower()):
                        ranking.append([imp.priority,hoster])
                        found = True
                        break
            if not found and not filter:
                ranking.append([999,hoster])
        ranking.sort()
        hosterQueue = []
        for i,hoster in ranking:
            hosterQueue.append(hoster)
        return hosterQueue
        
    def stream(self, playMode, siteName, function):
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create('xStream',"get stream/hoster")
        #load site as plugin and run the function
        self.dialog.update(5,'import plugin...')
        plugin = __import__(siteName, globals(), locals())
        function = getattr(plugin, function)
        self.dialog.update(10,'catch links...')
        siteResult = function()
        self.dialog.update(80)
        if not siteResult:
            self.dialog.close()
            cGui().showInfo('xStream','stream/hoster not available')
            return
        # if result is not a list, make in one
        if not type(siteResult) is list:
            temp = []
            temp.append(siteResult)
            siteResult = temp
        # field "name" marks hosters
        if 'name' in siteResult[0]:
            functionName = siteResult[-1]
            del siteResult[-1]
            if not siteResult:
                self.dialog.close()
                cGui().showInfo('xStream','no hoster available')
                return
            self.dialog.update(90,'prepare hosterlist..')                
            if playMode !='jd':
                # filter and sort hosters
                siteResult = self.__getPriorities(siteResult)
            if not siteResult:
                self.dialog.close()
                cGui().showInfo('xStream','no supported hoster available')
                return
            self.dialog.update(100)
            self.dialog.close()
            if len(siteResult)>1:
                #choose hoster                
                siteResult = self._chooseHoster(siteResult)
                if not siteResult:
                    return
            else:
                siteResult = siteResult[0]
            # get stream links
            logger.info(siteResult['link'])
            function = getattr(plugin, functionName)
            siteResult = function(siteResult['link'])
        # if result is not a list, make in one
        if not type(siteResult) is list:
            temp = []
            temp.append(siteResult)
            siteResult = temp
        # choose part
        if len(siteResult)>1:
            siteResult = self._choosePart(siteResult)
            if not siteResult:
                    return
        else:
            siteResult = siteResult[0]
        if playMode == 'play':
            self.play(siteResult)
        elif playMode == 'download':
            self.download(siteResult)
        elif playMode == 'enqueue':
            self.addToPlaylist(siteResult)
        elif playMode == 'jd':
            self.sendToJDownloader(siteResult['streamUrl'])

    def checkForResolver(self,sHosterFileName):
        if sHosterFileName != '':
            sHosterFileName = sHosterFileName.lower()
            source = [urlresolver.HostedMediaFile(url=sHosterFileName)]
            if (urlresolver.filter_source_list(source)):
                return source[0].get_host()
            # media_id is in this case only a dummy
            source = [urlresolver.HostedMediaFile(host=sHosterFileName, media_id='ABC123XYZ')]            
            if (urlresolver.filter_source_list(source)):
                return source[0].get_host()
        return False
    
    def _chooseHoster(self, siteResult):
        dialog = xbmcgui.Dialog()
        titles = []
        for result in siteResult:
            if 'displayedName' in result:
                titles.append(result['displayedName'])
            else:                
                titles.append(result['name'])
        index = dialog.select('Hoster wählen', titles)
        if index > -1:
            siteResult = siteResult[index]
            return siteResult
        else:
            return False

    def _choosePart(self, siteResult):
        self.dialog = xbmcgui.Dialog()
        titles = []
        for result in siteResult:                
            titles.append(result['title'])
        index = self.dialog.select('Part wählen', titles)
        if index > -1:
            siteResult = siteResult[index]
            return siteResult
        else:
            return False

    def streamAuto(self, playMode, siteName, function):
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create('xStream',"get stream/hoster")
        #load site as plugin and run the function
        self.dialog.update(5,'import plugin...')
        plugin = __import__(siteName, globals(), locals())
        function = getattr(plugin, function)
        self.dialog.update(10,'catch links...')
        siteResult = function()
        if not siteResult:
            self.dialog.close()
            cGui().showInfo('xStream','stream/hoster not available')
            return False
        # if result is not a list, make in one
        if not type(siteResult) is list:
            temp = []
            temp.append(siteResult)
            siteResult = temp
        # field "name" marks hosters
        if 'name' in siteResult[0]:
            self.dialog.update(90,'prepare hosterlist..') 
            functionName = siteResult[-1]
            del siteResult[-1]             
            hosters = self.__getPriorities(siteResult)
            if not hosters:
                self.dialog.close()
                cGui().showInfo('xStream','no supported hoster available')
                return False
            check = False
            self.dialog.create('xStream','try hosters...')
            total = len(hosters)
            count = 1
            for hoster in hosters:
                if self.dialog.iscanceled() or xbmc.abortRequested: return
                percent = count/total*100
                try:
                    logger.info('try hoster %s' % hoster['name'])
                    # get stream links
                    function = getattr(plugin, functionName)
                    siteResult = function(hoster['link'])
                    #check = self.__autoEnqueue(siteResult, playMode)
                    if self.__autoEnqueue(siteResult, playMode):
                        break
                        return True
                except:
                    self.dialog.update(percent,'hoster %s failed' % hoster['name'])
                    logger.info('playback with hoster %s failed' % hoster['name'])
                    pass
        # field "resolved" marks streamlinks
        elif 'resolved' in siteResult[0]:
            for stream in siteResult:
                try:
                    if self.__autoEnqueue(siteResult, playMode):
                        self.dialog.close()
                        return True
                except:
                    pass

    def __autoEnqueue(self, partList, playMode):
        # choose part
        if not partList:
            return False
        for i in range(len(partList)-1,-1,-1):
            try:
                if playMode == 'play' and i==0:
                    if not self.play(partList[i]):
                        return False
                elif playMode == 'download':
                    self.download(partList[i])
                elif playMode == 'enqueue' or (playMode=='play' and i>0):
                    self.addToPlaylist(partList[i])
            except:
                return False
                raise
        return True

class Hoster:

    def __init__(self, name, link):
        self.name = name
        self.link = link
            