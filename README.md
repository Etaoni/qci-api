# qiagen-clinical-insights-api
A Python 2 and 3 interface for Qiagen Clinical Insight's REST API.
Github Repository: [https://github.com/Etaoni/qci-api]

### Installation
##### Pip
```bash
pip install qci-api
```

##### Pipenv
```bash
pipenv install qci-api
```

##### Setup.py
```bash
git clone https://github.com/Etaoni/qci-api
cd qci-api
python setup.py sdist bdist_wheel
```
    

### Examples
  - Refer to the ```examples/``` folder
  
### Single Upload
  - Pull <entry> from your database
  
```python
from qci.api import upload_datapackage
from qci.classes import DataPackage

datapackage = DataPackage(<entry.values>)
upload_datapackage(datapackage)
```

### Batch Upload
  - Pull <entries> from your database
  
```python
from qci.api import upload_datapackages
from qci.classes import DataPackage

datapackages = []
for <entry> in <entries>:
    datapackages.append(DataPackage(<entry.values>))
upload_datapackages(datapackages)
```
