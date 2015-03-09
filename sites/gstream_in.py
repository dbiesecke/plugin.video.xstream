# -*- coding: utf-8 -*-
from resources.lib.util import cUtil
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.config import cConfig
from resources.lib import logger
from resources.lib.handler.ParameterHandler import ParameterHandler

SITE_IDENTIFIER = 'gstream_in'
SITE_NAME = 'G-Stream'
SITE_ICON = 'gstream.png'

URL_MAIN = 'http://gstream.to'
URL_SHOW_MOVIE = 'http://gstream.to/showthread.php?t='
URL_CATEGORIES = 'http://gstream.to/forumdisplay.php?f='
URL_SEARCH = 'http://gstream.to/search.php'


def load():
    oGui = cGui()

    sSecurityValue = __getSecurityCookieValue()

    __createMainMenuEntry(oGui, 'Aktuelle KinoFilme', 542, sSecurityValue)
    oGui.addFolder(cGuiElement('HD Filme',SITE_IDENTIFIER,'showHDMovies'))
    __createMainMenuEntry(oGui, 'Action', 591, sSecurityValue)
    __createMainMenuEntry(oGui, 'Horror', 593, sSecurityValue)
    __createMainMenuEntry(oGui, 'Komoedie', 592, sSecurityValue)
    __createMainMenuEntry(oGui, 'Thriller', 595, sSecurityValue)
    __createMainMenuEntry(oGui, 'Drama', 594, sSecurityValue)
    __createMainMenuEntry(oGui, 'Fantasy', 655, sSecurityValue)
    __createMainMenuEntry(oGui, 'Abenteuer', 596, sSecurityValue)
    __createMainMenuEntry(oGui, 'Animation', 677, sSecurityValue)
    __createMainMenuEntry(oGui, 'Dokumentation', 751, sSecurityValue)
    #__createMainMenuEntry(oGui, 'Serien', 543, sSecurityValue)
  
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction('displaySearch')
    oGuiElement.setTitle('Suche Filme')
    params = ParameterHandler()
    params.setParam('securityCookie', sSecurityValue)
    params.setParam('searchType', '528')
    oGui.addFolder(oGuiElement, params)
    # Serien parsing nicht implementiert
    #oGuiElement = cGuiElement()
    #oGuiElement.setSiteName(SITE_IDENTIFIER)
    #oGuiElement.setFunction('displaySearch')
    #oGuiElement.setTitle('Suche Serien')
    #params.setParam('searchType', '532')
    #oGui.addFolder(oGuiElement, params)
    if showAdult():
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(SITE_IDENTIFIER)
        oGuiElement.setFunction('showXXX')
        oGuiElement.setTitle('XXX')
        oGui.addFolder(oGuiElement, params)
    
    oGui.setEndOfDirectory()

def __createMainMenuEntry(oGui, sMenuName, iCategoryId, sSecurityValue=''):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setTitle(sMenuName)
    oGuiElement.setFunction('parseMovieResultSite')
    params = ParameterHandler()
    params.setParam('normalySiteUrl', URL_CATEGORIES + str(iCategoryId) + '&order=desc&page=')
    params.setParam('siteUrl', URL_CATEGORIES + str(iCategoryId) + '&order=desc&page=1')
    params.setParam('iPage', 1)
    params.setParam('securityCookie', sSecurityValue)
    oGui.addFolder(oGuiElement, params)
    
