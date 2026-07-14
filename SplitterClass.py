#!/usr/bin/env python
# coding: utf-8

# In[15]:


class ChannelSplitter:
    def __init__(self, attenuation_factor=0.5, ch_noise_std=0.004, ch2_blur_sigma=3.0):
        self.attenuation_factor = attenuation_factor
        self.ch_noise_std = ch_noise_std
        self.ch2_blur_sigma = ch2_blur_sigma

    def split(self, pmt_signal, time_array):
        if pmt_signal is None or time_array is None:
            raise ValueError("Input signal and time array cannot be None.")
            
        signal_len = len(time_array)

        noise_ch1 = np.random.normal(0, self.ch_noise_std, signal_len)
        channel_1 = (pmt_signal * self.attenuation_factor) + noise_ch1
        yield channel_1

        noise_ch2 = np.random.normal(0, self.ch_noise_std, signal_len)
        degraded_signal = gaussian_filter1d(pmt_signal, sigma=self.ch2_blur_sigma)
        channel_2 = (degraded_signal * self.attenuation_factor) + noise_ch2
        yield channel_2


# In[ ]:




