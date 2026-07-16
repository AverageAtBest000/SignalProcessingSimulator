#!/usr/bin/env python
# coding: utf-8

# In[4]:


#code BEFORE it got added to a class
import numpy as np

def mess_up_signal(original_signal, sample_rate, delay_seconds, reflection_coefficient=0.5):

    
    shift_samples = int(delay_seconds * sample_rate)
    
    reflected_signal = np.zeros_like(original_signal)
    
    if shift_samples < len(original_signal):
        reflected_signal[shift_samples:] = original_signal[:-shift_samples] * reflection_coefficient
    
    # Combine original signal and reflection
    corrupted_signal = original_signal + reflected_signal
    
    return corrupted_signal, reflected_signal


# In[5]:


#code AFTER it got added to a class
import numpy as np

class Terminator:
    
    def __init__(self, sample_rate, delay_seconds, reflection_coefficient=0.5):
        self.sample_rate = sample_rate
        self.delay_seconds = delay_seconds
        self.reflection_coefficient = reflection_coefficient

    def apply_reflection(self, original_signal):
        shift_samples = int(self.delay_seconds * self.sample_rate)
        
        reflected_signal = np.zeros_like(original_signal)
        
        if shift_samples < len(original_signal):
            reflected_signal[shift_samples:] = original_signal[:-shift_samples] * self.reflection_coefficient
        
        # Combine original signal and reflection that came back
        corrupted_signal = original_signal + reflected_signal
        
        return corrupted_signal, reflected_signal
    
    
# :)    
    
#--------------------------------------------------------
#how to use it in a pre-existing signal thing

# 1. Define your original signal data
my_signal = np.sin(np.linspace(0, 10, 1000))

# 2. Initialize the class with your parameters
corrupter = SignalCorrupter(sample_rate=44100, delay_seconds=0.05, reflection_coefficient=0.4)

# 3. Process the signal
corrupted, reflection = corrupter.apply_reflection(my_signal)



# In[ ]:




