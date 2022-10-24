# GUI overview

The GUI of OccuPy allows you to open maps and view them as sliced 2D images. OccuPy is not meant to visualize the 
map in any great detail, this is for you to make appropriate consistency checks. For fine analysis, the GUI will 
call out to open ChimeraX, a much more sophisticated visualization tool 

![image](https://drive.google.com/uc?export=view&id=10KrTBE-MLiQ4wu7kfjIKcupYLvydnxxu)


## Input map
The map to be used as input. When you run OccuPy through the GUI it will the currently selected map. 
OccuPy supports cubic .map and .mrc files. Occasionally, .ccp4 files cause issues. 

NOTE 1: OccuPy was designed to expect unsharpened maps with solvent noise, so it's best to not 
mask or post-process you map. In most cases this too is fine, but it's not recommended. 

NOTE 2: Machine-learning tools alter the maps in ways that OccuPy was not designed to anticipate. If you provide a 
map that has been altered by machine-learning methods, the output should be considered vey unreliable.

There is also an "emdb" button to fetch and unzip the main map of any EMD entry. 

---

## Scale Kernel Settings
When you provide an input map, OccuPy checks the box dimensions and voxel size. Based on this, it calculates 
suggested parameters to estimate the local scale with accuracy and confidence. 

If you change these parameters, parameters below may be updated. Changing some of these parameters will alter the 
local scale estimate, so leave them unchanged until you have gone through one of the specific tutorials and 
understand what they do. 

---

## Modification options
In some cases you may want to change the input map based on the scale estimate. This is where you do that. 

If you have not estimated an appropriate scale, this is still coupled to the "plot" tab of the viewer. By enabling 
one or more of the available modification types and dragging the slider, you will update the plot. If you have an 
input map and appropriate scale loaded, this will also interactively update the "preview" tab. More on this later. 
 
---

## Optional/extra 
These are options that you would normally not use, but that you might want to play with in certain cases. You can 
skip this section for now, leaving them at default values.
### Limit box size 
OccuPy down-samples the input map to this size for all internal calculations, using a Fourier-crop (low-pass) 
procedure. This makes OccuPy use less memory and run faster. Any modified output is zero-padded in Fourier space to 
match the input dimension. 
### Ouput lowpass 
This is only relevant for modified output. Beyond the limited box-size described above, OccuPy applies any 
modification on the full-resolution input, not the low-passed input. So if the output should be low-passed, this 
must be specified. 
### Naive normalization
This is an option to ignore the tile size specified in the kernel settings. In this case, the scale estimation 
becomes very sensitive to the Tau percentile (also a kernel setting), which might be desirable in some very special 
circumstances. 
### Histogram-match to input
Histogram-matching is a procedure to make the greyscale and contrast of two images as equal as possible. In some 
cases this might be desirable to enforce, but most of the time the greyscale of the output will very closely match 
the input anyway. 

---

## The viewer

### Input 
The map currently selected in the "input map" drop-down menu above. 
### Scale
The map currently selected in the "scale map" drop-down menu **below**. You can either add files to this drop-down 
by browsing or by running OccuPy. 
### Conf. 
The estimated solvent confidence from the previous time OccuPy was run. This is based on the estimated solvent model,
which can be viewed on the tab adjacent to the output log. The confidence is used to restrict any modification, so 
that solvent isn't amplified or attenuated.
### Sol.def
The map currently selected in the "solvent def" drop-down menu below. The solvent definition restricts the 
estimation of a solvent model. This is not typically required. 
### Preview
If you have an input and occupancy-mode scale selected, this will show a preview of the modification. **This does 
not account for confidence and solvent compensation, and will look worse than the actual output**. 

---

## The output log 
This will document what is happening, for our convenience. But everything is also documented in the full log, which 
you can access either through the menu or by double-clicking the output log *tab*. 

---

## The Menu 
Control over where OccuPy writes output, and other conventional options. 



