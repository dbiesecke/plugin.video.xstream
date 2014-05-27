# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.util import cUtil
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.config import cConfig
from resources.lib import logger
import string

    
# Variablen definieren die "global" verwendet werden sollen
SITE_IDENTIFIER = 'burning_series_org'
SITE_NAME = 'Burning-Seri.es'
SITE_ICON = 'burning_series.jpg'

URL_MAIN = 'http://www.burning-seri.es'
URL_SERIES = 'http://www.burning-seri.es/serie-alphabet'
URL_ZUFALL = 'http://www.burning-seri.es/zufall'

# Hauptmenu erstellen
def load():
    logger.info("Load %s" % SITE_NAME)
    # instanzieren eines Objekts der Klasse cGui zur Erstellung eines Menus
    oGui = cGui()
    # Menueintrag, durch Instanzierung eines Objekts der Klasse cGuiElement, erzeugen und zum Menu (oGui) hinzufügen
    oGui.addFolder(cGuiElement('Alle Serien', SITE_IDENTIFIER, 'showSeries'))
    oGui.addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showCharacters'))
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    # Ende des Menus    
    oGui.setEndOfDirectory()
 

def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False and sSearchText != ''):
        _search(oGui, sSearchText)
    else:
        return
    oGui.setEndOfDirectory()

def _search(oGui, sSearchText):
    sUrl = URL_SERIES
    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('Referer', 'http://burning-seri.es/')
    params = ParameterHandler()
    sHtmlContent = oRequestHandler.request()
    sPattern = "<ul id='serSeries'>(.*?)</ul>"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if not aResult[0]:
        return
    sHtmlContent = aResult[1][0]
    sPattern = '<li><a href="([^"]+)">(([^<]+)?%s([^<]+)?)</a></li>' % sSearchText  
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern, ignoreCase = True)
    if not aResult[0]:
        return
    total = len(aResult[1])
    for aEntry in aResult[1]:
        sTitle = cUtil().unescape(aEntry[1].decode('utf-8')).encode('utf-8')
        guiElement = cGuiElement(sTitle, SITE_IDENTIFIER, 'showSeasons')
        guiElement.setMediaType('tvshow')              
        params.addParams({'siteUrl' : URL_MAIN + '/' + str(aEntry[0]), 'Title' : sTitle})
        oGui.addFolder(guiElement, params, iTotal = total)

def showCharacters():
    oGui = cGui()
    oGuiElement = cGuiElement()
    oParams = ParameterHandler()
    oGuiElement = cGuiElement('#', SITE_IDENTIFIER, 'showSeries')
    oParams.setParam('char','#')
    oGui.addFolder(oGuiElement, oParams)
    for letter in string.uppercase[:26]:
        oGuiElement = cGuiElement(letter, SITE_IDENTIFIER, 'showSeries')
        oParams.setParam('char',letter)
        oGui.addFolder(oGuiElement, oParams)
    # Ende des Menus    
    oGui.setEndOfDirectory()

def showSeries():    
    oGui = cGui()  
    oParams = ParameterHandler()  
    
    sUrl = URL_SERIES
    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('Referer', 'http://burning-seri.es/')
    sHtmlContent = oRequestHandler.request();
    sChar = oParams.getValue('char')

    sPattern = "<ul id='serSeries'>(.*?)</ul>"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        sHtmlContent = aResult[1][0]
        sPattern = '<li><a href="([^"]+)">(.*?)</a></li>'
        if sChar:
            if sChar == '#':
                sPattern = '<li><a href="([^"]+)">([^a-zA-Z].*?)</a></li>'
            else:
                sPattern = '<li><a href="([^"]+)">('+sChar+'.*?)</a></li>'
        
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            total = len(aResult[1])
            for aEntry in aResult[1]:
                sTitle = cUtil().unescape(aEntry[1].decode('utf-8')).encode('utf-8')
                guiElement = cGuiElement(sTitle, SITE_IDENTIFIER, 'showSeasons')
                guiElement.setMediaType('tvshow')              
                oParams.addParams({'siteUrl' : URL_MAIN + '/' + str(aEntry[0]), 'Title' : sTitle})
                oGui.addFolder(guiElement, oParams, iTotal = total)

    oGui.setView('tvshows')
    oGui.setEndOfDirectory()

    
def showSeasons():
    oGui = cGui()
	
    params = ParameterHandler()
    sTitle = params.getValue('Title')
    sUrl = params.getValue('siteUrl')
    sImdb = params.getValue('imdbID')
    
    logger.info("%s: show seasons of '%s' " % (SITE_NAME, sTitle))
    
    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('Referer', 'http://burning-seri.es/')
    sHtmlContent = oRequestHandler.request();
	
    sPattern = '<ul class="pages">(.*?)</ul>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)    
    if (aResult[0] == True):
        sHtmlContent = aResult[1][0]

        sPattern = '[^n]"><a href="([^"]+)">(.*?)</a>'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            total = len(aResult[1])
            for aEntry in aResult[1]:
                seasonNum = str(aEntry[1])
                oGuiElement = cGuiElement('Staffel ' + seasonNum, SITE_IDENTIFIER, 'showEpisodes')
                oGuiElement.setMediaType('season')
                oGuiElement.setSeason(seasonNum)
                oGuiElement.setTVShowTitle(sTitle)
                oParams = ParameterHandler()
                oParams.setParam('siteUrl', URL_MAIN + '/' + str(aEntry[0]))
                oParams.setParam('Title', sTitle)
                oParams.setParam('Season', seasonNum)
                oGui.addFolder(oGuiElement, oParams, iTotal = total)
    oGui.setView('seasons')
    oGui.setEndOfDirectory()

