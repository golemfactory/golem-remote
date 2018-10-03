# golem-remote

MVP version of library for wrapping Python functions to run on golem.

**Note**: this is only the frontend part of the application. Backend is implemented as *golem app*, in the `runf_task` branch in the [main golem repository](https://github.com/golemfactory/golem).

Work in progress. Working revision: `1aa80d62032ef07d2d285669eb009712b4759096` here and `e7af451a600ca6e608bce7d46831975b3da4349b` in `golemfactory/golem@runf_task`.
Current state: working functions (and closures) execution, rudimentary filesystem support.

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
 - Install the newest version of redis from https://redis.io/download
 - `git clone git@github.com:golemfactory/golem.git && git checkout runf_task`
 - `pip install git+https://github.com/golemfactory/golem-remote.git` 
 - Set config options in `golem_remote/config.py`

### Running:
 - Set up `$DATADIR_R` and `DATADIR_P` env variables to contain locations for golem datadirs.  
 - Run requestor node (for example: ```
   python golemapp.py --log-level INFO --datadir $DATADIR_R 
   --accept-terms --protocol_id 97 --password "k123@" 
   -p localhost:40103 -r localhost:61000```)
 - Run provider node (for example ```
   python golemapp.py --log-level INFO --datadir $DATADIR_P 
   --accept-terms --protocol_id 97 --password "k123@" 
   -p localhost:40102 -r localhost:61001```)
 - If needed, wait some time until requestor node receives tETH from faucet.
 - Run redis on `localhost:6379`
 - Run your task on Golem (for example: `python examples/iteration7_golem_remote_package.py`)

### Testing:
 - Run `test_code.sh` in the package directory. It will first format the code with `yapf` and then test it with `pytest`, `pylint` and `mypy`. The script should exit with `OK`.
 - Set up appropriate paths in `integration_test.sh` (in the package directory) and run it.

### Troubleshooting:
 - If the task does not run using the example code, ensure that you first run requestor and only then provider.
 - If the task still does not run, you can try to turn off concent service (with `--concent disabled` flag passed to `golemapp.py`)
 - If the redis tests don't pass, ensure you don't have another redis instance running on `localhost:6379`
 - If the integration test doesn't pass, it is probably a problem with timeout. Reason is that when you run Golem for the first time, it will run benchmarks and request t(est)ETH from faucet. Getting funds takes unpredictable amount of time (typically X-1X minutes). You should therefore first run Golem separately in $DATADIR_R and $DATADIR_P (defined in `integration_test.sh` and wait for the funds to be transferred to you, and only then run integration test.
