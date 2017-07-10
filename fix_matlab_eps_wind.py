''' Fix EPS images that contain artifacts since Matlab 2014b

Usage: python fix_matlab_eps_wind.py input-file output-file
*** must format input and output files like: "C:\\Program Files\\filedir\\filename.eps"
'''

import re # regex
import os
import sys
import subprocess
import tempfile

# if there were more functions in this module, put them before main() with main at the bottom before the boilerplate
def main(): # standard function definition
    #ret = subprocess.call('inkscape --version', shell=True) # run inkscape in shell, assign output to ret (subprocess.call is old phrasing)
    theCommand='"C:\\Program Files\\Inkscape\\inkscape.exe" --version' # fucking windows with spaces in the path
    ret = subprocess.call(theCommand, shell=True)

    if len(sys.argv) < 3: # if length of argument passed from command line is less than 3 items
        print('Usage: python fix_matlab_eps_wind.py input-file output-file')

    if ret: # if ret variable is true or == 1 (i.e. process hasnt terminated and inkscape is still running) throw error
        print('Error: You need Inkscape to convert images to a parsable format')
        return

    tmp = os.path.join(tempfile.gettempdir(), 'fix_matlab_eps.eps') # concat temporary directory path (C:\Users\tyler\AppData\Local\Temp\) and temp filename ('fix_matlab...')
    theCommand2='"C:\\Program Files\\Inkscape\\inkscape.exe" --export-area-page --export-eps='
    ret = subprocess.call(theCommand2 + tmp+' '+sys.argv[1], shell=True) # this time call inkscape, load in input file from argv, and export data as tmp
                                                                         # argv[1] is first argument, argv[0] is name of module itself
    text = '' # initialize a bunch of empty vars to be used in following for loop
    line_list = []
    line = []

    colored_patch = False

    colorbar = False
    first_colorbar = []

    f = open(tmp)
    for i in f.readlines(): # readlines() returns a list of lines from the file upon opening it
        # Ignore ends of patches because we find them manually
        if colored_patch and re.match('.* m f', i): # match any line i that ends with m f (with any number of characters before it)
            continue

        # Hold the patches to group them together
        if colored_patch and re.match('.* f', i): # find lines that code for patches
            line.append(i.replace('f', 'h')) # replace f ending with h
            line_list.append(line) # append current line to line list
            line = [] # clear var
            continue

        # End of patches with 1 color
        if colored_patch and (re.match('.*g$', i) or re.match('^Q Q$', i)) \
           and line_list:
            colored_patch = False
            last = []
            for j in reversed(line_list):
                for k in j:
                    text += k
                last = j
            up_to_m = last[0].split('m')[0]
            text += up_to_m + 'm f\n'
            line_list = []
        elif re.match('.* g$', i) or i.endswith('showpage\n'):
            colorbar = False
            colored_patch = False

            if line:
                line_list.append(line)
                line = []

            for j in line_list:
                for k in j:
                    text += k
            line_list = []

        # Patches belonging to 1 color
        if re.match('.*rg$', i):
            colored_patch = True
            text += i
            continue

        # Start of the colorbar
        if re.match('^Q q$', i):
            colorbar = True
            line_list.append(i)
            continue

        # Just append any lines of the colorbar
        if colorbar:
            line_list.append(i)

        # End of the colorbar
        if line_list[-3:] == ['Q\n', '  Q\n', 'Q\n']:
            colorbar = False
            if first_colorbar:
                for j in line_list:
                    if j.endswith(' h\n'):
                        for k in first_colorbar:
                            if k.endswith(' h\n'):
                                text += k
                    text += j
                first_colorbar = []
            else:
                first_colorbar = list(line_list)
            line_list = []
            continue

        # There was only one colorbar
        if not colorbar and first_colorbar:
            for j in first_colorbar:
                text += j
            first_colorbar = []

        # Add other stuff
        if colored_patch:
            line.append(i)
            if i.endswith('h\n') or i.endswith('f\n'):
                line_list.append(line)
                line = []
        elif not colorbar:
            text += i

    f.close()

    f = open(sys.argv[2], 'w') # open output file
    f.write(text) # copy over text from original .eps file with adjustments made in script
    f.close() # close file

# standard lines to call main() function and begin program when called directly (i.e. not by another .py module)
if __name__ == '__main__':
    main()
