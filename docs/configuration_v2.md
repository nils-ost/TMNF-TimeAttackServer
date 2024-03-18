
## Create Matchsettings

### Pre stack start

The stack should be down (no containers running of tas)

```
sudo docker compose up -d tmnfd-static
sudo docker exec -ti tmnf-timeattackserver-tmnfd-static-1 /bin/bash
python3 cli
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