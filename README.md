# golem-remote

MVP version of library for wrapping Python functions to run on golem.  

Work in progress. Working revision: `d364ef748aaa94271559f62d274376f559191f74` here and `379e140c726c59bf1b80e5e61304ec5f27be7bc5` in `golemfactory/golem@runf`.  

### Description
The goal of this library is to provide wrappers analogous to these in [Ray](https://github.com/ray-project/ray). This is what is should look like from the user's perspective:
```python
import golem_remote as golem


################
# task details #
################

input_files: Optional[List[Path]] = [Path("somefile")]

timeout: Optional[int] = 300

# user can either call special golem.finish() function 
# or allow auto closing of files after this many
max_subtasks: Optional[int] = 10

# these should be detected from environment
# but if not detected properly, this option allows to overwrite it  
needed_packages: Optional[List[str]] = ["tqdm=4.25.0"]

##############
# golem init #
##############

golem.init(
    timeout=timeout,
    input_files=input_files,
    needed_packages=needed_packages
)


#######################
# function definition #
#######################

func_timeout: Optional[int] = 30 

# optional list of files that should be saved during computation
# and returned later
output_files: Optional[List[Path]] = []

@golem.remote(func_timeout=func_timeout)
def func(arg1: int, arg2: int, kwarg1: str="abc", kwarg2: str="def") -> Tuple[int, str]:
    time.sleep(1)  # expensive call    
    return (arg1 + arg2, kwarg1 + kwarg2)

##################
# function calls #
##################

# all options are possible to overwrite during function call
res_id1: golem.ObjectID = func.remote(1, 2, kwarg1="abcd", func_timeout=some_other_timeout)  # consistent with ray
res_id2: golem.ObjectID = func.remote(3, 4, kwarg1="xyz")


res1 = golem.get(res_id1)
assert res1 == (1 + 2, "abcd" + "def")


@golem.remote
def func2(arg: Tuple[int, str]) -> Tuple[int, str]:
    time.sleep(1)  # expensive call
    return (arg[0] * 2, arg[1] * 2)


# but we can also do that
res_id3 = func2.remote(res_id2)
res3 = golem.get(res_id3)

assert res3 = (3 * 4 * 2, ("xyz" + "def") * 2)

##############
# filesystem #
##############

poem = """
I saw the best minds of my generation
destroyed by madness,
starving hysterical naked
"""

with open("infile", "w") as f:
    f.write(poem)


input_file = Path("infile")  # it is possible to include dirs
output_file = Path("outfile")  # it is possible to include dirs

# custom input and output files for functions
@golem.remote(input_files=[input_file], output_files=[output_file])
def func3() -> None:
    # some files manipulation
    with open("infile", "r") as f:
        contents = f.read()
    with open("outfile", "w") as f:
        f.write(contents)
    return

with open("outfile", "r") as f:
    contents = f.read()

assert contents == poem
```


### Installation:
 - `git clone git@github.com:golemfactory/golem.git && git checkout runf`
 - `pip install git+https://github.com/inexxt/golem_remote.git` 
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
 - If the task is not run usint the example code above, ensure that you first run requestor and only then provider. 
 - If the redis tests don't pass, ensure you don't have another redis instance running on `localhost:6379`
 