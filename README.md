# makeDesignSpace
Guess the weight axis designspace values from a group of UFOs. I don't know how useful it is, but I needed it. 

`makeDesignSpace` that takes a folder of UFOs and tries to  "score" them according to weight name references in the style name.  Obviously this is a *guessing* process that can go wrong in many ways.

The goal is not to get it right all the time, but to get started quickly.

If your font collection is had wild and crazy names: more power to you, but then this won't make the right guesses. Then it is probably less work
to just make the designspace file the conventional way then to rename the fonts to match this script.

* Fonts that belong together will have the same family name.
* weights are indicated by their OS2 name https://docs.microsoft.com/en-us/typography/opentype/spec/os2#wtc
* italic is mentioned in the style name
* it does not look at the filename
* It does not look at OS2 values as development fonts don't always have these set. 
* It does not *validate* the designspace. If there are multiple candidates for a particular weight (Normal / Regular) then you have to make some edits. Also if there is no difference between the minimum and maximum axis values it won't be a valid designspace.

It will save a designspace file named `myoutputfolder/familyName_[Roman|Italic]_axisName.designspace`

## Usage:
```python
from makeDesignSpace import makeDesignSpace
myUFOPaths = ['one.ufo', 'two.ufo']
makeDesignSpace(ufoPaths, "myoutputfolder")
```