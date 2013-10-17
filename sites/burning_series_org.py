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


# Prüfen ob der metahandler verwendet werden soll, dieser liefert Metainformationen (Poster, Fanarts,...)
if cConfig().getSetting('metahandler')=='true':
    META = True
    try:
        import resources.lib.handler.metaHandler as metahandlers
        #from metahandler import metahandlers
    except:
        META = False
        logger.info("Could not import package 'metahandler'")
else:
    META = False
    
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
  
def __createMenuEntry(oGui, sFunction, sLabel, lParams, sMetaTitle='', iTotal = 0):
  '''
  Vereinfachung der Erzeugung eines Menueintrags. Setzt automatisch den obligatorischen Parameter 'site'
  und fügt, falls der metahandler aktiv ist, Metainformation hinzu.
  '''
  oParams = ParameterHandler()
  try:
    for param in lParams:
      oParams.setParam(param[0], param[1])
  except Exception, e:
    logger.error("Can't add parameter to menu entry with label: %s: %s" % (sLabel, e))
    oParams = ""

  # Create the gui element
  oGuiElement = cGuiElement(sLabel, SITE_IDENTIFIER, sFunction)
  if META == True and sMetaTitle != '':
    oMetaget = metahandlers.MetaData()
    meta = oMetaget.get_meta('tvshow', sMetaTitle)
    oGuiElement.setItemValues(meta)
    oGuiElement.setThumbnail(meta['cover_url'])
    oGuiElement.setFanart(meta['backdrop_url'])
    oParams.setParam('imdbID', meta['imdb_id'])
  oGui.addFolder(oGuiElement, oParams, iTotal = iTotal)

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
    for aEntry in aResult[1]:
        sTitle = cUtil().unescape(aEntry[1])                             
        __createMenuEntry(oGui, 'showSeasons', sTitle,
            [['siteUrl', URL_MAIN + '/' + str(aEntry[0])],['Title', sTitle]], sTitle, len(aResult[1]))

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
    if sChar and sChar == '#':
        import string

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
             for aEntry in aResult[1]:
                sTitle = cUtil().unescape(aEntry[1].decode('utf-8')).encode('utf-8')                             
                __createMenuEntry(oGui, 'showSeasons', sTitle,
                  [['siteUrl', URL_MAIN + '/' + str(aEntry[0])],['Title', sTitle]], sTitle, len(aResult[1]))

    oGui.setView('tvshows')
    oGui.setEndOfDirectory()

    
def showSeasons():
    oGui = cGui()
	
    oInputParameterHandler = ParameterHandler()
    sTitle = oInputParameterHandler.getValue('Title')
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sImdb = oInputParameterHandler.getValue('imdbID')
    
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
             seasonNums = []
             for aEntry in aResult[1]:
                seasonNums.append(str(aEntry[1]))
                if META == True and sImdb:
                    oMetaget = metahandlers.MetaData()
                    meta = oMetaget.get_seasons(sTitle, sImdb, seasonNums)
             ii=0
             for aEntry in aResult[1]:
                seasonNum = seasonNums[ii]
                oGuiElement = cGuiElement('Staffel ' + seasonNum, SITE_IDENTIFIER, 'showEpisodes')
                if META == True and sImdb:
                    meta[ii]['TVShowTitle'] = sTitle
                    oGuiElement.setItemValues(meta[ii])
                    oGuiElement.setThumbnail(meta[ii]['cover_url'])
                    oGuiElement.setFanart(meta[ii]['backdrop_url'])
                oParams = ParameterHandler()
                oParams.setParam('siteUrl', URL_MAIN + '/' + str(aEntry[0]))
                oParams.setParam('Title', sTitle)
                oParams.setParam('Season', seasonNum)
                oGui.addFolder(oGuiElement, oParams, iTotal = len(aResult[1]))
                ii+=1
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
             for aEntry in aResult[1]:
                if aEntry[3].strip() == '</td':
                    continue
                sNumber = str(aEntry[0]).strip()
                oGuiElement = cGuiElement('Episode ' + sNumber, SITE_IDENTIFIER, 'showHosters')
                if META == True and sImdb:
                    oMetaget = metahandlers.MetaData()
                    meta = oMetaget.get_episode_meta(sShowTitle, sImdb, sSeason, sNumber)
                    meta['TVShowTitle'] = sShowTitle
                    del meta['title']
                    oGuiElement.setItemValues(meta)
                    oGuiElement.setThumbnail(meta['cover_url'])
                    oGuiElement.setFanart(meta['backdrop_url'])

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
                oGui.addFolder(oGuiElement, oParams, bIsFolder = False, iTotal = len(aResult[1]))
  
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

def getHosterUrl(sUrl):
    oParams = ParameterHandler()
    sTitle = oParams.getValue('Title')
    sHoster = oParams.getValue('Hoster')
   
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