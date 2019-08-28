
import compas

from compas.datastructures import mesh_transformed_numpy
from compas.datastructures import Mesh

from compas.geometry import Transformation

def transform_mesh_proxy(data, T):
    mesh = Mesh.from_data(data)
    mesh = mesh_transformed_numpy(mesh, T)
    return mesh.to_data()

"""
mesh = Mesh.from_obj(compas.get('saddle.obj'))
T = Transformation()

print(transform_mesh_proxy(mesh.to_data(), T))
"""
