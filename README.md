# topython
Tools for converting scientific software from IDL to Python

### Requirements
openai

### Examples

Starting with the input:
```idl
pro create_tplot_variable, name, suffix=suffix
  if undefined(suffix) then suffix = '_out'
  get_data, name, data=d
  store_data, name + suffix, data={x: d.x, y: d.y}
end
```

and using:

```python
output = convert(input, raw=True)
```

We get:
```python

def create_tplot_variable(name, suffix='_out'):
    """
    This function does something useful

    Parameters
    ----------
    name : str
        name of the variable
    suffix : str
        suffix to add to the name of the variable [default: '_out']

    Returns
    --------
    """
    d = get_data(name)
    store_data(name + suffix, data={'x': d.times, 'y': d.y})

```

By default, it includes a header, even though there wasn't one in the input! This is because we showed the model an example of a header prior to requesting the conversion. 

To turn off the header, use the `header` option:

```python
output = convert(input, raw=True, header=False)
```

We now get:

```python
def create_tplot_variable(name, suffix=None):
    if suffix is None:
        suffix = '_out'
    d = get_data(name)
    store_data(name + suffix, data={'x': d.times, 'y': d.y})
```