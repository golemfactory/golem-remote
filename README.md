# golem_remote

MVP version of library for wrapping Python functions to run on golem.  

Work in progress. Working revision: `d364ef748aaa94271559f62d274376f559191f74`.  

Install:
 - `git clone git@github.com:golemfactory/golem.git && git checkout runf`
 - `pip install git+https://github.com/inexxt/golem_remote.git` 

Run:
 - Run requestor as ```python golemapp.py --log-level INFO --datadir golem_data_r/ --accept-terms --protocol_id 97 --password "k123@" -p localhost:40103 -r localhost:61000```
 - Run provider as ```python golemapp.py --log-level INFO --datadir golem_data_p --accept-terms --protocol_id 97 --password "k123@" -p localhost:40102 -r localhost:61001```
 - Run redis on `localhost:6379`
 - Run task as `python iteration6_golem_remote_package.py`
 - Watch the screen as `Assert: True` appears :)

