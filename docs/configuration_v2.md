## Configure Settings

In the root directory execute:

```
sudo docker compose -f setup-stack.yml up -d
```

Wait for the Stack to be up... the execute:

```
sudo docker exec -ti tmnf-timeattackserver-backend-1 python3 cli
```

After you are done, just:

```
sudo docker compose -f setup-stack.yml down
```

And start the normal stack as usual:

```
sudo docker compose up -d
```

## Create Matchsettings

### Pre stack start

For example during running the setup-stack (this is also required if you just cleard the database and want to edit Dedicated configs, without this step you will not be able to select a matchsetting) 

```
sudo docker compose up -d tmnfd-static
sudo docker exec -ti tmnf-timeattackserver-tmnfd-static-1 python3 cli
```

After you exited the container do:
```
sudo docker compose down
```

### Post stack start

The stack is allready running (`sudo docker compose up -d` executed)

```
sudo docker exec -ti tmnf-timeattackserver-tmnfd-static-1 /bin/bash
python3 cli
```

## Provide Challenges

### Pre stack start

The stack should be down (no containers running of tas)

```
sudo docker compose up -d tmnfd-static
sudo docker cp path_to_challenge.gbx tmnf-timeattackserver-tmnfd-static-1:/tracks/Challenges/
```

After you finished do:
```
sudo docker compose down
```

### Post stack start

The stack is allready running (`sudo docker compose up -d` executed)

```
sudo docker cp path_to_challenge.gbx tmnf-timeattackserver-tmnfd-static-1:/tracks/Challenges/
```