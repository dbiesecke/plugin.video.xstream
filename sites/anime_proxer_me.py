from resources.lib.util import cUtil
from resources.lib.gui.hoster import cHosterGui
from resources.lib.handler.hosterHandler import cHosterHandler
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
import logger

SITE_IDENTIFIER = 'anime_proxer_me'
SITE_NAME = 'Proxer.Me'

URL_MAIN = 'http://proxer.me'
URL_ANIME_LIST = 'http://proxer.me/anime'
URL_MOVIES = 'http://proxer.me/anime?set=movie'
URL_OVA = 'http://proxer.me/anime?set=ova'
URL_SEARCH = 'http://proxer.me/animesuche.html?set=suche&sprache=alle&genre='

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_ANIME_LIST)
    oOutputParameterHandler.addParameter('nextFunction', 'showSeries')
    __createMenuEntry(oGui, 'showCharacters', 'Animes von A - Z', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MOVIES)
    oOutputParameterHandler.addParameter('nextFunction', 'showMovies')
    __createMenuEntry(oGui, 'showCharacters', 'Movies', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_OVA)
    oOutputParameterHandler.addParameter('nextFunction', 'showOvas')
    __createMenuEntry(oGui, 'showCharacters', 'Ovas', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_SEARCH)    
    __createMenuEntry(oGui, 'showSearch', 'Suche', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sSearchText = sSearchText.replace(' ', '+')
        sUrl = URL_SEARCH + '&name=' + sSearchText        
        __parseList(sUrl, 'getAvaiableTypes')

    oGui.setEndOfDirectory()

def __createMenuEntry(oGui, sFunction, sLabel, oOutputParameterHandler = ''):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction(sFunction)
    oGuiElement.setTitle(sLabel)
    oGui.addFolder(oGuiElement, oOutputParameterHandler)

def showCharacters():
    params = cInputParameterHandler()    
    sSiteUrl = params.getValue('siteUrl')
    sNextFunction = params.getValue('nextFunction')

    oGui = cGui()
    __createCharacters(oGui, '0-9', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'A', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'B', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'C', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'D', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'E', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'F', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'G', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'H', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'I', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'J', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'K', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'L', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'M', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'N', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'O', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'P', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'Q', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'R', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'S', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'T', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'U', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'V', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'W', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'X', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'Y', sSiteUrl, sNextFunction)
    __createCharacters(oGui, 'Z', sSiteUrl, sNextFunction)

    oGui.setEndOfDirectory()

def __createCharacters(oGui, sCharacter, sSiteUrl, sNextFunction):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction('parseList')
    oGuiElement.setTitle(sCharacter)

    if sSiteUrl== URL_ANIME_LIST:
        sSiteUrl += '?set=abc'
    sUrl = sSiteUrl + '&abc=' + str(sCharacter) + '#liste'

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', sUrl)
    oOutputParameterHandler.addParameter('nextFunction', sNextFunction)
    oGui.addFolder(oGuiElement, oOutputParameterHandler)

def parseList():
    params = cInputParameterHandler()
    sUrl = params.getValue('siteUrl')
    sNextFunction = params.getValue('nextFunction')
    __parseList(sUrl, sNextFunction)

def __parseList(sUrl, sNextFunction):
    
    
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request();
    sHtmlContent = sHtmlContent.replace('\\', '')
    
    sPattern = '<tr\s*align=left onmouseover="Tip\(\'<img src=\'(.*?)\'.*?<td ><a href="([^"]+)".*?>(.*?)</a></td><td>.*?</td><td>.*?</td><td>(.*?)</td><td>.*?</td><td>(.*?)</td><td>(.*?)</td></tr>'
    
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if (aResult[0] == True):
        oGui = cGui()
        for aEntry in aResult[1]:
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setFunction(sNextFunction)
            oGuiElement.setThumbnail(str(aEntry[0]))

            sTitle = cUtil().removeHtmlTags(aEntry[2])

            sTitle = sTitle + ' SUBS(' + __getLanguage(str(aEntry[3])) + ')'
            sTitle = sTitle + ' DUBS(' + __getLanguage(str(aEntry[4])) + ')'

            oGuiElement.setTitle(sTitle)

            oOutputParameterHandler = cOutputParameterHandler()            
            oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + str(aEntry[1]).replace('#top', ''))
            oGui.addFolder(oGuiElement, oOutputParameterHandler)

        oGui.setEndOfDirectory()

def getAvaiableTypes():
    oGui = cGui()
    params = cInputParameterHandler()
    sUrl = params.getValue('siteUrl')
    sUrl = sUrl.replace('&amp;', '&')


    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request();

    sPattern = 'top">SERIE</a>(.*?)>'
    __getAvaiableTypes(oGui, sUrl, sHtmlContent, sPattern, 'Serie', 'showSeries')
    
    sPattern = 'top">MOVIE</a>(.*?)>'
    __getAvaiableTypes(oGui, sUrl, sHtmlContent, sPattern, 'Movie', 'showMovies')

    sPattern = 'top">OVA</a>(.*?)>'
    __getAvaiableTypes(oGui, sUrl, sHtmlContent, sPattern, 'Ova', 'showOvas')

    oGui.setEndOfDirectory()

def __getAvaiableTypes(oGui, sUrl, sHtmlContent, sPattern, sTitle, sNextFunction):
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)    
    if (aResult[0] == True):
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(SITE_IDENTIFIER)
        oGuiElement.setFunction(sNextFunction)
        oGuiElement.setTitle(sTitle)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oOutputParameterHandler.addParameter('showSeries', sNextFunction)
        oGui.addFolder(oGuiElement, oOutputParameterHandler)

