# make quick and dirty designspace with open fonts
from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, InstanceDescriptor, AxisDescriptor, RuleDescriptor
from fontParts.fontshell import RFont
from pprint import pprint
import os
import glob

"""

A rough and quick script that takes a folder of UFOs and tries to 
"score" them according to weight name references in the style name. 
Obviously this is a guessing process that can go wrong in many ways.

The goal is not to get it right all the time, but to get started quickly.

If your font collection is had wild and crazy names: more power to you, 
but then this won't make the right guesses. Then it is probably less work
to just make the designspace file the conventional way then to rename
the fonts to match this script.

It assumes a couple of things: 
    - fonts that belong together will have the same family name.
    - weights are indicated by their OS2 name
        https://docs.microsoft.com/en-us/typography/opentype/spec/os2#wtc
    - italic is mentioned in the style name
    - it does not look at the filename.

It does not look at OS2 values as development fonts don't always have these set.
It does not validate the designspace. If there are multiple candidates for a
particular weight (Normal / Regular) then you have to make some edits. Also if
there is no difference between the minimum and maximum axis values it won't be
a valid designspace.

It will save a designspace file named <familyName>_[romans|italics]_<axisName>.designspace.

"""

weights = [
    ('thin', 100),
    ('extralight', 200),
    ('ultralight', 200),
    ('light', 300),
    ('normal', 400),
    ('regular', 400),
    ('medium', 500),
    ('semibold', 600),
    ('demibold', 600),
    ('bold', 700),
    ('extrabold', 800),
    ('ultrabold', 800),
    ('black', 900),
    ('heavy', 900),
    ]

families = {}
def makeDesignSpace(ufoPaths, outputFolder):
    hasWeight = False
    minWeight = None
    maxWeight = None
    allFonts = [RFont(path) for path in ufoPaths]
    #print(allFonts)
    axisName = "weight"
    for f in allFonts:
        hasItalic = False
        hasRoman = False
        if f.info.familyName is None:
            continue
        if f.info.styleName is None:
            continue
        if not f.info.familyName in families:
            families[f.info.familyName] = dict(Roman=[], Italic=[])
        d = dict(weight=None, width=None, font=None)
        d['font'] = f
        sn = f.info.styleName.lower()
        print('f.info.styleName', f.info.styleName)
        sn = sn.replace("-", "")
        sn = sn.replace(" ", "")
        for i in ['italic', 'ita', 'oblique']:
            if i in sn:
                hasItalic = True
                sn = sn.replace(i, '')
                print('\thasItalic')
                break
        print('\tscoring with', sn)
        for name, value in weights:
            if name in sn:
                d['weight'] = value
                hasWeight = True
                if not minWeight:
                    minWeight = value
                else:
                    minWeight = min(minWeight, value)
                if not maxWeight:
                    maxWeight = value
                else:
                    maxWeight = max(maxWeight, value)
        if hasItalic:
            families[f.info.familyName]['Italic'].append(d)
        else:
            families[f.info.familyName]['Roman'].append(d)
    for name, data in families.items():
        for style in ['Roman', 'Italic']:
            if not data[style]:
                continue
            docName = "%s_%s_%s.designspace" % (name, style, axisName)
            #print('docName', docName)
            ds = DesignSpaceDocument()
            a = AxisDescriptor()
            a.name = "weight"
            a.tag = "wght"
            a.minimum = minWeight
            a.default = minWeight
            a.maximum = maxWeight
            if minWeight == maxWeight:
                print("No weight extremes: only %3.3f" % minWeight)
            ds.addAxis(a)
            sortedWeights = {}
            for m in data[style]:
                print("\t--", m['weight'], m['font'].path)
                mm = SourceDescriptor()
                mm.familyName = m['font'].info.familyName
                mm.styleName = m['font'].info.styleName
                mm.location = dict(weight=m['weight'])
                mm.path = m['font'].path
                mm.muteKerning = False
                if m['weight'] == a.default:
                    mm.copyLib = True
                if not m['weight'] in sortedWeights:
                    sortedWeights[m['weight']] = []
                else:
                    print("hmm, multiple sources with the same weight value")
                sortedWeights[m['weight']].append(mm)

            k = list(sortedWeights.keys())
            k.sort()
            for v in k:
                for mm in sortedWeights[v]:
                    ds.addSource(mm)
            ds.write(os.path.join(outputFolder, docName))

if __name__ == "__main__":
    for path in glob.glob("./test_0*/*.ufo"): 
        ufoPaths = glob.glob(path)
        makeDesignSpace(ufoPaths, os.getcwd())