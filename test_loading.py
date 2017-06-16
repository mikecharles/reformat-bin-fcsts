#!/usr/bin/env python

import numpy as np
from cpc.geogrids import Geogrid
from cpc.geofiles.loading import load_ens_fcsts
from cpc.geoplot import Geomap, Geofield

issued_dates = ['20170608']
# fhrs = range(0, 768 + 1, 12)
fhrs = ['120']
# members = range(0, 51)
members = [f'{m:02d}' for m in range(0, 5)]
file_tmpl = '/cpc/model_realtime_dev/ecens/{{ yyyy }}/{{ mm }}/{{ dd }}/00/ecens_{{ yyyy }}{{ mm }}{{ dd }}_00z_f{{ fhr }}_m{{ member }}_tmean.bin'
data_type = 'binary'
geogrid = Geogrid('1deg-global')
unit_conversion = 'degK-to-degC'

dataset = load_ens_fcsts(issued_dates, fhrs, members, file_tmpl, data_type, geogrid,
                         unit_conversion=unit_conversion, yrev=True, debug=True)

geomap = Geomap(domain='global', projection='mercator')
geofield = Geofield(dataset.ens[0, 0], geogrid, levels=np.arange(-30, 30, 2))
geomap.plot(geofield)
geomap.save('test.png')

pass