def showEpisodes():
    oGui = cGui()
    oParams = ParameterHandler()
    sShowTitle = oParams.getValue('Title')
    sUrl = oParams.getValue('siteUrl')
    sImdb = oParams.getValue('imdbID')    
    sSeason = oParams.getValue('Season')
    
    logger.info("%s: show episodes of '%s' season '%s' " % (SITE_NAME, sShowTitle, sSeason)) 
    
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request();

    sPattern = '<table>(.*?)</table>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        sHtmlContent = aResult[1][0]
        sPattern = '<td>([^<]+)</td>\s*<td><a href="([^"]+)">(.*?)</a>.*?<td class="nowrap">(\s*<a|\s*</td).*?</tr>'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            total = len(aResult[1])
            for aEntry in aResult[1]:
                if aEntry[3].strip() == '</td':
                    continue
                sNumber = str(aEntry[0]).strip()
                oGuiElement = cGuiElement('Episode ' + sNumber, SITE_IDENTIFIER, 'showHosters')
                oGuiElement.setMediaType('episode')
                oGuiElement.setSeason(sSeason)
                oGuiElement.setEpisode(sNumber)
                oGuiElement.setTVShowTitle(sShowTitle)

                sPattern = '<strong>(.*?)</strong>'
                aResultTitle = oParser.parse(str(aEntry[2]), sPattern)
                if (aResultTitle[0]== True):
                    sTitleName = str(aResultTitle[1][0]).strip()
                else:
                    sPattern = '<span lang="en">(.*?)</span>'
                    aResultTitle = oParser.parse(str(aEntry[2]), sPattern)
                    if (aResultTitle[0]== True):
                        sTitleName = str(aResultTitle[1][0]).strip()
                    else:
                        sTitleName = ''
                sTitle = sNumber
                sTitleName = cUtil().unescape(sTitleName.decode('utf-8')).encode('utf-8')
                oParams.setParam('EpisodeTitle', sTitleName)
                sTitle = sTitle + ' - ' + sTitleName

                oGuiElement.setTitle(sTitle)
                oParams.setParam('siteUrl', URL_MAIN + '/' + str(aEntry[1]))
                oParams.setParam('EpisodeNr', sNumber)
                oParams.setParam('TvShowTitle', sShowTitle)
                oParams.setParam('Title', sTitleName)
                oGui.addFolder(oGuiElement, oParams, bIsFolder = False, iTotal = total)
  
    oGui.setView('episodes')
    oGui.setEndOfDirectory()

def __createInfo(oGui, sHtmlContent, sTitle):
    sPattern = '<div id="desc_spoiler">([^<]+)</div>.*?<img src="([^"]+)" alt="Cover"/>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sDescription = cUtil().unescape(aEntry[0].decode('utf-8')).encode('utf-8').strip()
            oGuiElement = cGuiElement('info (press Info Button)',SITE_IDENTIFIER,'dummyFolder')
            sMovieTitle = __getMovieTitle(sHtmlContent)
            oGuiElement.setDescription(sDescription)
            oGuiElement.setThumbnail(URL_MAIN+'/'+aEntry[1])
            oGui.addFolder(oGuiElement)

def dummyFolder():
    return
            
def showHosters():
    #oGui = cGui()
	
    oParams= ParameterHandler()
    sTitle = oParams.getValue('Title')	
    sUrl = oParams.getValue('siteUrl')
    
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    #if not META:
    #    __createInfo(oGui, sHtmlContent, sTitle)
    
    sPattern = '<h3>Hoster dieser Episode(.*?)</ul>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        hosters = []
        sHtmlContent = aResult[1][0]
        sPattern = 'href="([^"]+)">.*?class="icon ([^"]+)"></span> ([^<]+?)</a>'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            for aEntry in aResult[1]:
                hoster = dict()
                hoster['link'] = URL_MAIN + '/' + str(aEntry[0])
                hoster['name'] = str(aEntry[2]).split(' - Teil')[0]
                hoster['displayedName'] = str(aEntry[2])
                hosters.append(hoster)
    hosters.append('getHosterUrl')
    return hosters

def __getMovieTitle(sHtmlContent):
    sPattern = '</ul><h2>(.*?)<small id="titleEnglish" lang="en">(.*?)</small>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)   
    if (aResult[0] == True):
	for aEntry in aResult[1]:
	    return str(aEntry[0]).strip() + ' - ' + str(aEntry[1]).strip()
    return ''

def getHosterUrl(sUrl = False):
    oParams = ParameterHandler()
    sTitle = oParams.getValue('Title')
    sHoster = oParams.getValue('Hoster')
    if not sUrl:
        sUrl = oParams.getValue('url')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request();
	
    sPattern = '<div id="video_actions">.*?<a href="([^"]+)" target="_blank">'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    results = []
    if (aResult[0] == True):
        sStreamUrl = aResult[1][0]
        result = {}
        result['streamUrl'] = sStreamUrl
        result['resolved'] = False
        results.append(result)
    return results