#!/usr/bin/env python

# Import built-in
import sys
import os

# Import third-party
import jinja2
import yaml
import numpy as np
from cpc.geogrids import Geogrid
from cpc.geogrids.manipulation import interpolate

# --------------------------------------------------------------------------------------------------
# Get command-line args
#
# Make sure there are 4 command-line args
num_args = 4
if len(sys.argv) < num_args + 1:
    print(f"""Usage: {os.path.basename(__file__)} INPUT_FILE_TMPL OUTPUT_FILE_TMPL VAR DATE
  Where:
    INPUT_FILE_TMPL     Input file Jinja2 template - supports the following Jinja2 vars: 
                          - {{ var }}
                          - {{ yyyy }}
                          - {{ mm }}
                          - {{ dd }}
    OUTPUT_FILE_TMPL    Output file Jinja2 template - supports the following Jinja2 vars: 
                          - {{ yyyy }}
                          - {{ mm }}
                          - {{ dd }}
    VAR                 Variable to process (tmean, precip, 500hgt)
    DATE                Issued date to process (YYYYMMDD)""")
    sys.exit(1)
# Input file Jinja2 template
input_file_tmpl = sys.argv[1]
input_file_tmpl = os.path.expanduser(os.path.expandvars(input_file_tmpl))
# Output file Jinja2 template
output_file_tmpl = sys.argv[2]
output_file_tmpl = os.path.expanduser(os.path.expandvars(output_file_tmpl))
# Variable
variable = sys.argv[3]
# Date
date = sys.argv[4]

# --------------------------------------------------------------------------------------------------
# Load config vars
#
try:
    config = yaml.load(open('config.yml', 'r'))
except Exception as e:
    print('Couldn\'t load vars from config.yml')
    sys.exit(1)

# --------------------------------------------------------------------------------------------------
# Render file template
#
# Input file
kwargs = {
    'var': config['filename-vars'][variable],
    'yyyy': date[0:4],
    'mm': date[4:6],
    'dd': date[6:8]
}
input_file = jinja2.Template(input_file_tmpl, undefined=jinja2.DebugUndefined).render(kwargs)
kwargs['var'] = variable
output_file_tmpl = jinja2.Template(output_file_tmpl, undefined=jinja2.DebugUndefined).render(kwargs)
print(f'Input file name: {input_file}')
print(f'Output file template: {output_file_tmpl}')
# Create the directory specified in the output_file_tmpl
os.makedirs(os.path.dirname(output_file_tmpl), exist_ok=True)

# --------------------------------------------------------------------------------------------------
# Read input file and reshape as necessary
#
dtype = config['input-files']['dtype']
num_members = config['input-files']['num-members']
num_fhrs = config['input-files']['num-fhrs']
fhr_int = config['input-files']['fhr-int']
input_geogrid = Geogrid(config['input-files']['geogrid-name'])
output_geogrid = Geogrid(config['output-files']['geogrid-name'])
num_y = input_geogrid.num_y
num_x = input_geogrid.num_x
data = np.fromfile(
    input_file, dtype=dtype
).reshape((num_members, num_fhrs, num_y * num_x))

# --------------------------------------------------------------------------------------------------
# Loop over dimensions of input file
#
for f in range(num_fhrs):
    fhr = [f'{f:03d}' for f in range(0, num_fhrs * fhr_int, fhr_int)][f]
    for m in range(num_members):
        member = f'{list(range(num_members))[m]:02d}'
        # Get a slice of the data and interpolate to the output grid size
        data_slice = interpolate(
            np.fliplr(
                data[m][f].reshape((num_y, num_x))
            ), input_geogrid, output_geogrid
        )
        # Render output file name
        kwargs = {
            'fhr': fhr,
            'member': member
        }
        output_file = jinja2.Template(
            output_file_tmpl, undefined=jinja2.DebugUndefined
        ).render(kwargs)
        print(f'Writing data[{m}][{f}] to {output_file}...')
        # Write data array to a grib2 file
        data_slice.astype('float32').tofile(output_file)