def showSeries():    
    params = cInputParameterHandler()

    iPage = 1
    if (params.exist('page')):
        iPage = params.getValue('page')

    sUrl = params.getValue('siteUrl')
    print sUrl
    #sUrl = sUrl + '&set=serie'    
    __parseMediaSite(sUrl, iPage)

def showMovies():
    params = cInputParameterHandler()

    iPage = 1
    if (params.exist('page')):
        iPage = params.getValue('page')

    sUrl = params.getValue('siteUrl')
    sUrl = sUrl + '&set=movie'    
    __parseMediaSite(sUrl, iPage)

def showOvas():
    params = cInputParameterHandler()

    iPage = 1
    if (params.exist('page')):
        iPage = params.getValue('page')

    sUrl = params.getValue('siteUrl')
    sUrl = sUrl + '&set=ova'    
    __parseMediaSite(sUrl, iPage)

def showNextPage():
    params = cInputParameterHandler()
    sUrl = params.getValue('siteUrl')
    iPage = 1
    if (params.exist('page')):
	iPage = params.getValue('page')

    __parseMediaSite(sUrl, iPage)

def __parseMediaSite(sUrl, iPage):
    sCurrentUrl = sUrl + '&s=list&p=' + str(iPage)+'#top'
    oGui = cGui()
    oRequestHandler = cRequestHandler(sCurrentUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '(?:id="box-table-a"|id=box-table-a)(.*?)</table>'  

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    # if (aResult[0] == False):
        # sPattern = 'id=box-table-a(.*?)</table>'
        # oParser = cParser()
        # aResult = oParser.parse(sHtmlContent, sPattern)        

    if (aResult[0] == True):
        sHtmlContent2 = aResult[1][0]

        sPattern = '</tr><tr><td>(.*?)</td><td align=left>(.*?)</td>'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent2, sPattern)
        
        if (aResult[0] == True):
            for aEntry in aResult[1]:
                oGuiElement = cGuiElement()
                oGuiElement.setSiteName(SITE_IDENTIFIER)
                oGuiElement.setFunction('showHoster')

                sTitle = str(aEntry[0]) + '.' + cUtil().removeHtmlTags(aEntry[1])
                oGuiElement.setTitle(sTitle)

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sCurrentUrl)
                oOutputParameterHandler.addParameter('number', str(aEntry[0]))
                oGui.addFolder(oGuiElement, oOutputParameterHandler)

	if (__checkFoxNextSite(iPage, sHtmlContent) == True):
	    oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setFunction('showNextPage')
	    oGuiElement.setTitle('next ..')
	    oOutputParameterHandler = cOutputParameterHandler()
	    oOutputParameterHandler.addParameter('siteUrl', sUrl)
	    oOutputParameterHandler.addParameter('page', str(int(iPage) + 1))
	    oGui.addFolder(oGuiElement, oOutputParameterHandler)
	    

    oGui.setEndOfDirectory()

def __checkFoxNextSite(iCurrentPage, sHtmlContent):
    iNextSite = int(iCurrentPage) + 1;
    sPattern = 'page=' + str(iNextSite) + '.*?>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
	return True

    return False;

def showHoster():
    oGui = cGui()
    params = cInputParameterHandler()
    sUrl = params.getValue('siteUrl')
    sNumber = params.getValue('number')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request();

    sPattern = '<td>' + str(sNumber) + '</td>(.*?)</tr>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
        
    if (aResult[0] == True):
        sHtmlContent = str(aResult[1][0])
        
        sPattern = '<a href="([^"]+)"><img src="/images/([^\.]+)\.png" alt="Play"'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        
        if (aResult[0] == True):
            for aEntry in aResult[1]:
                oHoster = cHosterHandler().getHoster2(str(aEntry[1]))
                if (oHoster != False):

                    oGuiElement = cGuiElement()
                    oGuiElement.setSiteName(SITE_IDENTIFIER)
                    oGuiElement.setFunction('getMovieUrl')

                    sTitle = oHoster + __getLanguageFromUrl(str(aEntry[0]))
                    sUrl = URL_MAIN + str(aEntry[0])#.replace('#top', '')
                    oGuiElement.setTitle(sTitle)

                    oOutputParameterHandler = cOutputParameterHandler()
                    oOutputParameterHandler.addParameter('siteUrl', sUrl)
                    oOutputParameterHandler.addParameter('hosterIdentifier', oHoster)
                    oGui.addFolder(oGuiElement, oOutputParameterHandler)
        
    oGui.setEndOfDirectory()

def getMovieUrl():
    oGui = cGui()
    params = cInputParameterHandler()
    sUrl = params.getValue('siteUrl')
    sHosterIdentifier = params.getValue('hosterIdentifier')
    oHoster = cHosterHandler().getHoster2(sHosterIdentifier)            
    
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request();
    oParser = cParser()
    sPattern = '<iframe src="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        sMovieUrl = aResult[1][0].strip().replace('/embed/video/','/video/')             
        cHosterGui().showHosterMenuDirect(oGui, oHoster, sMovieUrl)


    oGui.setEndOfDirectory()
        

def __getLanguageFromUrl(sUrl):
    sPattern = 'l=(.*?)&'
    oParser = cParser()
    aResult = oParser.parse(sUrl, sPattern)
    if (aResult[0] == True):
        return ' - ' + str(aResult[1][0])

    return ''    

def __getLanguage(sHtmlContent):
    sResult = ''

    sPattern = 'german(.*?).gif'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        if (sResult != ''):
            sResult = sResult + ', '
        sResult = sResult + 'de'

    sPattern = 'english(.*?).gif'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        if (sResult != ''):
            sResult = sResult + ', '
        sResult = sResult + 'en'
        
    return sResult


