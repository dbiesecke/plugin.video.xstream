# -*- coding: utf-8 -*-
from resources.lib.handler.pluginHandler import cPluginHandler
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.hoster import cHosterGui
from resources.lib.config import cConfig
import logger
import xbmc
import xbmcgui

# Main starting function
def run():
    parseUrl()

def parseUrl():
  oInputParameterHandler = ParameterHandler()

  # If no function is set, we set it to the default "load" function
  if oInputParameterHandler.exist("function"):
    sFunction = oInputParameterHandler.getValue("function")
    if sFunction == 'spacer':
        return True
    if sFunction == 'changeWatched':
        if cConfig().getSetting('metahandler')=='true':
            #videoType, name, imdbID, season=season, episode=episode, year=year, watched=watched
            try:
                from metahandler import metahandlers
                meta = metahandlers.MetaData()
                #print oInputParameterHandler.getAllParameters()
                params = oInputParameterHandler
                season = ''
                episode = ''
                mediaType = params.getValue('mediaType')
                imdbID = params.getValue('imdbID')
                name = params.getValue('title')
                if params.exist('season'):
                    season = params.getValue('season')
                if params.exist('episode'):
                    episode = params.getValue('episode')
                if imdbID:
                    meta.change_watched(mediaType, name, imdbID, season=season, episode=episode)
                    xbmc.executebuiltin("XBMC.Container.Refresh")
            except:
                META = False
                logger.info("Could not import package 'metahandler'")
            return

    if sFunction == 'updateMeta':
        if cConfig().getSetting('metahandler')=='true':
            #videoType, name, imdbID, season=season, episode=episode, year=year, watched=watched
            try:
                import resources.lib.handler.metaHandler as metahandlers
                #from metahandler import metahandlers
            except:
                logger.info("Could not import package 'metahandler'")
                return
            meta = metahandlers.MetaData()
            params = oInputParameterHandler
            season = ''
            episode = ''
            mediaType = params.getValue('mediaType')
            imdbID = params.getValue('imdbID')
            name = str(params.getValue('title'))
            year = params.getValue('year')
            # show meta search input
            oGui = cGui()
            sSearchText = oGui.showKeyBoard(name)
            if (sSearchText != False and sSearchText != ''):
                if mediaType == 'movie':
                    try:
                        foundInfo = meta.search_movies(sSearchText)
                    except:
                        logger.info('error or nothing found')
                        foundInfo = False
                elif mediaType == 'tvshow':
                    foundInfo = metahandlers.TheTVDB().get_matching_shows(sSearchText)
                else:
                    return
            else:
                return
            if not foundInfo:
                oGui.showInfo('xStream', 'Suchanfrage lieferte kein Ergebnis')
                return
            # select possible match
            dialog = xbmcgui.Dialog()
            items = []
            for item in foundInfo:
                if mediaType == 'movie':
                    items.append(str(item['title'].encode('utf-8'))+' ('+str(item['year'])+')')
                    
                elif mediaType == 'tvshow':
                    items.append(str(item[1]))
                else:
                    return
            index = dialog.select('Film/Serie wählen', items)
            if index > -1:
                item = foundInfo[index]
            else:
                return False
            if not imdbID:
                imdbID = ''
            if not year:
                year = ''
            if mediaType == 'movie':
                meta.update_meta(mediaType, name, imdbID, new_imdb_id=str(item['imdb_id']), new_tmdb_id=str(item['tmdb_id']), year=year)
            elif mediaType == 'tvshow':
                meta.update_meta(mediaType, name, imdbID, new_imdb_id=str(item[2]), year=year)
            #print oInputParameterHandler.getAllParameters()
            #if params.exist('season'):
            #    season = params.getValue('season')
            #if params.exist('episode'):
            #    episode = params.getValue('episode')
            #meta.update_meta(mediaType, name, imdbID, season=season, episode=episode)
            xbmc.executebuiltin("XBMC.Container.Refresh")
            return          
  else:
    sFunction = "load"

  # Test if we should run a function on a special site
  if oInputParameterHandler.exist('site'):
    sSiteName = oInputParameterHandler.getValue('site')
    logger.info (oInputParameterHandler.getAllParameters())
    
    if oInputParameterHandler.exist('playMode'):
        playMode = oInputParameterHandler.getValue('playMode')
        if cConfig().getSetting('autoPlay')=='true' and playMode != 'jd':
            cHosterGui().streamAuto(playMode, sSiteName, sFunction)
        else:        
            cHosterGui().stream(playMode, sSiteName, sFunction)
        return
        
    else:    
        logger.info("Call function '%s' from '%s'" % (sFunction, sSiteName))
        # If the hoster gui is called, run the function on it and return
        if sSiteName == 'cHosterGui':
            showHosterGui(sFunction)
            return  
        # If global search is called  
        if sSiteName == 'globalSearch':
            searchGlobal()
            return  
        if sSiteName == 'favGui':
            showFavGui(sFunction)
            return 
        # If addon settings are called  
        if sSiteName == 'xStream':
            oGui = cGui()
            oGui.openSettings()
            oGui.updateDirectory()
            return
        # If the urlresolver settings are called  
        if sSiteName == 'urlresolver':
            import urlresolver
            urlresolver.display_settings()
            return
        # Else load any other site as plugin and run the function
        plugin = __import__(sSiteName, globals(), locals())
        function = getattr(plugin, sFunction)
        function()
    
  else:
      # As a default if no site was specified, we run the default starting gui with all plugins
      showMainMenu(sFunction)

