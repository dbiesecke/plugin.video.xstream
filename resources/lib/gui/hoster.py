# -*- coding: utf-8 -*-
from resources.lib.handler.jdownloaderHandler import cJDownloaderHandler
from resources.lib.download import cDownload
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.player import cPlayer
from resources.lib.handler.requestHandler import cRequestHandler
import urlresolver
import logger

from resources.lib.handler.ParameterHandler import ParameterHandler
import xbmc, xbmcgui
from resources.lib.config import cConfig

#test
import xbmcplugin
import sys

class cHosterGui:

    
    SITE_NAME = 'cHosterGui'
    
    
    def __init__(self):
        # if cConfig().getSetting('autoplay')=='true':
            # self.autoPlay = True
        # else:
            # self.autoPlay = False
        self.dialog = False


    def play(self, siteResult=False):
        oGui = cGui()
        params = ParameterHandler()
        sMediaUrl = params.getValue('sMediaUrl')
        sFileName = params.getValue('sFileName')
        if not sFileName:
            sFileName = params.getValue('Title')
        if not sFileName:
            sFileName = params.getValue('title')
        if not sFileName: #nur vorrübergehend
            sFileName = params.getValue('sMovieTitle')
        sSeason = params.getValue('season')
        sEpisode = params.getValue('episode')
        sShowTitle = params.getValue('TvShowTitle')
        sThumbnail = params.getValue('thumb')
              
        if siteResult:
            sMediaUrl = siteResult['streamUrl']
            logger.info('call play: ' + sMediaUrl)
            if siteResult['resolved']:
                sLink = sMediaUrl
            else:
                sLink = urlresolver.resolve(sMediaUrl)

        elif sMediaUrl:
            logger.info('call play: ' + sMediaUrl)
            sLink = urlresolver.resolve(sMediaUrl)
        else:
            oGui.showError('xStream', 'Hosterlink not found', 5)
            return False
        if sLink != False:
            try:
                logger.info(sLink.msg)
                sLink = 'http://www.example.de'
            except:
                pass
            logger.info('file link: ' + str(sLink))
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
            #listItem.setInfo(type="Video", infoLabels='')
            #listItem.setProperty('IsPlayable', 'true')
            #pluginHandle = oGui.pluginHandle
            #xbmcplugin.setResolvedUrl(pluginHandle, True, listItem)

            oPlayer = cPlayer()
            oPlayer.clearPlayList()
            oPlayer.addItemToPlaylist(oGuiElement)
            #if self.dialog:
            #    try:
            #        self.dialog.close()
            #    except:
            #        pass
            oPlayer.startPlayer()
        else:
            logger.info('file link: ' + str(sLink))
            #oGui.showError('xStream', 'File deleted or Link could not be resolved', 5)
            return False

        
    def addToPlaylist(self, siteResult = False):
        oGui = cGui()
        params = ParameterHandler()

        sMediaUrl = params.getValue('sMediaUrl')
        sFileName = params.getValue('sFileName')
        if not sFileName:
            sFileName = params.getValue('Title')
        if not sFileName:
            sFileName = params.getValue('title')
        if not sFileName: #nur vorrübergehend
            sFileName = params.getValue('sMovieTitle')
        sSeason = params.getValue('season')
        sEpisode = params.getValue('episode')
        sShowTitle = params.getValue('TvShowTitle')
        sThumbnail = params.getValue('thumb')
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
            #oGui.showError('Playlist', 'File deleted or Link could not be resolved', 5);
            return False
        return True
        
        
    def download(self, siteResult = False):
        #oGui = cGui()
        params = ParameterHandler()

        sMediaUrl = params.getValue('sMediaUrl')
        sFileName = params.getValue('sFileName')
        sFileName = params.getValue('sMovieTitle')
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
            #cGui().showError('Download', 'File deleted or Link could not be resolved', 5);
            return False
        return True
        
        
    def sendToJDownloader(self, sMediaUrl = False):
        params = ParameterHandler()

        sHosterIdentifier = params.getValue('sHosterIdentifier')
        if not sMediaUrl:            
            sMediaUrl = params.getValue('sMediaUrl')            
        sFileName = params.getValue('sFileName')
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
                if cConfig().getSetting('hosterListFolder')=='true':
                    self.showHosterFolder(siteResult, siteName, functionName)
                    return
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
        else:
            self.dialog.close()
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

            
    def showHosterFolder(self, siteResult, siteName, functionName):
        oGui = cGui()
        total = len(siteResult)
        params = ParameterHandler()
        for hoster in siteResult:
            if 'displayedName' in hoster:
                name = hoster['displayedName']
            else:
                name = hoster['name']
            oGuiElement = cGuiElement(name, siteName, functionName)
            params.setParam('url',hoster['link'])
            oGui.addFolder(oGuiElement, params, iTotal = total, isHoster = True)
        oGui.setEndOfDirectory()

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
            