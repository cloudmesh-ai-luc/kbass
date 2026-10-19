# Week 4 — Chameleon Cloud VM Management

## 1. Objective

The objective of this assignment is to manage cloud machines using a Makefile. The required operations include creating a machine, inspecting its status, starting and stopping it, deleting it, and explaining how multiple machines can be managed.

This report covers Chameleon Cloud using the OpenStack command-line interface (CLI). Unlike the local Multipass environment and the Jetstream 2 virtual machines used in the other Week 4 exercises, the selected Chameleon `baremetal` flavor requires a reservation of physical hosts before instance deployment.

The exercise also documents a provisioning problem encountered during testing, the troubleshooting performed, and the final cleanup.

## 2. Environment and Configuration

| Component | Configuration |
|---|---|
| Cloud platform | Chameleon Cloud, CHI@TACC |
| Local environment | Windows Subsystem for Linux (WSL) |
| Cloud management tool | OpenStack CLI |
| Python environment | `~/.venvs/chameleon` |
| Operating system image | `CC-Ubuntu24.04` |
| Instance flavor | `baremetal` |
| Network | `sharednet1` |
| SSH keypair | `kbass4-comp488-chameleon` |
| Lease name | `comp488-kbass4-chameleon` |
| Instance name | `comp488-kbass4-chameleon-vm` |
| Lease duration | One hour |
| Physical hosts reserved | One |

The Chameleon application credential was stored outside the Git repository:

```bash
~/.config/openstack/chameleon-clouds.yaml
```

The following environment variable selected the Chameleon configuration. `export` makes the setting available to subsequent commands, while `OS_CLIENT_CONFIG_FILE` tells OpenStack which credential file to read:

```bash
export OS_CLIENT_CONFIG_FILE="$HOME/.config/openstack/chameleon-clouds.yaml"
```

The Python virtual environment was activated with `source`, which loads the environment into the current shell so that the installed Chameleon/OpenStack tools are used:

```bash
source ~/.venvs/chameleon/bin/activate
```

The OpenStack CLI successfully accessed Chameleon resources, including images, flavors, networks, keypairs, servers, and reservations.

Credential secrets and SSH private keys were not included in the assignment files.

## 3. Preparing Chameleon Access

### 3.1 Application credential

A Chameleon application credential was created and configured for the OpenStack CLI.

The configuration was stored in a private file outside the repository.

### 3.2 SSH keypair

An existing SSH private key was used to extract its corresponding public key. `ssh-keygen -y` prints the public key from a private key; `-f` selects the private-key file, and `>` writes the output to the `.pub` file:

```bash
ssh-keygen -y \
  -f ~/.ssh/kbass4-comp488-chameleon.pem \
  > ~/.ssh/kbass4-comp488-chameleon.pub
```

The public key was registered with Chameleon. `keypair create` registers a named SSH keypair; `--public-key` uploads the contents of the specified public-key file rather than generating a new private key:

```bash
openstack keypair create \
  --public-key ~/.ssh/kbass4-comp488-chameleon.pub \
  kbass4-comp488-chameleon
```

The keypair was successfully registered.

### 3.3 Resource verification

Before creating the instance, the selected image, flavor, and network were checked through the OpenStack CLI.

The following resources were available:

- Image: `CC-Ubuntu24.04`

- Flavor: `baremetal`

- Network: `sharednet1`

The project initially had no active instances or leases.

## 4. Creating a Bare-Metal Lease

A bare-metal lease was created for one physical host.

The command below requests a one-host reservation. `--reservation` defines the resource type and minimum/maximum host count; `--end-date` sets the lease expiration. The nested `date` command calculates a UTC time one hour ahead (`-u` for UTC, -d '+1 hour': specifies a relative date/time expression, calculating one hour from the current time., and `+%Y-%m-%d %H:%M` for the required date format). The final argument names the lease:

```bash
openstack reservation lease create \
  --reservation "min=1,max=1,resource_type=physical:host" \
  --end-date "$(date -u -d '+1 hour' '+%Y-%m-%d %H:%M')" \
  comp488-kbass4-chameleon
```

The lease was created successfully.

### 4.1 Lease details

