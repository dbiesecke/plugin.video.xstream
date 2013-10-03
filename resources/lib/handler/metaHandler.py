import metahandler.common as common
from metahandler.TMDB import TMDB
from metahandler import thetvdbapi
from metahandler import metahandlers
from metahandler.metahandlers import *

#theTVDB
import urllib
import elementtree.ElementTree as ET
from cStringIO import StringIO


class MetaData(metahandlers.MetaData):
    """partiall reimplementation of metahandler.MetaData class"""
    def get_meta(self, media_type, name, imdb_id='', tmdb_id='', year='', rating='', overlay=6):
        '''
        Main method to get meta data for movie or tvshow. Will lookup by name/year
        if no IMDB ID supplied.

        Args:
            media_type (str): 'movie' or 'tvshow'
            name (str): full name of movie/tvshow you are searching
        Kwargs:
            imdb_id (str): IMDB ID
            tmdb_id (str): TMDB ID
            year (str): 4 digit year of video, recommended to include the year whenever possible
            to maximize correct search results.
            rating (float): IMDB or TMDB rating of the movie/tvshow, can possibly increase the search accuracy
            overlay (int): To set the default watched status (6=unwatched, 7=watched) on new videos

        Returns:
            DICT of meta data or None if cannot be found.
        '''
       
        common.addon.log('---------------------------------------------------------------------------------------', 2)
        common.addon.log('Attempting to retreive meta data for %s: %s %s %s %s' % (media_type, name, year, imdb_id, tmdb_id), 2)
 
        if imdb_id:
            imdb_id = self._valid_imdb_id(imdb_id)
        
        if imdb_id:
            meta = self._cache_lookup_by_id(media_type, imdb_id=imdb_id)
        elif tmdb_id:
            meta = self._cache_lookup_by_id(media_type, tmdb_id=tmdb_id)
        else:
            meta = self._cache_lookup_by_name(media_type, name, year, rating)

        if not meta:

            if media_type==self.type_movie:
                meta = self._get_tmdb_meta(imdb_id, tmdb_id, name, year, rating)
            elif media_type==self.type_tvshow:
                meta = self._get_tvdb_meta(imdb_id, name, year, rating)
            
            self._cache_save_video_meta(meta, name, media_type, overlay)
        # while updating, chache_lookup_by_id can cause problems, there are movies/tvshows in different languages an therefore different names but with the same id
        # so we try to get meta information although we already have meta for the given id
        elif meta['title'] != self._clean_string(name.lower()):

            if media_type==self.type_movie:
                meta = self._get_tmdb_meta(imdb_id, tmdb_id, name, year, rating)
            elif media_type==self.type_tvshow:
                meta = self._get_tvdb_meta(imdb_id, name, year, rating)

            self._cache_save_video_meta(meta, name, media_type, overlay)

        meta = self.__format_meta(media_type, meta, name)
        
        return meta

    def _cache_lookup_by_name(self, media_type, name, year='', rating=''):
        '''
        Lookup in SQL DB for video meta data by name and year

        Args:
            media_type (str): 'movie' or 'tvshow'
            name (str): full name of movie/tvshow you are searching
        Kwargs:
            year (str): 4 digit year of video, recommended to include the year whenever possible
            to maximize correct search results.
            rating (float): IMDB or TMDB rating of the movie/tvshow, can possibly increase the search accuracy

        Returns:
            DICT of matched meta data or None if no match.
        '''

        name = self._clean_string(name.lower())
        if media_type == self.type_movie:
            sql_select = "SELECT * FROM movie_meta WHERE title = '%s'" % name
        elif media_type == self.type_tvshow:
            sql_select = "SELECT a.*, CASE WHEN b.episode ISNULL THEN 0 ELSE b.episode END AS episode, CASE WHEN c.playcount ISNULL THEN 0 ELSE c.playcount END as playcount FROM tvshow_meta a LEFT JOIN (SELECT imdb_id, count(imdb_id) AS episode FROM episode_meta GROUP BY imdb_id) b ON a.imdb_id = b.imdb_id LEFT JOIN (SELECT imdb_id, count(imdb_id) AS playcount FROM episode_meta WHERE overlay=7 GROUP BY imdb_id) c ON a.imdb_id = c.imdb_id WHERE a.title = '%s'" % name
            if DB == 'mysql':
                sql_select = sql_select.replace("ISNULL", "IS NULL")
        common.addon.log('Looking up in local cache by name for: %s %s %s' % (media_type, name, year), 0)
        
        # movie_meta doesn't have a year column
        if year and media_type == self.type_movie:
            sql_select = sql_select + " AND year = %s" % year
        elif rating:
            sql_select = sql_select + " AND rating = %s" % rating
        common.addon.log('SQL Select: %s' % sql_select, 0)
        
        try:
            self.dbcur.execute(sql_select)
            matchedrow = self.dbcur.fetchone()
        except Exception, e:
            common.addon.log('************* Error selecting from cache db: %s' % e, 4)
            pass
            
        if matchedrow:
            common.addon.log('Found meta information by name in cache table: %s' % dict(matchedrow), 0)
            return dict(matchedrow)
        else:
            common.addon.log('No match in local DB', 0)
            return None

    def _get_tmdb_meta(self, imdb_id, tmdb_id, name, year='', rating=''):
        '''
        Requests meta data from TMDB and creates proper dict to send back

        Args:
            imdb_id (str): IMDB ID
            name (str): full name of movie you are searching
        Kwargs:
            year (str): 4 digit year of movie, when imdb_id is not available it is recommended
            to include the year whenever possible to maximize correct search results.
            rating (float): IMDB or TMDB rating of the movie/tvshow, can possibly increase the search accuracy

        Returns:
            DICT. It must also return an empty dict when
            no movie meta info was found from tmdb because we should cache
            these "None found" entries otherwise we hit tmdb alot.
        '''
        
        tmdb = TMDB(lang = 'de')
        meta = tmdb.tmdb_lookup(name,imdb_id,tmdb_id, year)
        
        if meta is None:
            # create an empty dict so below will at least populate empty data for the db insert.
            meta = {}

        return self._format_tmdb_meta(meta, imdb_id, name, year)

    def _get_tvdb_meta(self, imdb_id, name, year='', rating=''):
        '''
        Requests meta data from TVDB and creates proper dict to send back

        Args:
            imdb_id (str): IMDB ID
            name (str): full name of movie you are searching
        Kwargs:
            year (str): 4 digit year of movie, when imdb_id is not available it is recommended
            to include the year whenever possible to maximize correct search results.
            rating (float): IMDB or TMDB rating of the movie/tvshow, can possibly increase the search accuracy

        Returns:
            DICT. It must also return an empty dict when
            no movie meta info was found from tvdb because we should cache
            these "None found" entries otherwise we hit tvdb alot.
        '''
        common.addon.log('Starting TVDB Lookup', 0)
        tvdb = TheTVDB( lang = 'de')
        tvdb_id = ''
        
        try:
            if imdb_id:
                tvdb_id = tvdb.get_show_by_imdb(imdb_id)
        except Exception, e:
            common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
            tvdb_id = ''
            pass
            
        #Intialize tvshow meta dictionary
        meta = self._init_tvshow_meta(imdb_id, tvdb_id, name, year)

        # if not found by imdb, try by name
        if tvdb_id == '':
            try:
                #If year is passed in, add it to the name for better TVDB search results
                if year:
                    name = name + ' ' + year
                show_list=tvdb.get_matching_shows(name)
            except Exception, e:
                common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
                show_list = []
                pass
            common.addon.log('Found TV Show List: %s' % show_list, 0)
            tvdb_id=''
            prob_id=''
            for show in show_list:
                (junk1, junk2, junk3) = show
                # encoding ensures better matching for tvshows with so called "umlauten" 
                junk2 = junk2.encode('utf-8')
                #if we match imdb_id or full name (with year) then we know for sure it is the right show
                if junk3==imdb_id or self._string_compare(self._clean_string(junk2),self._clean_string(name)):
                    tvdb_id=self._clean_string(junk1)
                    if not imdb_id:
                        imdb_id=self._clean_string(junk3)
                    break
                #if we match just the cleaned name (without year) keep the tvdb_id
                elif self._string_compare(self._clean_string(junk2),self._clean_string(name)):
                    prob_id = junk1
                    if not imdb_id:
                        imdb_id = self_clean_string(junk3)
            if tvdb_id == '' and prob_id != '':
                tvdb_id = self._clean_string(prob_id)

        if tvdb_id:
            common.addon.log('Show *** ' + name + ' *** found in TVdb. Getting details...', 0)

            try:
                show = tvdb.get_show(tvdb_id)
            except Exception, e:
                common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
                show = None
                pass
            
            if show is not None:
                meta['imdb_id'] = imdb_id
                meta['tvdb_id'] = tvdb_id
                meta['title'] = name
                if str(show.rating) != '' and show.rating != None:
                    meta['rating'] = float(show.rating)
                meta['duration'] = show.runtime
                meta['plot'] = show.overview
                meta['mpaa'] = show.content_rating
                meta['premiered'] = str(show.first_aired)

                #Do whatever we can to set a year, if we don't have one lets try to strip it from show.first_aired/premiered
                if not year and show.first_aired:
                        #meta['year'] = int(self._convert_date(meta['premiered'], '%Y-%m-%d', '%Y'))
                        meta['year'] = int(meta['premiered'][:4])

                if show.genre != '':
                    temp = show.genre.replace("|",",")
                    temp = temp[1:(len(temp)-1)]
                    meta['genre'] = temp
                meta['studio'] = show.network
                meta['status'] = show.status
                if show.actors:
                    for actor in show.actors:
                        meta['cast'].append(actor)
                meta['banner_url'] = show.banner_url
                meta['imgs_prepacked'] = self.classmode
                meta['cover_url'] = show.poster_url
                meta['backdrop_url'] = show.fanart_url
                meta['overlay'] = 6

                if meta['plot'] == 'None' or meta['plot'] == '' or meta['plot'] == 'TBD' or meta['plot'] == 'No overview found.' or meta['rating'] == 0 or meta['duration'] == 0 or meta['cover_url'] == '':
                    common.addon.log(' Some info missing in TVdb for TVshow *** '+ name + ' ***. Will search imdb for more', 0)
                    tmdb = TMDB()
                    imdb_meta = tmdb.search_imdb(name, imdb_id)
                    if imdb_meta:
                        imdb_meta = tmdb.update_imdb_meta(meta, imdb_meta)
                        if imdb_meta.has_key('overview'):
                            meta['plot'] = imdb_meta['overview']
                        if imdb_meta.has_key('rating'):
                            meta['rating'] = float(imdb_meta['rating'])
                        if imdb_meta.has_key('runtime'):
                            meta['duration'] = imdb_meta['runtime']
                        if imdb_meta.has_key('cast'):
                            meta['cast'] = imdb_meta['cast']
                        if imdb_meta.has_key('cover_url'):
                            meta['cover_url'] = imdb_meta['cover_url']

                return meta
            else:
                tmdb = TMDB()
                imdb_meta = tmdb.search_imdb(name, imdb_id)
                if imdb_meta:
                    meta = tmdb.update_imdb_meta(meta, imdb_meta)
                return meta
        else:
            return meta

    def _get_tvdb_episode_data(self, tvdb_id, season, episode, air_date=''):
        '''
        Initiates lookup for episode data on TVDB
        
        Args:
            tvdb_id (str): TVDB id
            season (str): tv show season number, number only no other characters
            episode (str): tv show episode number, number only no other characters
        Kwargs:
            air_date (str): Date episode was aired
                        
        Returns:
            DICT. Data found from lookup
        '''      
        
        meta = {}
        tvdb = TheTVDB()
        if air_date:
            try:
                episode = tvdb.get_episode_by_airdate(tvdb_id, air_date)
            except:
                common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
                episode = None
                pass
                
            
            #We do this because the airdate method returns just a part of the overview unfortunately
            if episode:
                ep_id = episode.id
                if ep_id:
                    try:
                        episode = tvdb.get_episode(ep_id)
                    except:
                        common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
                        episode = None
                        pass
        else:
            try:
                episode = tvdb.get_episode_by_season_ep(tvdb_id, season, episode)
            except Exception, e:
                common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
                episode = None
                pass
            
        if episode is None:
            return None
        
        meta['episode_id'] = episode.id
        meta['plot'] = self._check(episode.overview)
        if episode.guest_stars:
            guest_stars = episode.guest_stars
            if guest_stars.startswith('|'):
                guest_stars = guest_stars[1:-1]
            guest_stars = guest_stars.replace('|', ', ')
            meta['plot'] = meta['plot'] + '\n\nGuest Starring: ' + guest_stars
        meta['rating'] = float(self._check(episode.rating,0))
        meta['premiered'] = self._check(episode.first_aired)
        meta['title'] = self._check(episode.name)
        meta['poster'] = self._check(episode.image)
        meta['director'] = self._check(episode.director)
        meta['writer'] = self._check(episode.writer)
        meta['season'] = int(self._check(episode.season_number,0))
        meta['episode'] = int(self._check(episode.episode_number,0))
              
        return meta
    def update_meta(self, media_type, name, imdb_id, tmdb_id='', new_imdb_id='', new_tmdb_id='', year=''):
        '''
        Updates and returns meta data for given movie/tvshow, mainly to be used with refreshing individual movies.
        
        Searches local cache DB for record, delete if found, calls get_meta() to grab new data

        name, imdb_id, tmdb_id should be what is currently in the DB in order to find current record
        
        new_imdb_id, new_tmdb_id should be what you would like to update the existing DB record to, which you should have already found
        
        Args:
            name (int): full name of movie you are searching            
            imdb_id (str): IMDB ID of CURRENT entry
        Kwargs:
            tmdb_id (str): TMDB ID of CURRENT entry
            new_imdb_id (str): NEW IMDB_ID to search with
            new_tmdb_id (str): NEW TMDB ID to search with
            year (str): 4 digit year of video, recommended to include the year whenever possible
                        to maximize correct search results.
                        
        Returns:
            DICT of meta data or None if cannot be found.
        '''
        common.addon.log('---------------------------------------------------------------------------------------', 2)
        common.addon.log('Updating meta data: %s Old: %s %s New: %s %s Year: %s' % (name, imdb_id, tmdb_id, new_imdb_id, new_tmdb_id, year), 2)
        
        if imdb_id:
            imdb_id = self._valid_imdb_id(imdb_id)        
        
        if imdb_id:
            meta = self._cache_lookup_by_id(media_type, imdb_id=imdb_id)
        elif tmdb_id:
            meta = self._cache_lookup_by_id(media_type, tmdb_id=tmdb_id)
        else:
            meta = self._cache_lookup_by_name(media_type, name, year)
        
        if meta:
            overlay = meta['overlay']
            self._cache_delete_video_meta(media_type, imdb_id, tmdb_id, name, year)
        else:
            overlay = 6
            common.addon.log('No match found in cache db', 3)
        
        if not new_imdb_id:
            new_imdb_id = imdb_id
        elif not new_tmdb_id:
            new_tmdb_id = tmdb_id
            
        return self.get_meta(media_type, name, new_imdb_id, new_tmdb_id, year, overlay)