def __getSecurityCookieValue():
    oRequest = cRequestHandler(URL_MAIN, False, True)
    sHtmlContent = oRequest.request()
    header = oRequest.getResponseHeader()

    sPattern = '>DDoS protection by CloudFlare<'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if not aResult[0]:
        logger.info('No known protection found')
        return ''
    logger.info('CF DDos protection active')
    #Challengeform suchen
    sPattern = ('a\.value = ([0-9\*\+\-]+);.*?<form id="challenge-form" action="([^"]+)".*?'
                'name="([^"]+)" value="([^"]+)".*?name="([^"]+)"/>.*?</form>')
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if not aResult[0]:
        logger.info('ChallengeForm not found')
        return False
    aResult = aResult[1][0]
    constant = len(oRequest.getRealUrl().split('/')[2])
    exp = aResult[0]
    url = aResult[1]
    valueName1 = aResult[2]
    value1 = aResult[3]
    valueName2 = aResult[4]
    value2 = str(eval(exp)+constant)
    url = '%s%s?%s=%s&%s=%s' % (URL_MAIN, url, valueName1, value1, valueName2, value2)
    oRequest = cRequestHandler(url, caching = False, ignoreErrors = True)
    oRequest.addHeaderEntry('Host', 'gstream.to')
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    oRequest.addHeaderEntry('Connection', 'keep-alive')
    oRequest.addHeaderEntry('DNT', '1')
    sHtmlContent = oRequest.request()
    return True 

def __getHtmlContent(sUrl = None, sSecurityValue=None, use_caching=True):
    params = ParameterHandler()

    # Test if a url is available and set it
    if sUrl is None and not params.exist('siteUrl'):
        logger.info("There is no url we can request.")
        return False
    else:
        if sUrl is None:
            sUrl = params.getValue('siteUrl')

    # Test if a security value is available
    if sSecurityValue is None:
        if params.exist('securityCookie'):
            sSecurityValue = params.getValue('securityCookie')
        else :
            sSecurityValue = ''

    # Make the request
    oRequest = cRequestHandler(sUrl,caching=use_caching)
    #oRequest.addHeaderEntry('Cookie', sSecurityValue)
    #oRequest.addHeaderEntry('Accept', '*/*')
    #oRequest.addHeaderEntry('Host', 'gstream.to')

    return oRequest.request()
    
def showXXX():
    params = ParameterHandler()
    oGui = cGui()
    __createMainMenuEntry(oGui, 'Alle Pornos', 661)
    #im Moment können keine Clips abgespielt werden da die Cliphoster nicht aufgelöst werden können
    #__createMainMenuEntry(oGui, 'Clips', 669, sSecurityValue)
       
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction('displaySearch')
    oGuiElement.setTitle('Suche XXX Streams')
    params.setParam('searchType', '530')
    oGui.addFolder(oGuiElement, params)
    
    __createMainMenuEntry(oGui, 'Amateure', '661&prefixid=Amateure1')
    __createMainMenuEntry(oGui, 'Anal', '661&prefixid=Anal')
    __createMainMenuEntry(oGui, 'Asia', '661&prefixid=Asia')
    __createMainMenuEntry(oGui, 'Black', '661&prefixid=Ebony')
    __createMainMenuEntry(oGui, 'Blowjob', '661&prefixid=Blowjob')
    __createMainMenuEntry(oGui, 'Deutsch', '661&prefixid=Deutsch')
    __createMainMenuEntry(oGui, 'Fetish', '661&prefixid=Fetish')
    __createMainMenuEntry(oGui, 'Große Brüste', '661&prefixid=GrosseBrueste')
    __createMainMenuEntry(oGui, 'Gruppensex', '661&prefixid=Gruppensex')
    __createMainMenuEntry(oGui, 'Gay', '661&prefixid=Gay')
    __createMainMenuEntry(oGui, 'Hardcore', '661&prefixid=Hardcore')
    __createMainMenuEntry(oGui, 'International', '661&prefixid=International')
    __createMainMenuEntry(oGui, 'Lesben', '661&prefixid=Lesben')
    __createMainMenuEntry(oGui, 'Masturbation', '661&prefixid=Masturbation')
    __createMainMenuEntry(oGui, 'Teens', '661&prefixid=Teens')
    oGui.setEndOfDirectory()
    
def showHDMovies():
    oGui = cGui()
    sUrl = 'http://gstream.to/search.php?do=process&prefixchoice[]=hd'
    iPage = 1
    __parseMovieResultSite(oGui, sUrl, useSearchId = True)
    oGui.setEndOfDirectory()    

def displaySearch():
    oGui = cGui()   
    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        _search(oGui, sSearchText)
    else:
        return
    oGui.setEndOfDirectory()

def _search(oGui, sSearchText):
    params = ParameterHandler()
    sSearchType = params.getValue('searchType')
    if not sSearchType:
        sSearchType = '528'
    sUrl = URL_SEARCH+'?do=process&childforums=1&do=process&exactname=1&forumchoice[]='+sSearchType+\
        '&query=' + str(sSearchText) + '&quicksearch=1&s=&securitytoken=guest&titleonly=1'
    oRequest = cRequestHandler(sUrl)
    oRequest.request()
    sUrl = oRequest.getRealUrl()
    __parseMovieResultSite(oGui, sUrl)

def parseMovieResultSite():
    oGui = cGui()
    params = ParameterHandler()
    if (params.exist('siteUrl')):
        iPage = params.getValue('iPage')
        normalySiteUrl = params.getValue('normalySiteUrl')
        siteUrl = params.getValue('siteUrl')
        __parseMovieResultSite(oGui, siteUrl, normalySiteUrl, iPage)
    oGui.setEndOfDirectory()


def __parseMovieResultSite(oGui, siteUrl, normalySiteUrl = '', iPage = 1, useSearchId = False):
    if not normalySiteUrl:
        normalySiteUrl = siteUrl+'&page='
    params = ParameterHandler()  
    sPattern = 'class="p1".*?<img class="large" src="(http://[^"]+)".*?<a href="[^"]+" id=".*?([^"_]+)"(.*?)>([^<]+)</a>(.*?)</tr>'
    #sPattern = 'class="alt1Active".*?<a href="(forumdisplay.php[^"]+)".*?>([^<]+)<.*?(src="([^"]+)|</td>).*?</tr>' #Serien
    # request
    use_cache = True
    if(useSearchId == True):
        use_cache = False
    sHtmlContent = __getHtmlContent(sUrl = siteUrl, use_caching = use_cache)
    # parse content
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == False):
        return
    total = len(aResult[1])  
    for img, link, hdS, title, yearS  in aResult[1]:
        sMovieTitle = title.replace('&amp;','&')
        sTitle = sMovieTitle
        sUrl = URL_SHOW_MOVIE + str(link)
        year = ''
        aResult = oParser.parse(yearS, ' ([0-9]{4}) -')
        if aResult[0]:
            year = aResult[1][0]
        aResult = oParser.parse(hdS, '(title="HD Quali")')
        if aResult[0]:
            sTitle = sTitle + ' [HD]'
        oGuiElement = cGuiElement(sTitle,SITE_IDENTIFIER,'getHosters')
        oGuiElement.setMediaType('movie')
        oGuiElement.setYear(year)
        oGuiElement.setThumbnail(img)      
        params.setParam('movieUrl', sUrl)
        params.setParam('sMovieTitle', sMovieTitle)       
        oGui.addFolder(oGuiElement, params, bIsFolder = False, iTotal = total)

    # check for searchId
    if (useSearchId == True):
        searchId = __getSearchId(sHtmlContent)
        normalySiteUrl = 'http://gstream.to/search.php?searchid='+str(searchId)+"&page="
		
    # check for next site
    iTotalPages = __getTotalPages(iPage, sHtmlContent)
    if (iTotalPages >= int(iPage)+1):
        params = ParameterHandler()
        params.setParam('iPage', int(iPage)+1)
        params.setParam('normalySiteUrl', normalySiteUrl)
        params.setParam('siteUrl', normalySiteUrl+str(int(iPage)+1))
        oGui.addNextPage(SITE_IDENTIFIER,'parseMovieResultSite', params, iTotalPages)

    if  iTotalPages > 1:
        oGuiElement = cGuiElement('Go to page x of '+str(iTotalPages)+' (currently page '+str(iPage)+')',SITE_IDENTIFIER,'gotoPage')
        params = ParameterHandler()
        oGui.addFolder(oGuiElement, params)
                
    oGui.setView('movies')            

def gotoPage():
    oGui = cGui()
    pageNum = oGui.showNumpad()
    if not pageNum:
        return
    params = ParameterHandler()
    siteUrl = params.getValue('normalySiteUrl')+pageNum
    __parseMovieResultSite(oGui, siteUrl, iPage = int(pageNum))
    oGui.setEndOfDirectory()
    
def __getTotalPages(iPage, sHtml):
    sPattern = '>Seite [0-9]+ von ([0-9]+)<'
    oParser = cParser()
    aResult = oParser.parse(sHtml, sPattern)
    if (aResult[0] == True):
        iTotalCount = int(aResult[1][0])
        return iTotalCount
    return 0
	
def __getSearchId(sHtml):
    sPattern = 'searchid=([0-9]+)&'
    oParser = cParser()
    aResult = oParser.parse(sHtml, sPattern)
    if (aResult[0] == True):
        searchId = int(aResult[1][0])
        return searchId
    return 0


def __createDisplayStart(iPage):
    return (20 * int(iPage)) - 20

def __createInfo(oGui, sHtmlContent):
    sPattern = '<td class="alt1" id="td_post_.*?<img src="([^"]+)".*?<b>Inhalt:</b>(.*?)<br />'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sThumbnail = str(aEntry[0])
            sDescription = cUtil().removeHtmlTags(str(aEntry[1])).replace('\t', '').strip()
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setTitle('info (press Info Button)')
            oGuiElement.setThumbnail(sThumbnail)
            oGuiElement.setFunction('dummyFolder')
            oGuiElement.setDescription(sDescription)
            oGui.addFolder(oGuiElement)
            
def showAdult():
    oConfig = cConfig()
    if oConfig.getSetting('showAdult')=='true':    
        return True
    return False

def dummyFolder():
    oGui = cGui()
    oGui.setEndOfDirectory()
#### Hosterhandling
def getHosters():
    hosters = []
    params = ParameterHandler()
    if (params.exist('movieUrl') and params.exist('sMovieTitle')):
        sSiteUrl = params.getValue('movieUrl')
        sMovieTitle = params.getValue('sMovieTitle')
        sHtmlContent = __getHtmlContent(sUrl = sSiteUrl)
        sPattern = 'id="ame_noshow_post.*?<a href="([^"]+)" title="[^"]+" target="_blank">([^<]+)</a>'
        aResult = cParser().parse(sHtmlContent, sPattern)
        if aResult[0] == True:
            for aEntry in aResult[1]:
                sUrl = aEntry[0]
                # extract hoster domainname            
                if 'gstream.to/secure/' in sUrl :
                    sHoster = sUrl.split('secure/')[-1].split('/')[0].split('.')[-2]
                else:
                    sHoster = sUrl.split('//')[-1].split('/')[0].split('.')[-2]
                hoster = {}
                hoster['link'] = sUrl
                hoster['name'] = sHoster
                hosters.append(hoster)
            hosters.append('getHosterUrl')
    return hosters

def getHosterUrl(sUrl = False):
    params = ParameterHandler() 
    if not sUrl:
        sUrl =  params.getValue('url')
    results = []
    if 'gstream.to/secure/' in sUrl :
        sHoster = sUrl.split('secure/')[-1].split('/')[0]       
        oRequest = cRequestHandler(sUrl, False)
        oRequest.addHeaderEntry('Cookie', params.getValue('securityCookie'))
        oRequest.addHeaderEntry('Referer', params.getValue('movieUrl'))
        try:
            oRequest.request()
            sUrl = oRequest.getRealUrl()
            sUrl = 'http://%s%s' % (sHoster, sUrl.split(sHoster)[-1])
        except:
            pass
    result = {}
    result['streamUrl'] = sUrl
    result['resolved'] = False
    results.append(result)
    return results
