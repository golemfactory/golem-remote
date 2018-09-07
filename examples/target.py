import golem_remote as golem

###############
# rpc details #
###############
host = "127.0.0.1" 
port = "61000"
user = "golem_remote"
passwd = "12345"


# although I will use golemcli at the beginning
# because doing anything with WAMP is so painful
# host = "127.0.0.1" 
# port = "61000"
# golem_dir = "/home/jacek/golem_data/golem4_r"
# golemcli = "/home/jacek/golem_orig/golemcli.py"


################
# task details #
################

# list of files that have to be copied to providers
# we will have to do some magic with relative and absolute paths
# for example - to copy /etc/..., but not to /etc/..., 
# but at the same time allow to read from /etc/...
input_files: Optional[List[Path]] = [Path("somefile")]

# timeout in seconds, if empty it is INFTY
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
    host=host,
    port=port,
    user=user,
    passwd=passwd,
    timeout=timeout,
    input_files=input_files,
    needed_packages=needed_packages
)

# golem.init()  # this should be possible as well


#######################
# function definition #
#######################

# per-function timeout; if not set, defaults to golem.DEFAULT_SUBTASK_TIMEOUT
func_timeout: Optional[int] = 30 

# optional list of files that should be saved during computation
# adn returned later
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
# res: golem.ObjectID = func(func_timeout=some_other_timeout)  # not sure if that would not be better, have to talk with them

# ObjectIDs work as in ray
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


#######################################################################
# Some more advanced stuff - but probably possible with current golem #
#######################################################################

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

assert os.path.isfile("infile")

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

assert os.path.isfile("outfile")

with open("outfile", "r") as f:
    contents = f.read()

assert contents == poem
