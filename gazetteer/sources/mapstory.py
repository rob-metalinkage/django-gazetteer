from gazetteer.sources.abstractsource import PostgresSource

# from mapstory.models import Location, LocationName
import psycopg2
import psycopg2.extras
from psycopg2.extensions import AsIs

class MapstorySource(PostgresSource) :
    """ handler to find a mapstory layer by name in its source database and create a feature iterator """
    
    conn = None
    connstring = "host=localhost dbname=mapstory_data user=mapstory password=foobar"
    
    def __init__(self):
        self.set_conn (self.connstring) 
   
 
    def getfeatures(self,sourcebinding):
        """
            Yields a feature iterator. Each feature is a dict
            Throws exceptions
            May want to switch to server-side cursor.
        """
        cur = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) 
        SQL = "select * from %s "  
        if sourcebinding.filter or sourcebinding.config.filter :
            print "Need to apply filter!"
            # filterclause = 'WHERE '

            # process clauses in an injection-safe way and append to SQL 
        try :
            cur.execute(SQL, (AsIs(sourcebinding.source), ))
        except Exception as e:
            # import pdb; pdb.set_trace() 
            raise e
        for r in cur :
            yield r
                # break
            # refactor if necessary to force connection close on failure
    
