# -*- coding: utf-8 -*-
#
# Author: bullshit <me@oskarholowaty.com>
# SCM: https://github.com/bullshit
#

from resources.lib.gui.gui import cGui
from resources.lib.util import cUtil
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.config import cConfig
from resources.lib import logger
from resources.lib.player import cPlayer
import string
import xbmcaddon
import os
from os.path import join
addon = xbmcaddon.Addon(id='plugin.video.xstream')

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

SITE_IDENTIFIER = 'megatv_to'
SITE_NAME = 'MegaTV.to'
SITE_ICON = 'megatv_to.jpg'

URL_MAIN = 'http://www.megatv.to'


def load():
    logger.info("Load %s" % SITE_NAME)

    oGui = cGui()
    path = os.path.join(addon.getAddonInfo('path'),"resources", "art", "sites","megatv_to")

    oGuiElement = cGuiElement('Deutschland', SITE_IDENTIFIER, 'showGermanChannels')
    oGuiElement.setThumbnail(join(path,'deutschland.png'))
    oGuiElement = oGui.addFolder(oGuiElement)

    oGuiElement = cGuiElement('Österreich', SITE_IDENTIFIER, 'showAustrianChannels')
    oGuiElement.setThumbnail(join(path,'oesterreich.png'))
    oGuiElement = oGui.addFolder(oGuiElement)

    oGuiElement = cGuiElement('Schweiz', SITE_IDENTIFIER, 'showSwissChannels')
    oGuiElement.setThumbnail(join(path,'schweiz.png'))
    oGuiElement = oGui.addFolder(oGuiElement)

    oGuiElement = cGuiElement('España', SITE_IDENTIFIER, 'showSpainChannels')
    oGuiElement.setThumbnail(join(path,'spanien.png'))
    oGuiElement = oGui.addFolder(oGuiElement)

    oGuiElement = cGuiElement('France', SITE_IDENTIFIER, 'showFranceChannels')
    oGuiElement.setThumbnail(join(path,'frankreich.png'))
    oGuiElement = oGui.addFolder(oGuiElement)

    oGuiElement = cGuiElement('Россия', SITE_IDENTIFIER, 'showRussiaChannels')
    oGuiElement.setThumbnail(join(path,'russland.png'))
    oGuiElement = oGui.addFolder(oGuiElement)

    oGuiElement = cGuiElement('Türkiye', SITE_IDENTIFIER, 'showTurkeyChannels')
    oGuiElement.setThumbnail(join(path,'tuerkei.png'))
    oGuiElement = oGui.addFolder(oGuiElement)

    oGuiElement = cGuiElement('International', SITE_IDENTIFIER, 'showInternationChannels')
    oGuiElement.setThumbnail(join(path,'international.png'))
    oGuiElement = oGui.addFolder(oGuiElement)

    oGui.setEndOfDirectory()

def showGermanChannels():
    _showChannels(URL_MAIN + '/deutschland/')

def showAustrianChannels():
    _showChannels(URL_MAIN + '/osterreich/')

def showSwissChannels():
    _showChannels(URL_MAIN + '/schweiz/')

def showSpainChannels():
    _showChannels(URL_MAIN + '/spanien/')

def showFranceChannels():
    _showChannels(URL_MAIN + '/frankreich/')

def showRussiaChannels():
    _showChannels(URL_MAIN + '/russisch/')

def showTurkeyChannels():
    _showChannels(URL_MAIN + '/turkei/')

def showInternationChannels():
    _showChannels(URL_MAIN + '/international/')

def _showChannels(sUrl):
    oGui = cGui()
    channels = _parseChannels(sUrl)
    for channel in channels:
            oGuiElement = cGuiElement(channel['name'], SITE_IDENTIFIER, 'playChannel')
            logger.info(channel['logo'])
            oGuiElement.setThumbnail(channel['logo'])
            oParams = ParameterHandler()
            oParams.setParam('channelKey',channel['key'])
            oParams.setParam('channelName',channel['name'])
            oParams.setParam('channelUrl',channel['url'])
            oGui.addFolder(oGuiElement,oParams)
    oGui.setEndOfDirectory()

def _parseChannels(sUrl):
    logger.info('parse channel url: ' + sUrl)
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sPattern = '<div class="button">(.*?)</div>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    channels = []
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sHtmlContent = aEntry
            aPattern = 'href="([^"]+)">'
            imgPattern = 'src="([^"]+)"'
            oParser = cParser()
            aResult = oParser.parse(aEntry, aPattern)
            #channelKey = str(aResult[1])[5:-2]
            channelKey = str(aResult[1][0])[3:].strip()

            imgResult = oParser.parse(aEntry, imgPattern)
            channelLogo = str(imgResult[1][0]).strip()

            channel = dict()
            channel['url'] = URL_MAIN + '/' + channelKey
            channel['key'] = channelKey
            channel['logo'] = channelLogo
            channel['name'] = _getChannelName(channelKey)
            channels.append(channel)
    return channels

def playChannel():
    oParams = ParameterHandler()
    sChannelKey = oParams.getValue('channelKey')
    sChannelName = oParams.getValue('channelName')
    logger.info('get stream url for channel: ' + sChannelKey)

    sUrl = URL_MAIN + '/' + sChannelKey
    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('Referer', URL_MAIN)
    sHtmlContent = oRequestHandler.request();


    sPattern = "'file': '(.*?)',"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        sUrl = str(aResult[1])[2:-2]
        logger.info('streaming url: ' + sUrl)
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(SITE_NAME)
        logger.info('load channel ' + sChannelName + 'with url ' + sUrl)
        oGuiElement.setMediaUrl(sUrl)
        oGuiElement.setTitle(sChannelName)

        '''
        if sThumbnail:
            oGuiElement.setThumbnail(sThumbnail)
        if sShowTitle:
            oGuiElement.addItemProperties('Episode',sEpisode)
            oGuiElement.addItemProperties('Season',sSeason)
            oGuiElement.addItemProperties('TvShowTitle',sShowTitle)
        '''

        oPlayer = cPlayer()
        oPlayer.clearPlayList()
        oPlayer.addItemToPlaylist(oGuiElement)
        oPlayer.startPlayer()

def _getChannelName(channelKey):
    return channelKey.upper().replace('-', ' ')

