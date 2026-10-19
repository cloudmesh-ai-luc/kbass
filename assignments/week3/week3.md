# Week 3.4 — VM Comparison

## Objective

The objective of this assignment was to compare the experience of starting and using a virtual machine locally with using cloud-based VM infrastructure, particularly Jetstream and Chameleon Cloud.

## 1. Local Virtual Machine vs. Cloud VMs

| Category | Local Virtual Machine | Jetstream | Chameleon Cloud |
| :--- | :--- | :--- | :--- |
| **Setup** | Relatively simple once virtualization software and an OS image are available. | Requires cloud authentication, VM configuration, SSH keys, networking, and a floating IP. | Requires portal configuration, SSH keys, resource selection, a reservation, networking, and VM launch. |
| **Resources** | Limited by the local computer. | Uses remotely allocated cloud resources. | Uses remote computing resources reserved for the experiment. |
| **Access** | Usually accessed directly from the host computer. | Requires remote SSH access. | Requires remote SSH access. |
| **Networking** | Usually simpler for local access. | Required a floating IP and security-group configuration. | Required a floating IP to provide external SSH access. |
| **Resource management** | Uses resources belonging to the local computer. | VM resources must be deleted when no longer needed. | VM, floating IP, and lease must be released after use. |
| **Availability** | Available whenever the local computer is available. | Depends on available cloud resources. | Depends on available resources and reservations. |
| **Flexibility** | Easy to start, stop, and recreate locally. | Provides access to remote cloud infrastructure. | Provides access to remote computing hardware through reservations.

## 2. Experience Using a Local Virtual Machine

Starting a VM locally was relatively straightforward because the resources were directly available on the computer. There was no need to wait for a cloud reservation or configure a floating IP for basic access.

The main limitation was the hardware available on the local computer. A VM shares the host's CPU, memory, storage, and network resources. Giving the VM more resources can therefore affect the performance of the host system.

The local VM environment was convenient for learning Linux commands, testing software, and experimenting with configurations without depending on cloud availability.

## 3. Experience Using Jetstream

Jetstream was the first cloud environment used in the assignment. The basic VM creation process was straightforward, but SSH access required troubleshooting.

Two initial Ubuntu instances were successfully created and received floating IP addresses, but SSH connections timed out. The problem required checking the SSH configuration and trying a different approach.

A dedicated SSH key pair was eventually created through the Jetstream/OpenStack portal and used with the `remotelogin` security group. The final VM successfully accepted an SSH connection.

The successful Jetstream VM used the `m3.tiny` flavor with 1 vCPU and 3 GB of RAM. Compared with a local VM, Jetstream provided a useful introduction to managing remote infrastructure, floating IP addresses, security groups, and SSH authentication.

The Jetstream experience demonstrated that successfully creating a VM does not necessarily mean that remote access will work immediately. Networking, security groups, and SSH keys also have to be configured correctly.

## 4. Experience Using Chameleon Cloud

The Chameleon Cloud experience required more planning than both the local VM and the basic Jetstream deployment.

The Chameleon portal was explored first, the preferred time zone was configured, and an SSH key was prepared. The Ubuntu 24.04 image and available compute options were then inspected before creating the reservation.

TThe interface showed baremetal as the only available flavor for the selected Ubuntu 24.04 image, so baremetal was selected as the available option.

A one-hour host lease was created before the VM was launched. The lease initially entered a `PENDING` state and later became `ACTIVE`. After the VM was launched, a floating IP had to be associated with the instance before SSH access could be established.

Once networking was configured, SSH access worked successfully from WSL. The Chameleon VM provided substantially more CPU and memory than the small Jetstream VM, demonstrating the advantage of having access to larger remote computing resources.

The Chameleon experience also emphasized responsible resource management. After the verification and screenshot were completed, the VM, floating IP, and host lease were released.

## 5. Advantages and Disadvantages

### Local Virtual Machine

**Advantages:**
- Simple and convenient for experimentation.
- Direct access from the host computer.
- No cloud reservation is required.
- Can be used without an internet connection after installation.
- Easy to start, stop, and recreate.

**Disadvantages:**
- Limited by the host computer's hardware.
- VMs can consume significant RAM and storage.
- Performance depends on the local machine.
- External networking can require additional configuration.

### Jetstream

**Advantages:**
- Provides access to remote cloud computing resources.
- Relatively simple VM creation process.
- Supports floating IPs and security groups.
- Provides practical experience with remote SSH access.

**Disadvantages:**
- Requires internet connectivity.
- SSH and networking configuration can require troubleshooting.
- Cloud resources must be cleaned up after use.
- VM availability depends on cloud resources.

### Chameleon Cloud

**Advantages:**
- Provides access to powerful remote computing resources.
- Supports different cloud sites, images, and hardware configurations.
- Provides practical experience with cloud infrastructure.
- Supports remote access through SSH.
- Demonstrates resource reservations, networking, and resource cleanup.

**Disadvantages:**
- Requires more preparation before launching a VM.
- Depends on network connectivity.
- Requires SSH key and network configuration.
- Resources may initially be pending or unavailable.
- Reservations and allocated resources must be managed carefully.

## 6. Overall Experience

The three environments provided progressively different experiences.

The local VM was the easiest to use because the computing resources were immediately available and no external reservation was required.

Jetstream introduced the additional complexity of cloud networking, floating IP addresses, security groups, and remote SSH access. The initial SSH timeouts also demonstrated the need for troubleshooting when working with cloud infrastructure.

Chameleon required the most planning because a host lease had to be created and activated before the VM could be launched. However, it provided access to substantially more computing resources and demonstrated a more structured resource-allocation process.

The progression from a local VM to Jetstream and then Chameleon provided increasing exposure to cloud infrastructure concepts and resource management.

## Conclusion

Starting a VM locally, using Jetstream, and using Chameleon Cloud all provide useful virtualization experiences, but they emphasize different levels of infrastructure management.

A local VM is convenient for development, testing, and learning because it provides immediate access and direct control over the environment. Jetstream introduces remote cloud infrastructure, networking, floating IPs, security groups, and SSH troubleshooting. Chameleon adds resource reservations and provides access to larger remote computing resources.

Overall, the local VM was the simplest to start and manage, Jetstream provided a useful introduction to remote cloud VM deployment, and Chameleon provided the most complete experience with reservations, networking, SSH access, hardware allocation, and resource cleanup.