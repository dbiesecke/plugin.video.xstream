# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.player import cPlayer
import xbmc, xbmcgui
import logger
#test
#import xbmcplugin
#import sys

class cHosterGui:

    
    SITE_NAME = 'cHosterGui'
    
    
    def __init__(self):
        # if cConfig().getSetting('autoplay')=='true':
            # self.autoPlay = True
        # else:
            # self.autoPlay = False
        self.maxHoster = int(cConfig().getSetting('maxHoster'))
        self.dialog = False


    def play(self, siteResult=False):
        import urlresolver
        oGui = cGui()
        params = ParameterHandler()
        sMediaUrl = params.getValue('sMediaUrl')
        sFileName = params.getValue('MovieTitle')
        if not sFileName:
            sFileName = params.getValue('Title')
        if not sFileName: #nur vorrübergehend
            sFileName = params.getValue('sMovieTitle')
        if not sFileName:
            sFileName = params.getValue('title')

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
        try:
            msg = sLink.msg
        except:
            msg = False
        if sLink != False and not msg:
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
            if self.dialog:
               try:
                   self.dialog.close()
               except:
                   pass
            oPlayer.startPlayer()
            return True #Necessary for autoStream
        else:
            logger.info('File link: ' + str(sLink))
            print str(msg)
            return False

        
    def addToPlaylist(self, siteResult = False):
        import urlresolver
        oGui = cGui()
        params = ParameterHandler()

        sMediaUrl = params.getValue('sMediaUrl')
        sFileName = params.getValue('MovieTitle')
        if not sFileName:
            sFileName = params.getValue('title')
        if not sFileName:
            sFileName = params.getValue('Title')
        if not sFileName: #nur vorrübergehend
            sFileName = params.getValue('sMovieTitle')
        if not sFileName:
            sFileName = params.getValue('title')
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
        from resources.lib.download import cDownload
        import urlresolver
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
        
		
    def sendToPyLoad(self, sMediaUrl = False):
        from resources.lib.handler.pyLoadHandler import cPyLoadHandler
        params = ParameterHandler()      
        sHosterIdentifier = params.getValue('sHosterIdentifier')
        if not sMediaUrl:            
            sMediaUrl = params.getValue('sMediaUrl')            
        sFileName = params.getValue('sFileName')
        if self.dialog:
            self.dialog.close()
        logger.info('call send to PyLoad: ' + sMediaUrl)       
        cPyLoadHandler().sendToPyLoad(sMediaUrl)
        

        
    def sendToJDownloader(self, sMediaUrl = False):
        from resources.lib.handler.jdownloaderHandler import cJDownloaderHandler
        params = ParameterHandler()
        sHosterIdentifier = params.getValue('sHosterIdentifier')
        if not sMediaUrl:            
            sMediaUrl = params.getValue('sMediaUrl')            
        sFileName = params.getValue('sFileName')
        if self.dialog:
            self.dialog.close()
        logger.info('call send to JDownloader: ' + sMediaUrl)       
        cJDownloaderHandler().sendToJDownloader(sMediaUrl)
        

    def __getPriorities(self, hosterList, filter = True):
        '''
        Sort hosters based on their resolvers priority.
        '''
        import urlresolver
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

        
    def stream(self, playMode, siteName, function, url):
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create('xStream',"get stream/hoster")
        #load site as plugin and run the function
        self.dialog.update(5,'import plugin...')
        plugin = __import__(siteName, globals(), locals())
        function = getattr(plugin, function)
        self.dialog.update(10,'catch links...')
        if url:
            siteResult = function(url)
        else:
            siteResult = function()
        self.dialog.update(40)
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

            self.dialog.update(80,'prepare hosterlist..')
            if (playMode !='jd') and (playMode != 'pyload') and \
                            cConfig().getSetting('presortHoster')=='true':
                # filter and sort hosters
                siteResult = self.__getPriorities(siteResult)
            if not siteResult:
                self.dialog.close()
                cGui().showInfo('xStream','no supported hoster available')
                return
            self.dialog.update(100)
            self.dialog.close()
            if len(siteResult) > self.maxHoster:
                siteResult = siteResult[:self.maxHoster-1]
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
            pass
        # choose part
        if len(siteResult)>1:
            siteResult = self._choosePart(siteResult)
            if not siteResult:
                    return
        else:
            siteResult = siteResult[0]


        self.dialog.update(60,'start opening stream..')

        if playMode == 'play':
            self.play(siteResult)
        elif playMode == 'download':
            self.download(siteResult)
        elif playMode == 'enqueue':
            self.addToPlaylist(siteResult)
        elif playMode == 'jd':
            self.sendToJDownloader(siteResult['streamUrl'])
        elif playMode == 'pyload':
            self.sendToPyLoad(siteResult['streamUrl'])

    
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
            params.setParam('isHoster','true')
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
            if len(siteResult) > self.maxHoster:
                siteResult = siteResult[:self.maxHoster-1]
            check = False
            self.dialog.create('xStream','try hosters...')
            total = len(hosters)
            count = 1
            for hoster in hosters:               
                if self.dialog.iscanceled() or xbmc.abortRequested or check: return
                percent = count/total*100
                try:
                    logger.info('try hoster %s' % hoster['name'])
                    # get stream links
                    function = getattr(plugin, functionName)
                    siteResult = function(hoster['link'])
                    check = self.__autoEnqueue(siteResult, playMode)
                    if check:                      
                        return True
                except:
                    self.dialog.update(percent,'hoster %s failed' % hoster['name'])
                    logger.info('playback with hoster %s failed' % hoster['name'])
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
        logger.info('autoEnqueue successful')
        return True


class Hoster:

    def __init__(self, name, link):
        self.name = name
        self.link = link
            
