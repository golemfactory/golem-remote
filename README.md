# golem-remote

MVP version of library for wrapping Python functions to run on golem.  

Work in progress. Working revision: `1aa80d62032ef07d2d285669eb009712b4759096` here and `e7af451a600ca6e608bce7d46831975b3da4349b` in `golemfactory/golem@runf`.
Current state: working function (and closure) execution, no filesystem support.

### Description
The goal of this library is to provide wrappers analogous to these in [Ray](https://github.com/ray-project/ray). This is how it should look like from the users perspective:

Without Golem:
```python
import time

def f(x):
    time.wait(30) # really expensive call
    return 2*x

results = []
for i in range(100):
    results.append(f(i))
```

With Golem:
```python
import time
import golem_remote as golem

golem.init()

@golem.remote
def f(x):
    time.wait(30) # really expensive call
    return 2*x

results_futures = []
for i in range(100):
    results_futures.append(f.remote(i))  # non-blocking call

results = golem.get(results_futures)  # blocking call
```

### Installation:
 - `git clone git@github.com:golemfactory/golem.git && git checkout runf`
 - `pip install git+https://github.com/golemfactory/golem-remote.git` 
 - Set config options in `golem_remote/config.py`

### Running:
 - Run requestor node (for example: ```
   python golemapp.py --log-level INFO --datadir golem_data_r/ 
   --accept-terms --protocol_id 97 --password "k123@" 
   -p localhost:40103 -r localhost:61000```)
 - Run provider node (for example ```
   python golemapp.py --log-level INFO --datadir golem_data_p 
   --accept-terms --protocol_id 97 --password "k123@" 
   -p localhost:40102 -r localhost:61001```)
 - Run redis on `localhost:6379`
 - Run your task on Golem (for example: `python iteration6_golem_remote_package.py`)

### Testing:
 - Run `test_code.py` in the package directory. It will first format the code with `yapf` and then test it with `pytest`, `pylint` and `mypy`. The script should exit with `OK`.

### Troubleshooting:
 - If the task is not run using the example code, ensure that you first run requestor and only then provider. 
 - If the redis tests don't pass, ensure you don't have another redis instance running on `localhost:6379`
 
