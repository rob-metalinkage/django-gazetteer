import abc
# from gazetteer.sources.mapstory import MapstorySource
import psycopg2
import psycopg2.extras

class AbstractSource(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def getfeatures(self):
        """Yields a feature iterator. Each feature is a dict. Throws exceptions"""
        return

def get_handler(sourcetype):
    if sourcetype == 'mapstory' :
        import gazetteer.sources.mapstory
        return gazetteer.sources.mapstory.MapstorySource
    return None
        
class PostgresSource(AbstractSource):
    """ base class for a postgres connection based data source """
    
    def __init__(self) :
        self.connection_string = 'not initialised'
        self.conn = None
    
    def set_conn(self,connection_string) :
        """ sets an initialises a database connection """
        self.connection_string = connection_string
        if self.conn :
            self.conn.close()
        self.conn = psycopg2.connect(connection_string) 
        return self.conn
        
    def getconn(self):
        """
        Gets the low level database connection"""
        return conn
        
    def __exit__(self):
         if self.conn :
            self.conn.close()
            