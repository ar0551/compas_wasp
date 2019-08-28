## imports for py2.7
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


## import compas & friends
import compas_rhino
from compas.geometry import Frame
from compas.geometry import Transformation


## list all classes in file
__all__ = ['Connection']


class Connection(object):
    """Wasp Connection

    """

    __module__ = 'compas_wasp'

    def __init__(self, _frame, _type, _part, _id):
        
        self.frame = _frame

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


