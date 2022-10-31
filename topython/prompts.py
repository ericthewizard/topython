
prompts = {}

prompts['dprint'] = """IDL: 
dprint, 'This is an error message', dlevel=1
Python:
logging.error('This is an error message')
IDL: 
dprint, 'This is an informational message', dlevel=2
Python:
logging.info('This is a informational message')
"""

prompts['options'] = """IDL:
options, 'variable','panel_size',0.5
Python:
options('variable', 'panel_size', 0.5)
IDL:
options, 'variable', color='r', /def
Python:
options('variable', 'color', 'r')
IDL:
options,'variable', yrange=[-0.5,15.5]
Python:
options('variable', 'yrange', [-0.5, 15.5])
"""

prompts['append_array'] = """IDL: 
append_array(arr, item)
Python:
arr.append(item)
"""

prompts['n_elements'] = """IDL: 
n_elements(array)
Python:
len(array)
"""

prompts['indgen'] = """IDL: 
indgen(16)
Python:
np.arange(16)
"""

prompts['dindgen'] = """IDL: 
dindgen(16)
Python:
np.arange(16)
"""

prompts['where'] = """IDL: 
idx = where(values ge total(values))
Python:
idx = np.argwhere(values >= np.nansum(values))
"""
prompts['get_data'] = """IDL:
get_data, 'variable', data=data
if is_struct(data) then do begin
  store_data, 'new', data={x: data.x, y: data.y}
  print, data.x
endif
Python:
data = get_data('variable')
if data is not None:
    store_data('new', data={'x': data.times, 'y': data.y})
    print(data.times)
IDL:
get_data, 'variable2', data=data2
if is_struct(data2) then do begin
  store_data, 'new2', data={x: data2.x, y: data2.y, v: data2.v}
endif
Python:
data2 = get_data('variable2')
if data2 is not None:
    store_data('new2', data={'x': data2.times, 'y': data2.y, 'v': data2.v})
"""
prompts['dlimits'] = """IDL:
get_data, e_uncor[0], data=e1_uncor, dlimits=e1_uncor_dlimits
if is_struct(e1_uncor_dlimits) then begin
    FillVal = e1_uncor_dlimits.cdf.vatt.fillval
endif
Python:
e1_uncor = get_data(e_uncor[0])
e1_uncor_dlimits = get_data(e_uncor[0], metadata=True)
if e1_uncor_dlimits is not None:
    FillVal = e1_uncor_dlimits['CDF']['VATT']['FILLVAL']
"""

prompts['uniq('] = """IDL:
spin_starts = uniq(spin_nums.Y)
Python:
spin_starts = np.unique(spin_nums.y, return_index=True)[1][1:]-1
"""

prompts['keyword_set'] = """IDL:
if keyword_set(data) then begin
   return
endif
Python:
if data is not None:
    return
"""

prompts['units_name'] = """IDL:
units = data.units_name
Python:
units = data['units_name']
IDL:
mass = data.mass
Python:
mass = data['mass']
"""

PROMPT_HEADER = '''IDL:
;+
; PROCEDURE:
;         rbsp_rbspice_pad_spinavg
;
; PURPOSE:
;         This function does something useful
;
; KEYWORDS:
;         probe:        RBSP spacecraft indicator [Options: 'a' (default), 'b']
;         datatype:     desired data type [Options: 'TOFxEH' (default), 'TOFxEnonH']
;
; OUTPUT:
;
;-
pro rbsp_rbspice_pad_spinavg, probe=probe, datatype = datatype
Python:
def rbsp_rbspice_pad_spinavg(probe='a', datatype='TOFxEH'):
    """
    This function does something useful

    Parameters
    ----------
    probe : str
        RBSP spacecraft indicator [Options: 'a' (default), 'b']
    datatype : str
        desired data type [Options: 'TOFxEH' (default), 'TOFxEnonH']

    Returns
    --------
    """
'''

PROMPT_START = """#IDL to Python:
"""