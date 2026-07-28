

# Signal Processing Simulator

This project allows an experimenter to design/pre-plan a simulated analog to digital path. Using the classes within this repo, one can generate a PMT signal, run it through cables, splitters, amplifiers, and other components. Code to gather and display signal loss to the user is currently being implemented. 

## Getting Started 

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AverageAtBest000/SignalProcessingSimulator
   cd SignalProcessingSimulator
   ```
   
2. **Set up a virtual environment (Recommended):**

   If you do not have the ```venv``` package installed, run :
   
   ```bash
   sudo apt update
   sudo apt install python3-venv
   ```
   Then, to create a virtual environment, run :
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **To run the example circuit:**
   ```bash
   python3 main.py
   ```
   
__________________________________________________________________________________________________________________________________________
CLASS OVERVIEWS

| File Name | Code Summary | Impact |
|-------|-------------------|-----------------------|
|```Amplifier```| This file contains an amplifier class that increases the amplitude of a signal by a given gain | Increases signal amplitude and may affect how fast the signal rises |
|```Cable```| This file contains the cable class that simulates a cable with customizable properties, such as length | Delays signal times/reduces amplitude relative to cable width and its characteristic impedance |
|```Digitizer```| This file contains the digitizer class, which takes in an analog signal and returns a digitized waveform| Discretizes the time, and voltage of a signal |
|```LeadingEdgeDiscriminator```| This file contains the LED class, which finds the moment that an input signal goes above a certain threshold | Causes timing delays because it triggers at differing moments (depending on signal size/noise level) and causes a loss in amplitude data |
|```SignalGenerator```| This file contains the Signal generator class that creates a synthetic PMT signal | This is the simulated signal
|```Splitter```| This file contains the splitter class, which simulates a resistive splitter and divides one input signal into two  | Reduces a signal's amplitude depending on the provided resistor values. Does not change the timing/shape
|```Terminators```| This file contains the terminator class that'll represent and control how much of a signal will bounce back | May add reflection to the waveform |
|```Connectors```| This code is a connector class that calculates how much voltage decreases from a signal when its plugged into a circuit | May completely flatten or distort the pulse |
|```init```| This code has all the classes we created in one place so we are able to import and use them for our signal |

Classes were use in the development of the project in order to increase code maintainability/ 



## ```SignalGenerator.py```

The ```SignalGenerator.py``` file contains the ```Generator``` class. The ```Generator``` class contains the class method ```get_PMT_signal()``` which returns a synthetic signal that is modeled after a photo-multiplier tube signal. To do this, we used a double exponential, initially represented as:

$$
    f(t) = e^{ \frac{-(t - t_0)}{ \tau_f} } - e^{ \frac{-(t - t_0)}{ \tau_r} } 
$$

The generator was later modified to use the normalized function :

$$
    f(t) =  \frac {e^{ \frac{-(t - t_0)}{ \tau_f} } - e^{ \frac{-(t - t_0)}{ \tau_r} }} { \tau_f - \tau_r} 
$$

Implemented in code as: 

```Python
def normalized_double_exponential(cls, time_array, t_0, Tao_fall, Tao_rise): 
        raw_wave =  ( np.exp( -(time_array-t_0) / Tao_fall) - np.exp( -(time_array - t_0) / Tao_rise )  ) / (Tao_fall - Tao_rise)
        return np.where(time_array >= t_0, raw_wave, 0)
```
where ```np.where(time_array >= t_0, raw_wave, 0)``` prevents the pulse from existing before the event begins. 


``` get_arrival_rate()```  multiplies the normalized double exponential by ``` mean_number_photoelectons``` : 

$$
    \lambda(t) = N_{expected}f(t)
$$ 

Where $\lambda$ outputs a measurement in Photo-elections per second. Because $f(t)$ integrates to one :

$$
    \int  \lambda(t) \ dt = N_{expected}
$$

*Function for arrival rate calculation*
```python
def get_arrival_rate(cls, mean_number_photoelectrons, scintillator_double_exponential ):
        return mean_number_photoelectrons * scintillator_double_exponential
```

In ```get_PMT_singal()```, we then calculate the time delta between each time step, ```dt```. Multiplying the result of ```get_arrival_rate()``` by ```dt``` yields an array ```expected```, where ```expected[i]``` gives you the number of photo-electrons that are expected to arrive during time bin ```i```.


The ```expected``` array is then used to draw from a Poisson distribution in order to calculate the actual number of photo-electron arrivals at each time bin. 

```Python
        photoelectron_arrivals = rng.poisson(lam=expected, size=len(expected))
```


A for loop is then used to sum the signal produced by each photo-electron at each time bin using ```get_photoelecton_voltage```. The parameters used are : ```polarity```, ```SPE_pulse_area```, ```relative_gain```, and  ```double_exponential_SPE```. Where : 

* ```SPE_pulse_area``` represents the area under the pulse generated by a photo-electron. This can either be passed in directly using ```pulse_area_method = "direct"``` and passing in the desired ```SPE_pulse_area``` or estimated using  ```pulse_area_method = "estimate_from_g_r"```  and passing in ```terminator_resistance``` and ```PMT_gain```.

* ```relative_gain``` is calculated using a normal distribution with a mean of one and a deviation of ```relative_gain_sigma```, passed in by the user. 

* ```double_exponential_SPE``` is passed in using the ```normalized_double_exponential``` function with ```Tao_fall``` and ```Tao_rise``` set using their respective spe values and ```t_0``` set to the time when the photo-electron arrived. 

### How to Use



## ```Splitter.py```
The ```Splitter.py``` file contains the ```Slpitter``` class. The ```Slpitter``` class contains method ```split()```, which returns two open circuit voltage arrays (one for each branch), as well as their corresponding impedance values in order to apply load to the open circuit later. To do this, we first calculate the impedance of the source branch : 

$$
    Z_{SourceBranch} = Z_{SourceImpedance} + R_1 
$$

We can do the same for the remaining branches:

$$
    Z_{Branch1} = Z_{Load1} + R_2 
$$

$$
    Z_{Branch2} = Z_{Load2} + R_1 
$$

This allows us to calculate the impedance experienced by the two loads. We do this by removing the load of whatever branch we are calculating the equivalent impedance from in order to continue our convention of return open circuit thevenin signals: 

$$
    Z_{out1} = R_2 + Z_{SourceBranch}||Z_{Branch2}
$$

$$
    Z_{out2} = R_3 + Z_{SourceBranch}||Z_{Branch1}
$$



## ```Cable.py```
The ```Cable.py``` file contains the ```Cable``` class. The ```Cable``` class contains method ```propagation()```, which takes in a unloaded, open circuit voltage array and returns a signal loaded with the both the source impedance and the load impedance. Reflections and attenuation is taken into account. To do this, we first calculate delay:

$$
    delay = \frac{L_m}{(V_f)(c)}
$$

where $L_m$ is cable length in meters, $V_f$ is the cable's velocity factor, and $c$ is the speed of light. Next the attenuation factor is calculated: 

$$
    A = 10^{-(\alpha L_m) / 20}
$$

where $\alpha$ is the attenuation per meter in dB. Next we calculate the reflection coefficient at both the load and the source: 

$$
    \Gamma_L = \frac{Z_L - Z_0}{Z_L + Z_0}
$$

$$
    \Gamma_S = \frac{Z_S - Z_0}{Z_S + Z_0}
$$

Next we can calculate the wave launches into the cable, taking into account that the a voltage divider is formed between the cable and the signal source. 


$$
    V_{pulse}(t) = V_in(t) - V_{baseline}
    V_L(t) = V_{pulse}(t)\frac{Z_0}{Z_S + Z_0}
$$

applying the attenuation factor yields the incident wave:

$$
    V_{pulse}(t) = A V_L(t)
$$

Next, we use a loop to apply the effect of the bounce-back: 


$$
   V_{contribution}(t) = (1 - \Gamma_L)\sum_{n = 0}^{N} (\Gamma_L\Gamma_SA^2)  V_{pulse}(t - t_{delay,n})
$$

## ```Connector.py```
The ```Connector.py``` file contains the ```Connector``` class. The ```Connector``` class contains method ```connect()```, which takes in a unloaded, open circuit voltage array and returns a signal loaded with the load impedance. Reflections and attenuation are not taken into account. As a result, this class simply acts as a voltage divider:

$$
   V_{loaded}(t) = (V_{in}(t) - V_{baseline}) \frac{ Z_{load} }{ Z_{load} + Z_{source} } 
$$

## ```Amplifier.py```
The ```Amplifier.py``` file contains the ```Amplifier``` class. The ```Amplifier``` class contains method ```amplify()```, which takes in a loaded voltage array and returns a open circuit Thevenin voltage signal. To do this, we first apply the gain passes in by the user:

$$
   V_{pulse}(t) = V_{in}(t) - V_{baseline}
   V_{amplified}(t) = A_v V_{pulse}
$$

Where A_v is the voltage gain. Gain may either be inputted as a unit-less quantity or in units of decibels. If it gain is given in decibels, it will be converted into a linear, unit-less multiplier. 



