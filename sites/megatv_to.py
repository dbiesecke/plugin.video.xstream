# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.config import cConfig
from resources.lib import logger
import xbmcaddon
import os
import re
from os.path import join
addon = xbmcaddon.Addon(id='plugin.video.xstream')


SITE_IDENTIFIER = 'megatv_to'
SITE_NAME = 'MegaTV.to'
SITE_ICON = 'megatv_to.jpg'

URL_MAIN = 'http://www.megatv.to'


def load():
    logger.info("Load %s" % SITE_NAME)

    oGui = cGui()
    path = os.path.join(addon.getAddonInfo('path'),"resources", "art", "sites","megatv_to")

    oGuiElement = cGuiElement('Alle', SITE_IDENTIFIER, 'showAllChannels')
    oGuiElement.setThumbnail(join(path,'international.png'))
    oGuiElement = oGui.addFolder(oGuiElement)
	
    oGuiElement = cGuiElement('Deutschland', SITE_IDENTIFIER, 'showGermanChannels')
    oGuiElement.setThumbnail(join(path,'deutschland.png'))
    oGuiElement = oGui.addFolder(oGuiElement)
	
    oGuiElement = cGuiElement('Türkiye', SITE_IDENTIFIER, 'showTurkeyChannels')
    oGuiElement.setThumbnail(join(path,'tuerkei.png'))
    oGuiElement = oGui.addFolder(oGuiElement)
	

    oGui.setEndOfDirectory()
	
def showAllChannels():
    _showChannels(URL_MAIN)

def showGermanChannels():
    _showChannels(URL_MAIN + '/Live-Stream/category/deutschland')

def showTurkeyChannels():
    _showChannels(URL_MAIN + '/Live-Stream/category/tuerkei')

def _showChannels(sUrl):
    oGui = cGui()
    channels = _parseChannels(sUrl)
    for channel in channels:
            oGuiElement = cGuiElement(channel['name'], SITE_IDENTIFIER,'getHosters')#'playChannel')
            logger.info(channel['logo'])
            oGuiElement.setThumbnail(channel['logo'])
            oParams = ParameterHandler()
            oParams.setParam('channelName',channel['name'])
            oParams.setParam('channelUrl',channel['url'])
            oGui.addFolder(oGuiElement,oParams, bIsFolder=False, iTotal = len(channels))
    oGui.setEndOfDirectory()

def _parseChannels(sUrl):
    logger.info('parse channel url: ' + sUrl)
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    divs = re.compile('<div id="post-.*?>.*?<a href="(.*?)">.*?src="(.*?)".*?bookmark">(.*?)</a>', re.DOTALL)
    channels = []
    for div in divs.finditer(sHtmlContent): 
        channel = dict()
        channel['url'] = div.group(1)
        channel['logo'] = div.group(2)
        channel['name'] = div.group(3)
        channels.append(channel)
    return channels

#def playChannel():
def getHosters():
    oParams = ParameterHandler()
    sChannelUrl = oParams.getValue('channelUrl')
    sChannelName = oParams.getValue('channelName')
    logger.info('get stream url for URL: ' + sChannelUrl)

    oRequestHandler = cRequestHandler(sChannelUrl)
    oRequestHandler.addHeaderEntry('Referer', URL_MAIN)
    sHtmlContent = oRequestHandler.request();

    hosters = []

    sPattern = "'file': '(.*?)',"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        sUrl = str(aResult[1])[2:-2]
        logger.info('load channel ' + sChannelName + ' with url ' + sUrl)

        hoster = {}
        hoster['link'] = sUrl
        hoster['name'] = 'streamcloud'  # dummy
        hosters.append(hoster)
    hosters.append('getHosterUrl')
    return hosters

def getHosterUrl(sUrl):
    logger.info("getHosterUrl with url %s" % (sUrl))
    results = []
    result = {}
    result['streamUrl'] = sUrl
    result['resolved'] = True
    results.append(result)
    return results

