## imports for py2.7
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


## import compas & friends
import compas
import compas_rhino

from compas.geometry import Frame
from compas.geometry import Transformation
from compas.geometry import centroid_points
from compas.geometry import Point

from compas.datastructures import Mesh
from compas.datastructures import Datastructure

from compas.datastructures._mixins import FromToData
from compas.datastructures._mixins import FromToJson
from compas.datastructures._mixins import FromToPickle

from compas_wasp.datastructures import Connection


if not compas.IPY:
    from compas.datastructures import mesh_transformed_numpy
    get_transformed_mesh = mesh_transformed_numpy

else:
    ## basic compas methos for transformations
    if True:
        from compas.datastructures import mesh_transformed
        get_transformed_mesh = mesh_transformed

        """
        from compas.rpc import Proxy
        helper = Proxy("compas_wasp.datastructures.helpers")

        def transform_part_geo(mesh_geo, T):
            mesh_data = mesh_geo.to_data()
            mesh_data = helper.transform_mesh_proxy(mesh_data, list(T))
            return Mesh.from_data(mesh_data)

        get_transformed_mesh = transform_part_geo
        """
    ## rpc call for transformation with numpy
    else:
        from compas.rpc import Proxy
        compas_geometry = Proxy("compas.geometry")

        def transform_part_geo(mesh_geo, T):
            mesh_data = mesh_geo.to_vertices_and_faces()
            t_mesh = Mesh.from_vertices_and_faces(mesh_data[0], mesh_data[1])
            xyz = compas_geometry.transform_points_numpy(mesh_data[0], list(T))
            
            for key, attr in t_mesh.vertices(True):
                attr['x'] = xyz[key][0]
                attr['y'] = xyz[key][1]
                attr['z'] = xyz[key][2]
            
            return t_mesh

        get_transformed_mesh = transform_part_geo


## list all classes in file
__all__ = ['Part']


class Part(FromToData,
           FromToJson,
           FromToPickle,
           Datastructure):
    
    """Wasp basic Part

    """

    __module__ = 'compas_wasp'

    #def __init__(self, name, geometry, connections, collider, attributes, dim=None, id=None, field=None):  
    def __init__(self, _name=None, _geometry=None, _connections=[]):
        super(Part, self).__init__()
        self.name = _name
        self.id = None
        self.geo = _geometry

        #self.field = field
        
        self.connections = []
        self.active_connections = []
        count = 0
        for conn in _connections:
            conn.part = self.name
            conn.id = count
            self.connections.append(conn)
            self.active_connections.append(count)
            count += 1
        
        self.transformation = Transformation()
        self.center = Point(0,0,0)
        if self.geo is not None:
            center_coords = self.geo.centroid()
            self.center = Point(center_coords[0], center_coords[1], center_coords[2])

        #self.collider = collider

        """
        ##part size
        if dim is not None:
            self.dim = dim
        else:
            max_collider_dist = None
            for coll_geo in self.collider.geometry:
                for v in coll_geo.Vertices:
                    dist = self.center.DistanceTo(v)
                    if dist > max_collider_dist or max_collider_dist is None:
                        max_collider_dist = dist
            
            self.dim = max_collider_dist
        """
        
        self.parent = None
        self.children = []

        """
        self.attributes = []
        if len(attributes) > 0:
            self.attributes = attributes
        
        self.is_constrained = False
        """

	## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "WaspPart [name: %s, id: %s]" % (self.name, self.id)
    
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
        data = {'name'                  : self.name,
                'id'                    : self.id,
                'geo'                   : self.geo.to_data(),
                'connections'           : [c.to_data() for c in self.connections],
                'active_connections'    : self.active_connections,
                'transformation'        : list(self.transformation),
                'parent'                : self.parent,
                'children'              : self.children}
        
        return data

    @data.setter
    def data(self, data):
        p_name                    = data.get('name') or None
        p_id                      = data.get('id') or None
        p_geo                     = data.get('geo') or {}
        p_connections             = data.get('connections') or []
        p_active_connections      = data.get('active_connections') or []
        p_transformation          = data.get('transformation') or []
        p_parent                  = data.get('parent') or None
        p_children                = data.get('children') or []

        self.name = p_name
        self.id = p_id
        self.geo = Mesh.from_data(p_geo)

        self.connections = [Connection.from_data(c) for c in p_connections]
        self.active_connections = p_active_connections

        self.transformation = Transformation.from_matrix(p_transformation)

        center_coords = self.geo.centroid()
        self.center = Point(center_coords[0], center_coords[1], center_coords[2])

        self.parent = p_parent
        self.children = p_children






    def centroid(self):
        """Compute the centroid of the block.

        Returns
        -------
        point
            The XYZ location of the centroid.

        """
        return centroid_points([self.geo.vertex_coordinates(key) for key in self.geo.vertices()])
    
    ## reset the part and connections according to new provided aggregation rules
    def reset_part(self, rules):
        count = 0
        self.active_connections = []
        for conn in self.connections:
            conn.generate_rules_table(rules)
            self.active_connections.append(count)
            count += 1
    
        ## return a dictionary containing all part data
    def return_part_data(self):
        data_dict = {}
        data_dict['name'] = self.name
        data_dict['id'] = self.id
        data_dict['geo'] = self.geo
        data_dict['connections'] = self.connections
        data_dict['transform'] = self.transformation
        #data_dict['collider'] = self.collider
        data_dict['center'] = self.center
        data_dict['parent'] = self.parent
        data_dict['children'] = self.children
        #data_dict['attributes'] = self.attributes
        return data_dict
    
    ## return a transformed copy of the part
    def transform(self, trans, transform_sub_parts=False):
        geo_trans = get_transformed_mesh(self.geo, trans)
        
        #collider_trans = self.collider.transform(trans)
        
        connections_trans = []
        for conn in self.connections:
            connections_trans.append(conn.transform(trans))
        
        """
        attributes_trans = []
        if len(self.attributes) > 0:
            for attr in self.attributes:
                attributes_trans.append(attr.transform(trans))
        """
        
        #part_trans = Part(self.name, geo_trans, connections_trans, collider_trans, attributes_trans, dim=self.dim, id=self.id, field=self.field)
        part_trans = Part(self.name, geo_trans, connections_trans)

        part_trans.transformation = trans
        return part_trans
    
    ## return a copy of the part
    def copy(self):
        geo_copy = self.geo.copy()
        
        #collider_copy = self.collider.copy()
        
        connections_copy = []
        for conn in self.connections:
            connections_copy.append(conn.copy())
        
        """
        attributes_copy = []
        if len(self.attributes) > 0:
            for attr in self.attributes:
                attributes_copy.append(attr.copy())
        """
        
        #part_copy = Part(self.name, geo_copy, connections_copy, collider_copy, attributes_copy, dim=self.dim, id=self.id, field=self.field)
        part_copy = Part(self.name, geo_copy, connections_copy)

        part_copy.transformation = self.transformation
        return part_copy
    
    ## return transformed center point of the part
    def transform_center(self, trans):
        center_trans = self.center.transformed(trans)
        return center_trans
    
    ## return transformed collider
    def transform_collider(self, trans):
        pass
        #return self.collider.transform(trans)

# ==============================================================================
# Debugging
# ==============================================================================
if __name__ == "__main__":
    pass