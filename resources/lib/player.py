from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.config import cConfig
import logger
from resources.lib.gui.gui import cGui
import xbmc
import time

class cPlayer:
    
    def clearPlayList(self):
        oPlaylist = self.__getPlayList()
        oPlaylist.clear()

    def __getPlayList(self):
        return xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

    def addItemToPlaylist(self, oGuiElement):
        oGui = cGui()
        oListItem =  oGui.createListItem(oGuiElement)
        self.__addItemToPlaylist(oGuiElement, oListItem)
	
    def __addItemToPlaylist(self, oGuiElement, oListItem):    
        oPlaylist = self.__getPlayList()	
        oPlaylist.add(oGuiElement.getMediaUrl(), oListItem )

    def startPlayer(self):
        logger.info('start player')
        sPlayerType = self.__getPlayerType()
        xbmcPlayer = xbmc.Player(sPlayerType)
        oPlayList = self.__getPlayList()
        xbmcPlayer.play(oPlayList)
        

        # For older Versions; dirty but works 
        if (cConfig().isDharma() == False):
            oInputParameterHandler = ParameterHandler()
            aParams = oInputParameterHandler.getAllParameters()

            oGui = cGui()
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(aParams['site'])
            oGuiElement.setFunction(aParams['function'])
            oGui.addFolder(oGuiElement)
            oGui.setEndOfDirectory()

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
        if META:
            percent = 0
            while xbmcPlayer.isPlaying():
                time.sleep(5)
                try:
                    totalTime = xbmcPlayer.getTotalTime()
                    playedTime = xbmcPlayer.getTime()
                    percent = playedTime/totalTime
                except:
                    logger.info('Watched percent '+str(int(percent*100)))
                    percent = playedTime/totalTime
                    if percent >= 0.80:
                        logger.info('Attemt to change watched status')
                        meta = metahandlers.MetaData()
                        params = ParameterHandler()
                        season = ''
                        episode = ''
                        mediaType = params.getValue('mediaType')
                        imdbID = params.getValue('imdbID')
                        name = params.getValue('Title')
                        if params.exist('season'):
                            season = params.getValue('season')
                            if int(season) > 0:mediaType = 'season'
                        if params.exist('episode'):
                            episode = params.getValue('episode')
                            if int(episode) > 0: mediaType = 'episode'
                        if imdbID and mediaType:
                            meta.change_watched(mediaType, name, imdbID, season=season, episode=episode)
                            xbmc.executebuiltin("XBMC.Container.Refresh")
                        else:
                            logger.info('Could not change watched status; imdbID or mediaType missing')
                    pass           

            #xbmcPlayer.onPlayBackEnded():



    def __getPlayerType(self):
        oConfig = cConfig()
        sPlayerType = oConfig.getSetting('playerType')

        if (sPlayerType == '0'):
            logger.info('playertype from config: auto')
            return xbmc.PLAYER_CORE_AUTO

        if (sPlayerType == '1'):
            logger.info('playertype from config: mplayer')
            return xbmc.PLAYER_CORE_MPLAYER

        if (sPlayerType == '2'):
            logger.info('playertype from config: dvdplayer')
            return xbmc.PLAYER_CORE_DVDPLAYER
