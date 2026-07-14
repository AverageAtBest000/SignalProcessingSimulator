#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np

class Splitter:
    def _init_(self, time_array, volts_array, impedance_to_out1, impedance_to_out2):
        self.time_array = np.array(time_array)
        self.volts_array = np.array(volts_array)
        self.z_out1 = impedance_to_out1
        self.z_out2 = impedance_to_out2
        
    def split(self, r1, r2, r3):
        branch1 = r2 + self.z_out1
        branch2 = r3 + self.z_out2
        
        z_parallel = (branch1 * branch2) / (branch1 + branch2)
        
        v_node = self.volts_array * (z_parallel / (r1 + z_parallel))
        
        v_out1 = v_node * (self.z_out1 / branch1)
        v_out2 = v_node * (self.z_out2 / branch2)
        
        return v_out1, v_out2

