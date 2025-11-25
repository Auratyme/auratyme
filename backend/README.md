# What is this repository?
This repository holds backend for auratyme project (ai, apis, etc)

# How to run

## Prerequisites
 - docker with compose plugin (refer to [docker documentation](https://docs.docker.com/))

## Startup
You can either run whole backend at once (by executing `./startup.sh`) or one part (for example by executing `./schedules/startup.sh`)

__warning__: _when executing script on linux (`./startup.sh`) you may need to give it execution permissions by running `chmod u+x ./startup.sh` command before running the script._

__info__: _if you want to run backend on windows simply change script extension to `.bat`, rest stays the same_

__info__: _more information about startup is [here](./docs/startup.md)_

# Documentation
General documentation is (or will be) in the `./docs` folder, while documentation for specific services will be in `./service-name/docs` folder (for example `./schedules/docs`).
