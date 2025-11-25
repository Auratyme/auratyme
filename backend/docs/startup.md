# Prerequisites
 - docker with compose plugin (refer to [docker documentation](https://docs.docker.com/))

# Whole backend
You can either run whole backend at once by executing `./startup.sh`.
After running above command, backend will be accessible on `http://localhost` on default port (`80`). To check routes, look at gateway configuration (`./gateway/etc/nginx/nginx.conf`)

# Part of the backend
You can run part of the backend by executing `./<service-name>/startup.sh`.
For example if you want to run only schedules service (with database and gateway), run `./schedules/startup.sh` command. After that schedules service should be accessible on `http://localhost` on default port. To check routes, look at gateway configuration (`./schedules/gateway/etc/nginx/nginx.conf`). Running other services is analogous.

__info__: _if you want to run backend on windows simply change script extension to `.bat`, rest stays the same_

__warning__: _when executing script on linux (`./startup.sh`) you may need to give it execution permissions by running `chmod u+x ./startup.sh` command before running the script._

# Troubleshooting
## Taken ports
Try changing ports in gateway configuration