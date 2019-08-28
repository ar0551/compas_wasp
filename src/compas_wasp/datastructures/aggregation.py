## imports for py2.7
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import random


## import compas & friends
import compas_rhino

from compas.geometry import Frame
from compas.geometry import Transformation




## list all classes in file
__all__ = ['Aggregation']


class Aggregation(object):
    """Wasp Aggregation data structure

    """

    __module__ = 'compas_wasp'

    def __init__(self, _name, _parts, _rules, _mode, _prev = [], _coll_check = True, _field = [], _global_constraints = []):
        
        ## basic parameters
        self.name = _name
        
        self.parts = {}
        for part in _parts:
            self.parts[part.name] = part
        
        self.rules = _rules
        
        self.mode = _mode
        self.coll_check = _coll_check
        
        self.aggregated_parts = []
        

        ## fields
        self.multiple_fields = False
        if len(_field) == 0 or _field is None:
            self.field = None
        elif len(_field) == 1:
            self.field = _field[0]
        else:
            self.field = {}
            for f in _field:
                self.field[f.name] = f
            self.multiple_fields = True
        
        ## reset base parts
        self.reset_base_parts()
        
        ## temp list to store possible colliders to newly added parts
        self.possible_collisions = []
        
        ## aggregation queue, storing sorted possible next states in the form (part, f_val)
        self.aggregation_queue = []
        self.queue_values = []
        self.queue_count = 0
    
        
        ## previous aggregated parts
        self.prev_num = 0
        if len(_prev) > 0:
            self.prev_num = len(_prev)
            for prev_p in _prev:
                prev_p_copy = prev_p.copy()
                prev_p_copy.reset_part(self.rules)
                prev_p_copy.id = len(self.aggregated_parts)
                self.aggregated_parts.append(prev_p_copy)
                if self.field is not None:
                    self.compute_next_w_field(prev_p_copy)
        

        ## global constraints applied to the aggregation
        self.global_constraints = _global_constraints
        
        #### WIP ####
        self.collision_shapes = []
        self.graph = None
	
	## override Rhino .ToString() method (display name of the class in Gh)
    def ToString(self):
        return "WaspAggregation [name: %s, size: %s]" % (self.name, len(self.aggregated_parts))
    
    ## reset base parts
    def reset_base_parts(self, new_parts = None):
        if new_parts != None:
            self.parts = {}
            for part in new_parts:
                self.parts[part.name] = part
        
        for p_key in self.parts:
            self.parts[p_key].reset_part(self.rules)
            
    ## reset rules and regenerate rule tables for each part
    def reset_rules(self, rules):
        if rules != self.rules:
            self.rules = rules
            self.reset_base_parts()
            
            for part in self.aggregated_parts:
                part.reset_part(rules)
    
    
    ## recompute aggregation queue
    def recompute_aggregation_queue(self):
        pass
    

    ## trim aggregated parts list to a specific length
    def remove_elements(self, num):
        self.aggregated_parts = self.aggregated_parts[:num]
        for part in self.aggregated_parts:
            part.reset_part(self.rules)
        """
        if self.field is not None:
            self.recompute_aggregation_queue()
        """

    
    ## compute all possible parts which can be placed given an existing part and connection
    def compute_possible_children(self, part_id, conn_id, check_constraints = False):
        pass
    
    ## add a custom pre-computed part which has been already transformed in place and checked for constraints
    def add_custom_part(self, part_id, conn_id, next_part):
        pass
    
    #### constraints checks ####
    ## function grouping all constraints checks (not yet implemented)
    def constraints_check(self, part, trans):
        pass
    
    ## overlap // part-part collision check
    def collision_check(self, part, trans):
        part_center = part.transform_center(trans)
        
        ## overlap check
        #coll_count = 0
        for ex_part in self.aggregated_parts:
            dist = ex_part.center.distance_to_point(part_center)
            if dist < 0.001:
                return True
            """
            elif dist < ex_part.dim + part.dim:
                self.possible_collisions.append(coll_count)
            coll_count += 1
            """
        """
        ## collision check
        if self.coll_check == True:
            part_collider = part.transform_collider(trans)
            if part_collider.check_collisions_by_id(self.aggregated_parts, self.possible_collisions):
                return True
        """
        return False
    
    ## additional collider check
    def additional_collider_check(self, part, trans):
        pass
    
    ## support check
    def missing_supports_check(self, part, trans):
        pass
    
    ## global constraints check
    def global_constraints_check(self, part, trans):
        pass
    
     #### aggregation methods ####
    
    ## sequential aggregation with Graph Grammar
    def aggregate_sequence(self, graph_rules):
        pass
    
    ## stochastic aggregation
    def aggregate_rnd(self, num):
        added = 0
        loops = 0
        while added < num:
            loops += 1
            if loops > num*100:
                break
            ## if no part is present in the aggregation, add first random part
            if len(self.aggregated_parts) == 0:
                first_part = self.parts[random.choice(self.parts.keys())]
                first_part_trans = first_part.transform(Transformation())
                for conn in first_part_trans.connections:
                    conn.generate_rules_table(self.rules)
                first_part_trans.id = 0
                self.aggregated_parts.append(first_part_trans)
                added += 1
            ## otherwise add new random part
            else:
                next_rule = None
                part_01_id = -1
                conn_01_id = -1
                next_rule_id = -1
                new_rule_attempts = 0
                
                while new_rule_attempts < 10000:
                    new_rule_attempts += 1
                    part_01_id = random.randint(0,len(self.aggregated_parts)-1)
                    part_01 = self.aggregated_parts[part_01_id]
                    if len(part_01.active_connections) > 0:
                        conn_01_id = part_01.active_connections[random.randint(0, len(part_01.active_connections)-1)]
                        conn_01 = part_01.connections[conn_01_id]
                        if len(conn_01.active_rules) > 0:
                            next_rule_id = conn_01.active_rules[random.randint(0, len(conn_01.active_rules)-1)]
                            next_rule = conn_01.rules_table[next_rule_id]
                            break
                
                if next_rule is not None:
                    next_part = self.parts[next_rule.part2]
                    orientTransform = Transformation.from_frame_to_frame(next_part.connections[next_rule.conn2].flip_pln, conn_01.frame)
                    
                    ## boolean checks for all constraints
                    coll_check = False
                    add_coll_check = False
                    #valid_connections = []
                    missing_sup_check = False
                    global_const_check = False
                    
                    ## collision check
                    self.possible_collisions = []
                    coll_check = self.collision_check(next_part, orientTransform)
                    
                    """
                    ## constraints check
                    if self.mode == 1: ## only local constraints mode
                        if coll_check == False and next_part.is_constrained:
                            add_coll_check = self.additional_collider_check(next_part, orientTransform)
                            
                            if add_coll_check == False:
                               missing_sup_check = self.missing_supports_check(next_part, orientTransform)
                    
                    elif self.mode == 2: ## onyl global constraints mode
                        if coll_check == False and len(self.global_constraints) > 0:
                            global_const_check = self.global_constraints_check(next_part, orientTransform)
                    
                    elif self.mode == 3: ## local+global constraints mode
                        if coll_check == False:
                            if len(self.global_constraints) > 0:
                                global_const_check = self.global_constraints_check(next_part, orientTransform)
                            if global_const_check == False and next_part.is_constrained:
                                add_coll_check = self.additional_collider_check(next_part, orientTransform)
                                if add_coll_check == False:
                                   missing_sup_check = self.missing_supports_check(next_part, orientTransform)
                    """
                    
                    if coll_check == False and add_coll_check == False and missing_sup_check == False and global_const_check == False:
                        next_part_trans = next_part.transform(orientTransform)
                        next_part_trans.reset_part(self.rules)
                        for i in range(len(next_part_trans.active_connections)):
                            if next_part_trans.active_connections[i] == next_rule.conn2:
                                next_part_trans.active_connections.pop(i)
                                break
                        next_part_trans.id = len(self.aggregated_parts)
                        
                        ## parent-child tracking
                        self.aggregated_parts[part_01_id].children.append(next_part_trans.id)
                        next_part_trans.parent = self.aggregated_parts[part_01_id].id
                        self.aggregated_parts.append(next_part_trans)
                        
                        for i in range(len(self.aggregated_parts[part_01_id].active_connections)):
                            if self.aggregated_parts[part_01_id].active_connections[i] == conn_01_id:
                                self.aggregated_parts[part_01_id].active_connections.pop(i)
                                break
                        added += 1
                    ## TO FIX --> do not remove rules when only caused by missing supports
                    else:
                       ## remove rules if they cause collisions or overlappings
                       for i in range(len(self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules)):
                           if self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules[i] == next_rule_id:
                               self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules.pop(i)
                               break
                       ## check if the connection is still active (still active rules available)
                       if len(self.aggregated_parts[part_01_id].connections[conn_01_id].active_rules) == 0:
                           for i in range(len(self.aggregated_parts[part_01_id].active_connections)):
                            if self.aggregated_parts[part_01_id].active_connections[i] == conn_01_id:
                                self.aggregated_parts[part_01_id].active_connections.pop(i)
                                break
                else:
                    ## if no part is available, exit the aggregation routine and return an error message
                    msg = "Could not place " + str(num-added) + " parts"
                    return msg
    
    ## compute all possibilities for child-parts of the given part, and store them in the aggregation queue
    def compute_next_w_field(self, part):
        pass
    
    ## field-driven aggregation
    def aggregate_field(self, num):
        pass


# ==============================================================================
# Debugging
# ==============================================================================
if __name__ == "__main__":
    pass