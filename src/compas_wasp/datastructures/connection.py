## imports for py2.7
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


## import compas & friends
from compas.geometry import Frame
from compas.geometry import Transformation

from compas.datastructures import Datastructure

from compas.datastructures._mixins import FromToData
from compas.datastructures._mixins import FromToJson
from compas.datastructures._mixins import FromToPickle


## list all classes in file
__all__ = ['Connection']


class Connection(FromToData,
                 FromToJson,
                 FromToPickle,
                 Datastructure):
    """Wasp Connection

    """

    __module__ = 'compas_wasp'

    def __init__(self, _frame=None, _type=None, _part=None, _id=None):
        super(Connection, self).__init__()
        
        self.frame = _frame

        self.flip_pln = None
        if self.frame is not None:
            flip_pln_Y = self.frame.yaxis.copy()
            flip_pln_Y.scale(-1)
            self.flip_pln = Frame(self.frame.point, self.frame.xaxis, flip_pln_Y)

        self.type = _type
        self.part = _part
        self.id = _id

        self.rules_table = []
        self.active_rules = []
    
        ## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "WaspConnection [id: %s, type: %s]" % (self.id, self.type)
    

    @property
    def data(self):
        """dict : A data dict representing the part data structure for serialisation.

        The dict has the following structure:

        * 'aaa'   => dict

        Note
        ----
        All dictionary keys are converted to their representation value (``repr(key)``)
        to ensure compatibility of all allowed key types with the JSON serialisation
        format, which only allows for dict keys that are strings.

        """
        data = {'f_origin'          : [self.frame.point.x, self.frame.point.y, self.frame.point.z],
                'f_xaxis'           : [self.frame.xaxis.x, self.frame.xaxis.y, self.frame.xaxis.z],
                'f_yaxis'           : [self.frame.yaxis.x, self.frame.yaxis.y, self.frame.yaxis.z],
                'type'              : self.type,
                'part'              : self.part,
                'id'                : str(self.id)}
        
        return data

    @data.setter
    def data(self, data):
        f_origin    = data.get('f_origin') or []
        f_xaxis     = data.get('f_xaxis') or []
        f_yaxis     = data.get('f_yaxis') or []
        c_type      = data.get('type') or None
        c_part      = data.get('part') or None
        c_id        = data.get('id') or None


        self.frame = Frame(f_origin, f_xaxis, f_yaxis)

        flip_pln_Y = self.frame.yaxis.copy()
        flip_pln_Y.scale(-1)
        self.flip_pln = Frame(self.frame.point, self.frame.xaxis, flip_pln_Y)

        self.type = c_type
        self.part = c_part
        self.id = int(c_id)

        self.rules_table = []
        self.active_rules = []



    
    ## return a transformed copy of the connection
    def transform(self, trans):
        pln_trans = self.frame.transformed(trans)
        conn_trans = Connection(pln_trans, self.type, self.part, self.id)
        return conn_trans
    
    ## return a copy of the connection
    def copy(self):
        pln_copy = self.frame.copy()
        conn_copy = Connection(pln_copy, self.type, self.part, self.id)
        return conn_copy
    
    ## generate the rules-table for the connection
    def generate_rules_table(self, rules):
        count = 0
        self.rules_table = []
        self.active_rules = []
        for rule in rules:
            if rule.part1 == self.part and rule.conn1 == self.id:
                self.rules_table.append(rule)
                self.active_rules.append(count)
                count += 1
    

# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":
    pass


