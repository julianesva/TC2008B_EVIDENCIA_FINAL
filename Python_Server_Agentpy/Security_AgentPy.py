import agentpy as ap
import json
import random
from owlready2 import *

# Create the ontology
onto = get_ontology("file://onto.owl")

with onto:
    #===================SECURITY PERSON ONTLOGY SECTION===================
    class Security_P(Thing):
        pass
    
    class has_decision(DataProperty, FunctionalProperty):
        domain = [Security_P]
        range = [str] # Property acting as the decision of the security person. 
        # Status = "Normal" or "Alert".
    
    #===================CAMERA ONTLOGY SECTION===================
    class Camera(Thing):
        pass

    class has_id(DataProperty, FunctionalProperty):
        domain = [Camera]
        range = [int] # Property acting as a variable to store the id of each camera instance.
        
    #===================DRON ONTLOGY SECTION===================
    class Dron(Thing):
        pass
    
    #===================DRON AND CAMERA ONTLOGY SECTION (PROPERTIES IN COMMON)===================
    class has_status(DataProperty, FunctionalProperty):
        domain = [Camera, Dron]
        range = [str] # Status = "Normal" or "Detected".
        
    class has_action(DataProperty, FunctionalProperty):
        domain = [Camera, Dron]
        range = [int] # Property acting as a variable to store the number of times that a Camera or Dron make an alert of an intruder.
    


# Save the ontology
onto.save()



class CamAgent(ap.Agent):
    def setup(self):
        self.onto_camera = onto.Camera(f"camera_{self.id}")  # Use the ID in the instance name
        self.onto_camera.has_status = "Normal"
        self.onto_camera.has_action = 0
        self.perception_data = {}
        self.rules = [
            ({"perception": {"F": 1}, "is_holding": False}, "grab_F"),
            ({"perception": {"B": 1}, "is_holding": False}, "grab_B"),
            ({"perception": {"L": 1}, "is_holding": False}, "grab_L"),
            ({"perception": {"R": 1}, "is_holding": False}, "grab_R"),
            ({"perception": {"F": 3}, "is_holding": True}, "drop_F"),
            ({"perception": {"B": 3}, "is_holding": True}, "drop_B"),
            ({"perception": {"L": 3}, "is_holding": True}, "drop_L"),
            ({"perception": {"R": 3}, "is_holding": True}, "drop_R"),
        ]











class SecurityDepartmentModel(ap.Model):
    def setup(self):
        self.num_cams = self.p.num_cams
        self.num_dron = self.p.num_dron
        self.num_securityper = self.p.num_secper
        self.current_step = 0

        self.cams = ap.AgentList(self, self.num_cams, CamAgent)
        
        
        for i, cam in enumerate(self.cams):
            cam.id = i  # Assign the unique ID
            cam.onto_camera.has_id = i  # Update the ontology with the correct ID
            
        #self.data = {
        #    'steps_to_completion': None,
        #    'robot_movements': {cam.onto_camera.id: 0 for robot in self.robots}
        #}