| Field | Value |
|---|---|
| Lease name | `comp488-kbass4-chameleon` |
| Lease ID | `d4a7cb8d-92da-47c3-a86b-6b3dc3e297e8` |
| Reservation ID | `f4f5051f-5d80-49ea-b323-0e0c628c6746` |
| Resource type | `physical:host` |
| Minimum hosts | `1` |
| Maximum hosts | `1` |
| Start time | September 19, 2026, 17:18 UTC |
| End time | September 19, 2026, 18:18 UTC |

The lease was inspected using `lease show`; each `-c` selects a field to display (`status`, `reservations`, and `end_date`):

```bash
openstack reservation lease show \
  comp488-kbass4-chameleon \
  -c status -c reservations -c end_date
```

The output confirmed:

```text
Lease status:       ACTIVE
Reservation status: active
Missing resources:  false
Minimum hosts:      1
Maximum hosts:      1
```

**Result:** The physical-host reservation was successfully created and activated.

An active reservation confirms that Chameleon accepted the reservation. It does not, by itself, confirm that an operating system has been successfully deployed to the physical machine.

## 5. First VM Deployment Attempt

After the lease became active, the following command requested the instance. `--image` selects the OS image, `--flavor` the hardware type, `--network` the network, `--key-name` the registered SSH keypair, and `--hint reservation=...` the active physical-host reservation. The final argument is the instance name:

```bash
openstack server create \
  --image CC-Ubuntu24.04 \
  --flavor baremetal \
  --network sharednet1 \
  --key-name kbass4-comp488-chameleon \
  --hint reservation=f4f5051f-5d80-49ea-b323-0e0c628c6746 \
  comp488-kbass4-chameleon-vm
```

### 5.1 Initial result

The creation request was accepted.

| Field | Value |
|---|---|
| Instance ID | `bfc8b3bc-5197-4411-a2e7-bdf33ff10160` |
| Created | September 19, 2026, 17:19:47 UTC |
| Initial status | `BUILD` |
| Image | `CC-Ubuntu24.04` |
| Flavor | `baremetal` |
| Network requested | `sharednet1` |

The instance was monitored with `server show`. The `-c` options limit the output to the provisioning state, assigned addresses, and any reported fault:

```bash
openstack server show \
  comp488-kbass4-chameleon-vm \
  -c status -c addresses -c fault
```

A repeating status check was also used. `watch -n 30` reruns the quoted command every 30 seconds so changes from `BUILD` to `ACTIVE` or `ERROR` can be observed:

```bash
watch -n 30 \
  'openstack server show comp488-kbass4-chameleon-vm -c status -c addresses -c fault'
```

The instance remained in `BUILD` for several minutes.

It subsequently entered:

```text
status:    ERROR
addresses:
```

No IP address was assigned.

**Result:** The VM creation request was accepted, but bare-metal provisioning did not complete successfully.

## 6. Problem Encountered and Troubleshooting

### 6.1 Problem description

The primary problem was that Chameleon accepted the VM creation request but did not successfully provision the instance.

The lease was active and reported no missing resources. Nevertheless, the instance transitioned from `BUILD` to `ERROR` without receiving a network address.

The available fault information did not identify the underlying cause.

The following troubleshooting steps were performed.

### 6.2 Step 1 — Inspecting the VM status and fault

The instance was inspected with `server show`. In addition to status and fault, `OS-EXT-STS:task_state` checks for an in-progress task and `OS-EXT-SRV-ATTR:host` requests the assigned compute host:

```bash
openstack server show \
  comp488-kbass4-chameleon-vm \
  -c status \
  -c fault \
  -c OS-EXT-STS:task_state \
  -c OS-EXT-SRV-ATTR:host
```

The output showed:

```text
OS-EXT-SRV-ATTR:host   None
OS-EXT-STS:task_state  None
status                 ERROR
```

No useful fault message was returned.

**Finding:** The instance was in an error state, but the available server details did not explain why provisioning failed.

### 6.3 Step 2 — Listing the server events

The server event history was requested using `server event list`, which displays recorded actions for the named instance:

```bash
openstack server event list \
  comp488-kbass4-chameleon-vm
```

Three actions were listed:

| Action | Start time (UTC) |
|---|---|
| `create` | 2026-09-19 17:19:47 |
| `start` | 2026-09-19 17:21:21 |
| `stop` | 2026-09-19 17:26:08 |

