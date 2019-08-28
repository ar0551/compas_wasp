## imports for py2.7
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


## import compas & friends
import compas_rhino
from compas.geometry import Frame


## list all classes in file
__all__ = ['Rule']


class Rule(object):
    """Wasp assembly rule

    """

    __module__ = 'compas_wasp'

    def __init__(self, _part1, _conn1, _part2, _conn2, _active = True):
        self.part1 = _part1
        self.conn1 = _conn1
        self.part2 = _part2
        self.conn2 = _conn2
        self.active = _active
	
	## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "WaspRule [%s|%s_%s|%s]" % (self.part1, self.conn1, self.part2, self.conn2)


# ==============================================================================
# Debugging
# ==============================================================================
if __name__ == "__main__":
    pass