class TheTVDB(thetvdbapi.TheTVDB):

    def __init__(self, api_key='2B8557E0CBF7D720', lang = 'de'):
        #http://www.thetvdb.com/api/GetEpisodeByAirDate.php?apikey=1D62F2F90030C444&seriesid=71256&airdate=2010-03-29
        self.api_key = api_key
        self.mirror_url = "http://www.thetvdb.com"
        self.base_url = self.mirror_url + "/api"
        self.base_key_url = "%s/%s" % (self.base_url, self.api_key)
        self.lang = lang

    def get_matching_shows(self, show_name):
        """Get a list of shows matching show_name."""
        get_args = urllib.urlencode({"seriesname": show_name, 'language': self.lang}, doseq=True)
        url = "%s/GetSeries.php?%s" % (self.base_url, get_args)
        data = urllib.urlopen(url)
        show_list = []
        if data:
            try:
                tree = ET.parse(data)
                show_list = [(show.findtext("seriesid"), show.findtext("SeriesName"),show.findtext("IMDB_ID")) for show in tree.getiterator("Series")]
            except SyntaxError:
                pass

        return show_list

    def get_show(self, show_id):
        """Get the show object matching this show_id."""
        #url = "%s/series/%s/%s.xml" % (self.base_key_url, show_id, "el")
        url = "%s/series/%s/%s.xml" % (self.base_key_url, show_id, self.lang)
        print url
        data = StringIO(urllib.urlopen(url).read())
        temp_data = data.getvalue()
        print 'data returned from TheTVDB ' + temp_data
        show = None
        if temp_data.startswith('<?xml') == False:
            return show

        try:
            tree = ET.parse(data)
            show_node = tree.find("Series")

            show = TheTVDB.Show(show_node, self.mirror_url)
        except SyntaxError:
            pass

        return show

    def get_show_by_imdb(self, imdb_id):
        """Get the show object matching this show_id."""
        #url = "%s/series/%s/%s.xml" % (self.base_key_url, show_id, "el")
        url = "%s/GetSeriesByRemoteID.php?imdbid=%s" % (self.base_url, imdb_id)
        print url
        data = StringIO(urllib.urlopen(url).read())
        temp_data = data.getvalue()
        print 'data returned from TheTVDB ' + temp_data
        tvdb_id = ''
        if temp_data.startswith('<?xml') == False:
            return tvdb_id
        try:
            tree = ET.parse(data)
            for show in tree.getiterator("Series"):
                tvdb_id = show.findtext("seriesid")

        except SyntaxError:
            pass

        return tvdb_id

    def get_episode_by_season_ep(self, show_id, season_num, ep_num):
        """Get the episode object matching this episode_id."""
        url = "%s/series/%s/default/%s/%s/%s.xml" % (self.base_key_url, show_id, season_num, ep_num, self.lang)
        data = StringIO(urllib.urlopen(url).read())

        episode = None
        print url
        
        #code to check if data has been returned
        temp_data = data.getvalue()
        if temp_data.startswith('<?xml') == False :
            print 'No data returned ', temp_data
            return episode
        
        try:
            tree = ET.parse(data)
            episode_node = tree.find("Episode")

            episode = TheTVDB.Episode(episode_node, self.mirror_url)
        except SyntaxError:
            pass
        
        return episode

class TMDB(TMDB):

    def _search_movie(self, name, year=''):
        ''' Helper method to start a TMDB Movie.search request - search by Name/Year '''
        # no usage of clean_name, otherwise names with so called 'umlauten' can't be found
        name = urllib.quote(name)
        if year:
            name = name + '+' + year
        return self._do_request('Movie.search',name)