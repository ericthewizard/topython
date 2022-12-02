# topython
Tools for converting scientific software from IDL to Python

### Requirements
openai

### Getting Started
The model this code uses is still in private beta, so you'll need an invite prior to using it; request an invite here:

https://openai.com/blog/openai-codex/

Once you've accepted the invite, install the latest openai library:

```bash
pip install openai
```

then set your `OPENAI_API_KEY` environment variable.

### Cost
Access to the OpenAI Codex model is free (as of November 2022) while in private beta, but will become a paid product once it's made available to the public. 

### Usage
To convert some code to Python, simply call the `topython.convert` function with the code to convert as the argument:

```python
from topython import convert
output = convert('/path/to/idl/file/my_code.pro')
```

By default, the `convert` function works on a .pro file; to submit raw code instead of a file, set the `raw` keyword to `True`.

### Optional Parameters
- `raw`: set to `True` if the input is code in a string instead of a file
- `header`: set to `True` (default) to include an example of an IDL header and PySPEDAS docstring to the model prior to doing the conversion (will include a proper docstring). Setting this option to `False` will allow you to convert slightly larger functions/procedures.
- `dynamic_tokens`: set to `True` (default) for the conversion to attempt to guess the maximum number of output tokens from the number of input tokens (significantly improves output and will limit costs when the model becomes a paid product).
- `max_tokens`: specify the exact number of output tokens (dynamic_tokens must be set to `False` to use this option)
- `token_padding`: amount of padding to add to the output tokens from the input tokens (if dynamic_tokens is set to `True`); default: 0.61 (or 61% more tokens than the input)
- `best_of`: integer specifying the number of times inference is ran on the model (default: 5); higher means better conversions, but with larger functions, the max seems to be around 5 before the model starts throwing rate limit errors. Decreasing this should decrease the cost when the model becomes a paid product. Note: 1-2 seems to do a decent job, but the default is set to 5 to try to get the best output. 

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
from topython import convert

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

Note: this is the raw output from the function, nothing was added or changed.

Not only does it produce correct code - it includes a header, even though there wasn't one in the input! This is because we showed the model an example of a header prior to requesting the conversion. 

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

Now for the magic - changing our input to:

```idl
; function that uses get_data to return the data for an input variable, 
; and store_data to save the data with a suffix
```

and again using:

```python
output = convert(input, raw=True, header=False)
```

We get:

```python

def get_and_store_data(variable, suffix):
    data = get_data(variable)
    if data is not None:
        store_data(variable + suffix, data={'x': data.times, 'y': data.y})

get_and_store_data('variable', '_suffix')
get_and_store_data('variable2', '_suffix')

```

🤯 🤯 🤯

We can modify the input slightly to ask for a docstring:

```idl
; function that uses get_data to return the data for an input variable, 
; and store_data to save the data with a suffix, with a docstring
```

and again using:

```python
output = convert(input, raw=True, header=False)
```

We get:

```python
def get_and_store_data(variable, suffix):
    """
    Get the data for a variable and store it with a suffix.

    Parameters
    ----------
    variable : str
        The variable to get the data for.
    suffix : str
        The suffix to add to the variable name when storing the data.

    Returns
    -------
    data : dict
        The data for the variable.
    """
    data = get_data(variable)
    if data is not None:
        store_data(variable + suffix, data={'x': data.times, 'y': data.y})
    return data
```

The only problem is in the 'Returns' section of the docstring: `get_data` returns a named tuple, not a dictionary. We usually return the name of the variable created, so we can change our IDL comment slightly ask for that:


```idl
; function that uses get_data to return the data for an input variable, 
; and store_data to save the data with a suffix, with a docstring,
; that returns the output variable name
```

This returns a working function, with a correct docstring:

```python
def get_and_store_data(variable, suffix):
    """
    Get data for a variable and store it with a suffix.

    Parameters
    ----------
    variable : str
        The variable to get data for.
    suffix : str
        The suffix to add to the variable name when storing the data.

    Returns
    -------
    str
        The name of the variable that the data was stored in.
    """
    data = get_data(variable)
    if data is not None:
        store_data(variable + suffix, data={'x': data.times, 'y': data.y})
    return variable + suffix
```

### Caveats
- The upper limit seems to be around 200 lines per function/procedure (depending on line density), or around 10KB
- Due to the caveat above, when converting files with multiple proceudres or functions, the `convert` routine will attempt to split the file up into individual functions, and send each one to the model independently. This splitting is based on 'end's in the IDL code, so if your functions include 'end's that aren't proper procedure/function 'end's (e.g., if you use 'end' to end an 'if' statement instead of 'endif'), you'll get some bad results; exception: 'end's that exist inside 'case' statements should be fine. 