The event history showed that the create request was followed by start and stop actions.

The event list alone did not explain the provisioning failure.

### 6.4 Step 3 — Inspecting the create event

The create event was inspected with `server event show`. The instance name identifies the server and the `req-...` ID selects the specific action:

```bash
openstack server event show \
  comp488-kbass4-chameleon-vm \
  req-6f3d27a8-42eb-4162-8266-3467c427d2d9
```

The event reported:

```text
action: create
event:  compute__do_build_and_run_instance
result: Success
message: None
```

Its recorded finish time was:

```text
2026-09-19T17:26:35 UTC
```

**Finding:** The Nova create event reported success, but the instance itself remained in `ERROR`. The event contained no useful traceback or diagnostic message explaining the failed provisioning.

A successful action record was therefore not treated as proof that the physical machine had booted successfully.

### 6.5 Step 4 — Inspecting the stop event

The stop event was inspected using the same `server event show` syntax with the stop action’s request ID:

```bash
openstack server event show \
  comp488-kbass4-chameleon-vm \
  req-34f7e5e2-8945-4499-9304-1b08162c215b
```

The event reported:

```text
action: stop
event:  compute_power_update
result: Success
message: None
```

The event's project and user IDs differed from those recorded for the original create request.

This difference was noted during troubleshooting, but the available information did not establish who initiated the action or why it occurred.

**Finding:** The stop event did not reveal the root cause.

### 6.6 Step 5 — Inspecting the start event

The start event was inspected using the same command with the start action’s request ID:

```bash
openstack server event show \
  comp488-kbass4-chameleon-vm \
  req-c39b7132-d35b-4290-a08d-617c03fbc498
```

The event reported:

```text
action: start
event:  compute_power_update
result: Success
message: None
```

No useful error details or traceback were provided.

**Finding:** The create, start, and stop events all reported success, but none explained why the instance entered `ERROR`.

### 6.7 Step 6 — Checking bare-metal node visibility

The following command requested the bare-metal node inventory. `--long` asks for additional columns when the project is permitted to see them:

```bash
openstack baremetal node list --long
```

The command returned no visible nodes and no explicit error.

This did not establish that the reserved host was missing or broken. The project might not have permission to list the underlying physical nodes.

**Finding:** The node listing did not provide enough information to diagnose the failure.

### 6.8 Step 7 — Requesting the console log

The console log was requested using `console log show`. `--lines 100` limits the request to the most recent 100 console-output lines:

```bash
openstack console log show \
  --lines 100 \
  comp488-kbass4-chameleon-vm
```

The request failed with HTTP 409:

```text
ConflictException: 409
Instance ... is not ready
```

**Finding:** No console output was available to inspect the operating-system boot process.

### 6.9 Step 8 — Rechecking the lease

The lease and VM were inspected again. The `-c` options select only the fields needed to compare reservation health with instance state and the last update time:

```bash
openstack reservation lease show \
  comp488-kbass4-chameleon \
  -c status -c end_date -c reservations
openstack server show \
  comp488-kbass4-chameleon-vm \
  -c status -c fault -c updated
```

The lease still reported:

```text
status:            ACTIVE
reservation status: active
missing_resources: false
```

The VM still reported:

```text
status:  ERROR
updated: 2026-09-19T17:26:35Z
```

**Finding:** The lease had not expired before the first provisioning failure. The instance remained in an error state despite the active reservation.

### 6.10 Step 9 — Deleting the failed instance

The failed instance was deleted using `server delete`; `--wait` keeps the CLI command running until deletion completes:

```bash
openstack server delete --wait \
  comp488-kbass4-chameleon-vm
```

The instance list was then checked using `server list`, which shows remaining instances in the project:

```bash
openstack server list
```

The list was empty.

**Result:** The first failed instance was successfully removed while preserving the existing lease for one retry.

## 7. Second VM Deployment Attempt

A second deployment was attempted using the same:

- Active lease and reservation ID

- Ubuntu image

- Bare-metal flavor

- Network

- SSH keypair

- Instance name

The same creation command was submitted with the original image, flavor, network, keypair, and reservation ID to retry deployment without changing the configuration:

```bash
openstack server create \
  --image CC-Ubuntu24.04 \
  --flavor baremetal \
  --network sharednet1 \
  --key-name kbass4-comp488-chameleon \
  --hint reservation=f4f5051f-5d80-49ea-b323-0e0c628c6746 \
  comp488-kbass4-chameleon-vm
```

The second request was accepted.

| Field | Value |
|---|---|
| Instance ID | `b455bb47-1b0b-49db-87ac-eac5f1096a8f` |
| Created | September 19, 2026, 17:32:04 UTC |
| Initial status | `BUILD` |
| Reservation | Same active one-host reservation |

The second instance was monitored with `watch -n 30`, repeating the status, address, and fault query every 30 seconds:

```bash
watch -n 30 \
  'openstack server show comp488-kbass4-chameleon-vm -c status -c addresses -c fault'
```

It subsequently entered:

```text
status:    ERROR
addresses:
```

The second instance also failed before receiving an IP address.

Because the repeated deployment produced the same outcome, further identical attempts were stopped.

**Result:** Two VM creation requests were accepted, but neither instance reached `ACTIVE`.

## 8. OpenStack CLI Warning

During the Chameleon session, many OpenStack commands printed:

```text
Could not load 'reservation_host_unset':
module 'blazarclient.v1.shell_commands.hosts'
has no attribute 'UnsetAttributeHost'
```

This warning appeared during both successful and unsuccessful operations.

For example, it appeared when:

- Listing resources

- Creating the lease

- Creating the VM

- Deleting the VM

- Deleting the lease

The warning did not prevent successful lease creation or deletion.

**Conclusion:** The available evidence does not establish that this CLI warning caused the bare-metal provisioning failures.

## 9. Makefile Implementation

The Chameleon Makefile provides a command interface for authentication checks, lease management, VM lifecycle operations, and cleanup.

### 9.1 Authentication and lease targets

| Target | Purpose |
|---|---|
| `make help` | Display available commands |
| `make check-auth` | Check OpenStack authentication |
| `make lease` | Create a physical-host lease |
| `make lease-info` | Display lease information and reservation ID |
| `make lease-list` | List existing leases |

The default lease requests one physical host: `make lease` runs the Makefile recipe with its default `HOSTS=1` and `LEASE_HOURS=1` settings:

```bash
make lease
```

The host count is configurable: `HOSTS=2` overrides the Makefile’s default and requests two physical hosts instead of one:

```bash
make lease HOSTS=2
```

The lease duration is also configurable: `LEASE_HOURS=2` overrides the Makefile’s default end-time calculation to request approximately two hours:

```bash
make lease LEASE_HOURS=2
```

### 9.2 VM lifecycle targets

| Target | Purpose |
|---|---|
| `make create RESERVATION_ID=ID` | Request the first VM |
| `make status` | Display the first VM's status |
| `make info` | Display detailed instance information |
| `make start` | Request VM start |
| `make stop` | Request VM stop |
| `make delete` | Delete the first VM |

The reservation ID must be supplied to the creation target because Chameleon generates a new reservation ID for each lease. `RESERVATION_ID=...` is a Makefile variable override, not an OpenStack CLI option.

Example (replace `RESERVATION_ID_HERE` with the ID printed by `make lease-info`):

```bash
make lease
make lease-info
make create RESERVATION_ID=RESERVATION_ID_HERE
```

### 9.3 Cleanup target

The Makefile includes `make cleanup`, which runs the cleanup recipe defined in the Makefile:

```bash
make cleanup
```

This target is designed to delete the configured instances before deleting the lease.

Deleting instances before releasing the physical-host reservation is the intended cleanup sequence.

## 10. Managing Multiple Bare-Metal VMs

The Makefile includes a second instance name:

```text
comp488-kbass4-chameleon-vm-2
```

It also provides the following targets:

| Target | Purpose |
|---|---|
| `make create-second RESERVATION_ID=ID` | Request a second VM |
| `make status-all` | List all instances |
| `make start-all` | Request start for both configured instances |
| `make stop-all` | Request stop for both configured instances |
| `make delete-second` | Delete the second VM |
| `make delete-all` | Delete both configured instances |

### 10.1 Why multiple VMs require additional resources

The selected `baremetal` flavor uses physical hosts.

The one-host lease created during testing was therefore not sufficient for two simultaneous bare-metal instances.

A two-instance deployment would first require a lease requesting two physical hosts. `HOSTS=2` changes the number of hosts reserved for this invocation:

```bash
make lease HOSTS=2
```

After the lease becomes active, `make lease-info` displays the lease details, including the generated reservation ID:

```bash
make lease-info
```

The two instances can be created using the same reservation ID. The RESERVATION_ID variable passes the reservation identifier to each Makefile target. The actual ID, obtained from make lease-info, replaces the placeholder in the following commands:

```bash
make create RESERVATION_ID=<reservation-id>
make create-second RESERVATION_ID=<reservation-id>
```

The Makefile uses the same reservation ID for both requests.

**Testing limitation:** A two-host lease and simultaneous deployment of two Chameleon bare-metal instances were not tested. The first and second attempts described in this report were sequential attempts to deploy a single instance using the same one-host reservation.

## 11. Makefile Verification

The following Makefile command was run successfully. `make help` displays the target descriptions defined in the Makefile:

```bash
make help
```

The command displayed the configured targets.

After the cloud resources were deleted, the following commands were run. `make lease-list` lists leases and `make status-all` lists servers:

```bash
make lease-list
make status-all
```

These Makefile targets invoke the corresponding OpenStack CLI commands:

```bash
openstack reservation lease list
openstack server list
```

Both commands completed successfully and returned empty lists.

These results confirmed that the Makefile could invoke the configured read-only OpenStack commands and that no instances or leases remained after cleanup.

The VM creation commands were exercised directly through the OpenStack CLI rather than through `make create`.

Because both deployment attempts ended in `ERROR`, successful Chameleon VM start/stop behavior and SSH connectivity were not verified.

## 12. Final Cleanup

After the second failed provisioning attempt, the instance was deleted:

```bash
openstack server delete --wait \
  comp488-kbass4-chameleon-vm
```

The instance list was checked with `server list` to confirm the failed instance was gone:

```bash
openstack server list
```

No instances remained.

The lease was then released with `reservation lease delete`, followed by the lease name:

```bash
openstack reservation lease delete \
  comp488-kbass4-chameleon
```

OpenStack confirmed:

```text
Deleted lease: comp488-kbass4-chameleon
```

The lease list was checked with `reservation lease list` to confirm no reservations remained:

```bash
openstack reservation lease list
```

No leases remained.

The Makefile commands `make lease-list` and `make status-all` were also run after cleanup and returned empty lists.

**Final resource state:** No Chameleon instances or leases remained in the project.

## 13. Results Summary

| Operation | Result |
|---|---|
| Chameleon CLI authentication | Successful |
| SSH public key registration | Successful |
| Image, flavor, and network verification | Successful |
| One-host bare-metal lease creation | Successful |
| Lease activation | Successful |
| First VM creation request | Accepted |
| First VM provisioning | Failed — `ERROR` |
| Server event inspection | Completed; no root cause identified |
| Bare-metal node listing | Completed; no visible nodes |
| Console-log request | Failed — HTTP 409, instance not ready |
| First failed VM deletion | Successful |
| Second VM creation request | Accepted |
| Second VM provisioning | Failed — `ERROR` |
| Second failed VM deletion | Successful |
| Lease deletion | Successful |
| `make help` | Successful |
| `make lease-list` | Successful |
| `make status-all` | Successful |
| Floating-IP assignment | Not reached |
| SSH connection to deployed VM | Not reached |
| Successful VM start/stop testing | Not verified |
| Simultaneous two-VM deployment | Not tested |

## 14. Conclusion

The Chameleon exercise demonstrated the additional resource-management steps required for bare-metal cloud instances.

Authentication, SSH keypair registration, physical-host reservation, lease activation, VM creation requests, instance deletion, and lease cleanup were completed successfully.

However, both VM provisioning attempts ended in `ERROR` before an IP address was assigned. The available server details, Nova events, node listing, and console-log request did not establish the root cause.

The Chameleon Makefile provides a reusable structure for lease creation, instance management, multiple-machine operations, and cleanup. Its help and read-only listing targets were verified. Successful VM lifecycle operations and simultaneous multiple-VM deployment remain unverified because neither instance became operational.

All failed instances and the lease were removed at the end of testing, leaving the Chameleon project without active instances or reservations.