def showMainMenu(sFunction):    
    oGui = cGui()
    oPluginHandler = cPluginHandler()
    aPlugins = oPluginHandler.getAvailablePlugins()
    if len(aPlugins) <= 0:
      logger.info("No Plugins found")
      # Open the settings dialog to choose a plugin that could be enable
      oGui.openSettings()
      oGui.updateDirectory()
    else:
      # Create a gui element for every plugin found
      for aPlugin in aPlugins:
        oGuiElement = cGuiElement()
        oGuiElement.setTitle(aPlugin[0])
        oGuiElement.setSiteName(aPlugin[1])
        oGuiElement.setFunction(sFunction)
        if aPlugin[2] != '':
            oGuiElement.setThumbnail(aPlugin[2])
        oGui.addFolder(oGuiElement)
      
      # Create a gui element for global search
      oGuiElement = cGuiElement()
      oGuiElement.setTitle("Globale Suche")
      oGuiElement.setSiteName("globalSearch")
      oGuiElement.setFunction("globalSearch")
      #oGuiElement.setThumbnail("DefaultAddonService.png")
      oGui.addFolder(oGuiElement)
        
      # Create a gui element for favorites
      #oGuiElement = cGuiElement()
      #oGuiElement.setTitle("Favorites")
      #oGuiElement.setSiteName("FavGui")
      #oGuiElement.setFunction("showFavs")
      #oGuiElement.setThumbnail("DefaultAddonService.png")
      #oGui.addFolder(oGuiElement)

      # Create a gui element for addon settings
      oGuiElement = cGuiElement()
      oGuiElement.setTitle("xStream Settings")
      oGuiElement.setSiteName("xStream")
      oGuiElement.setFunction("display_settings")
      oGuiElement.setThumbnail("DefaultAddonService.png")
      oGui.addFolder(oGuiElement)
      
      # Create a gui element for urlresolver settings
      oGuiElement = cGuiElement()
      oGuiElement.setTitle("Resolver Settings")
      oGuiElement.setSiteName("urlresolver")
      oGuiElement.setFunction("display_settings")
      oGuiElement.setThumbnail("DefaultAddonService.png")
      oGui.addFolder(oGuiElement)

    oGui.setEndOfDirectory()

def showHosterGui(sFunction):
    oHosterGui = cHosterGui()
    function = getattr(oHosterGui, sFunction)
    function()
    return True
  
#def showFavGui(functionName):
    #from resources.lib.gui.favorites import FavGui
    #oFavGui = FavGui()
    #function = getattr(oFavGui, functionName)
    #function()
    #return True

def searchGlobal():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False and sSearchText != ''):
        aPlugins = []
        aPlugins = cPluginHandler().getAvailablePlugins()
        for pluginEntry in aPlugins:
            pluginName = pluginEntry[0]
            pluginSiteName = pluginEntry[1]
            logger.info('Searching for "'+sSearchText+'" at '+pluginName)
            try:
                plugin = __import__(pluginSiteName, globals(), locals())
                function = getattr(plugin, '_search')
                oGuiElement = cGuiElement('[B][COLOR yellow]----'+pluginName+'----[/COLOR][/B]',pluginSiteName,'spacer')
                if len(pluginEntry)>2:
                    oGuiElement.setThumbnail(pluginEntry[2])
                oGui.addFolder(oGuiElement)
                function(oGui, sSearchText)
            except:
                logger.info(str(pluginName)+': search failed')
        oGui.setView()
        oGui.setEndOfDirectory()
    return True
