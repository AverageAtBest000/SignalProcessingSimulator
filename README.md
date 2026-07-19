# Signal Processing Simulator

This project is to let an experimenter design/pre-plan a simulated signal and run it through cables, splitters, or amplifiers and seeing how much the signal reflects, distorts, or messes up before reaching the digitizer.
__________________________________________________________________________________________________________________________________________
COMPUTER CLASSES

| files | our code (python) | how if affects signal |
|-------|-------------------|-----------------------|
|Amplifier| This code is an amplifier class that'll amplify a simulated signal | Increases signal amplitude but can affect how fast the signal rises |
|Cable| This code is a cable class that'll simulate a real cable for us to run our signal through | Delays signal times/reduces amplitude the longer the cable is |
|Digitizer| This code is a digitizer class that'll turn a smooth signal into digital steps like a real analog digital converter | Electronic device that converts signals to digital data |
|LeadingEdgeDiscriminator| This code is a LED class that'll find the moment that our signal will rise/fall on a certain level | Causes timing delays because it triggers at different moments (depending on signal size/noise level) |
|SignalGenerator| This code is a signal generator class that'll create a realistic noisy PMT signal | This is the simulated signal
|Splitter| This code is a splitter class that'll simulate a resistive splitter and divide one input signal into two output signals | Reduces a signals amplitude by half, but not changing the timing/shape
|Terminators| This code is a terminator class that'll represent and control how much of a signal will bounce back | How much of the signal reflects back at the end |

We put everything into classes to make our code more organized and neat rather than there being stacks on stacks of long code



##SignalGenerator.py

The ```SignalGenerator.py``` file contains the ```Generator``` class. The ```Generator``` class contains the class method ```get_PMT_signal()``` wich returns a synthetic signal that is modeled after a photomultiplier tube signal. To do this, we used a double exponential, initially represented as:

$$
    f(t) = e^{ \frac{-(t - t_0)}{ tau_f} } - e^{ \frac{-(t - t_0)}{ tau_r} } 
$$

The generator was later modified to use the normalized function :

$$
    f(t) =  \frac {e^{ \frac{-(t - t_0)}{ tau_f} } - e^{ \frac{-(t - t_0)}{ tau_r} }} { tau_f - tau_r} 
$$

This allowed for easier integration with out other components:

1. The normalized equation now yields units of $\frac{1}{s}$. Multiplying by a constant, A, with units representing the number of photoelectrons yields units of $\frac{PE}{s}$, a rate representing photoelectrons per second. This was not possible previously as $\int{f(t)} \neq 1$, disallowing A from representing the mean number of photoelectrons. 

2.



