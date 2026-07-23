

# Signal Processing Simulator

This project allows an experimenter to design/pre-plan a simulated analog to digital path. Using the classes within this repo, one can generate a PMT signal, run it through cables, splitters, amplifiers, and other components. Code to gather and dysplay signal loss to the user is currently being implemented. 

## Getting Started 

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AverageAtBest000/SignalProcessingSimulator
   cd SignalProcessingSimulator
   ```

2. **Set up a virtual environment (Recomended):**

   If you do not have the venv package installed, run :
   
   ```bash
   sudo apt update
   sudo apt install python3-venv
   ```
   then, to create a virtual enviroment, run :
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

| File Name | our code (python) | effect on signals |
|-------|-------------------|-----------------------|
|Amplifier| This file contains an amplifier class that increases the amplitude of a signal by a given gain | Increases signal amplitude and may affect how fast the signal rises |
|Cable| This file contains the cable class that simulates a cable with customizable properties, such as length | Delays signal times/reduces amplitude relative to cable width and its characteristic impedance |
|Digitizer| This file contains the digitizer class, wich takes in an analog signal and returns a digitized waveform| Discretizes the time, and voltage of a signal |
|LeadingEdgeDiscriminator| This file contains the LED class, wich finds the moment that an input signal goes above a certain threshold | Causes timing delays because it triggers at differing moments (depending on signal size/noise level) and causes a loss in amplitude data |
|SignalGenerator| This file contains the Signal generator class that creates a synthetic PMT signal | This is the simulated signal
|Splitter| This file contains the splitter class, wich simulates a resistive splitter and divides one input signal into two  | Reduces a signal's amplitude depending on the provided resistor values. Does not change the timing/shape
|Terminators| This file contains the terminator class that'll represent and control how much of a signal will bounce back | May add reflection to the waveform |
|Connectors| This code is a connector class that calculates how much voltage decreases from a signal when its plugged into a circuit | May completely flatten or distort the pulse |
|init| This code has all the classes we created in one place so we are able to import and use them for our signal |

Classes were use in the development of the project in order to increase code maintainability/ 



## SignalGenerator.py

The ```SignalGenerator.py``` file contains the ```Generator``` class. The ```Generator``` class contains the class method ```get_PMT_signal()``` wich returns a synthetic signal that is modeled after a photomultiplier tube signal. To do this, we used a double exponential, initially represented as:

$$
    f(t) = e^{ \frac{-(t - t_0)}{ tau_f} } - e^{ \frac{-(t - t_0)}{ tau_r} } 
$$

The generator was later modified to use the normalized function :

$$
    f(t) =  \frac {e^{ \frac{-(t - t_0)}{ tau_f} } - e^{ \frac{-(t - t_0)}{ tau_r} }} { tau_f - tau_r} 
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

This equation yields units of $\frac{PE}{s}$. Because $f(t)$ integrates to one :

$$
    \int  \lambda(t) \,dt = N_{expected}
$$

*Function for arrival rate calculation*
```python
def get_arrival_rate(cls, mean_number_photoelectrons, scintillator_double_exponential ):
        return mean_number_photoelectrons * scintillator_double_exponential
```

In ```get_PMT_singal()```, we then calculate the time delta between each time step, ```dt```. Multiplying the result of ```get_arrival_rate()``` by ```dt``` yields an array ```expected```, where ```expected[i]``` gives you the number of photoelectrons that are expected to arrive during time bin ```i```.


The ```expected``` array is then used to draw from a poisson distribution in order to calculate the actual number of photoelectron arrivals at each time bin. 

```Python
        photoelectron_arrivals = rng.poisson(lam=expected, size=len(expected))
```


A for loop is then used to sum the signal produced by each photoelectron at each time bin using ```get_photoelecton_voltage```. The parameters used are : ```polarity```, ```SPE_pulse_area```, ```relative_gain```, and  ```double_exponential_SPE```. Where : 

* ```SPE_pulse_area``` represents the area under the pulse generated by a photoelectron. This can either be passed in directly using ```pulse_method_area = "direct"``` and pasing in the desired ```SPE_pulse_area``` or estimated using  ```pulse_method_area = "estimate_from_g_r"```  and passing in ```terminator_resistance``` and ```PMT_gain```.

* ```relative_gain``` is calculated using a normal distribution with a mean of one and a deviation of ```relative_mean_sigma```, passed in by the user. 

* ```double_exponential_SPE``` is passed in using the ```normalized_double_exponential``` function with ```Tao_fall``` and ```Tao_rise``` set using their respective spe values and ```t_0``` set to the time when the photoelectron arrived. 

### How to Use



## Digitizer.py

The ```SignalGenerator.py``` file contains the ```Generator``` class. The ```Generator``` class contains the class method ```get_PMT_signal()``` wich returns a synthetic signal that is modeled after a photomultiplier tube signal. To do this, we used a double exponential, initially represented as:
