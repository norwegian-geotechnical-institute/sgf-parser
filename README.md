# sgf-parser

Parser for data from geotechnical field investigations in the data format 
specified in Report 3:2012E from the Swedish Geotechnical Society /
[Svenska Geotekniska Föreningen](http://sgf.net/) (SGF).

This package is inspired by the [libsgfdata](https://github.com/emerald-geomodelling/libsgfdata) 
package by [EMerald Geomodelling](https://www.emerald-geomodelling.com/).

Latest releases see [CHANGES.md](CHANGES.md)

# Installation (end user) 

```bash
pip install sgf-parser
```

## Basic usage

```python
from sgf_parser import Parser

with open("tests/data/cpt-test-3.cpt", "rt") as file:
    # The test file only contains one method
    [method] = Parser().parse(file)

print(repr(method))
# <MethodCPT CPT method_data=[<MethodCPTData 1.000>, <MethodCPTData 1.020>, <MethodCPTData 1.040>, 
# <MethodCPTData 1.060>, <MethodCPTData 1.080>, <MethodCPTData 1.100>, <MethodCPTData 1.120>, ...,
# <MethodCPTData 24.940>, <MethodCPTData 24.960>, <MethodCPTData 24.980>]>


method.model_dump(exclude={'method_data'}, exclude_defaults=True)
# {'location_name': 'Test', 'project_number': '1234', 'method_type_string': '107A', 
# 'conducted_at': datetime.datetime(2019, 9, 5, 11, 5), 'predrilling_depth': Decimal('1.00'), 
# 'cone_reference': '5349', 'cone_area_ratio': Decimal('0.844'), 'sleeve_area_ratio': Decimal('0'), 
# 'application_class_depth': <ApplicationClass.ONE: 1>, 'application_class_resistance': <ApplicationClass.ONE: 1>, 
# 'application_class_friction': <ApplicationClass.ONE: 1>, 'application_class_pressure': <ApplicationClass.ONE: 1>, 
# 'depth_top': Decimal('1.000'), 'depth_base': Decimal('24.980'), 'stopcode': 90}

method.stopcode
# 90

len(method.method_data)
# 1200

```

# Getting Started developing

1. Software dependencies

   - Python 3.11 or higher
   - uv
   - ruff code formatter

2. Clone this repository

3. Install

   `uv sync`


# Build and Test

Run in the project root folder: 

    uv run pytest 

Build the package wheel: 

    uv build

# Publish

# TODOs

- [ ] Implement everything
- [ ] Do the rest


# Contribute

Please start by adding an issue before submitting any pull requests.

