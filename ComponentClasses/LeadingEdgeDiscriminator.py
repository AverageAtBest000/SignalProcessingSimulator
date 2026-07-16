#!/usr/bin/env python
# coding: utf-8
#THIS IS THE LEADING EDGE DISCRIMINATOR
# In[9]:


#this is the code before making it into a class

import numpy as np

def apply_edge_discriminator(time_array, signal_array, threshold):

    above_threshold = signal_array >= threshold

    transitions = np.diff(above_threshold.astype(int))

    lead_indices = np.where(transitions == 1)[0] + 1
    trail_indices = np.where(transitions == -1)[0] + 1

    lead_times = time_array[lead_indices]
    trail_times = time_array[trail_indices]

    return lead_indices, lead_times, trail_indices, trail_times
#--------------------------------------------------------------
#how to add to a signal we already have

# make sure you have variables named 'my_time' and 'my_signal':
#
# idx_lead, t_lead, idx_trail, t_trail = apply_edge_discriminator(my_time, my_signal, threshold=2.5)
#
# print("Leading Edge Triggers at:", t_lead)
# print("Trailing Edge Triggers at:", t_trail)

#boom


# In[8]:


#this is the code after making it into a class

import numpy as np

class EdgeDiscriminator:
#this threshold is the only thing that sorta changed
#bascially makes it so it remembers the value thing
    def __init__(self, threshold):
        self.threshold = threshold

    def apply(self, time_array, signal_array):
        above_threshold = signal_array >= self.threshold

        transitions = np.diff(above_threshold.astype(int))

        lead_indices = np.where(transitions == 1)[0] + 1
        trail_indices = np.where(transitions == -1)[0] + 1

        lead_times = time_array[lead_indices]
        trail_times = time_array[trail_indices]

        return lead_indices, lead_times, trail_indices, trail_times

#--------------------------------------------------------------
#how to add to a signal we prob have

# make sure you have variables named 'my_time' and 'my_signal':

# discriminator = EdgeDiscriminator(threshold=2.5)

# idx_lead, t_lead, idx_trail, t_trail = discriminator.apply(my_time, my_signal)

# print("Leading Edge Triggers at:", t_lead)
# print("Trailing Edge Triggers at:", t_trail)

#boomshakalaka baby

