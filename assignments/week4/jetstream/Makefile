# COMP 488 - Week 4
# Jetstream 2 VM Management with OpenStack CLI

VM_NAME = comp488-kbass4-jetstream
VM2_NAME = comp488-kbass4-jetstream-2
IMAGE = Featured-Minimal-Ubuntu22
FLAVOR = m3.tiny
NETWORK = auto_allocated_network
SECURITY_GROUP = remotelogin
KEY_NAME = kbass4-comp488-jetstream

FLOATING_IP = 149.165.172.146

.PHONY: help create start stop status info delete attach-ip detach-ip  \
		create-second start-all stop-all status-all delete-second

help:
	@echo "COMP 488 - Jetstream 2 VM Management"
	@echo "-------------------------------------"
	@echo "make create  - Create the VM"
	@echo "make start   - Start the VM"
	@echo "make stop    - Stop the VM"
	@echo "make status  - List VMs"
	@echo "make info    - Show VM information"
	@echo "make delete  - Delete the VM"
	@echo "make attach-ip - Attach floating IP to the VM"
	@echo "make detach-ip - Detach floating IP from the VM"
	
	@echo ""
	@echo "Multiple VMs:"
	@echo "make create-second - Create the second VM"
	@echo "make start-all     - Start both VMs"
	@echo "make stop-all      - Stop both VMs"
	@echo "make status-all    - List all VMs"
	@echo "make delete-second - Delete the second VM"

create:
	openstack server create \
		--image $(IMAGE) \
		--flavor $(FLAVOR) \
		--network $(NETWORK) \
		--security-group $(SECURITY_GROUP) \
		--key-name $(KEY_NAME) \
		$(VM_NAME)

start:
	openstack server start $(VM_NAME)

stop:
	openstack server stop $(VM_NAME)

status:
	openstack server list

info:
	openstack server show $(VM_NAME)

delete:
	openstack server delete $(VM_NAME)

attach-ip:
	openstack server add floating ip $(VM_NAME) $(FLOATING_IP)

detach-ip:
	openstack server remove floating ip $(VM_NAME) $(FLOATING_IP)


create-second:
	openstack server create \
		--image $(IMAGE) \
		--flavor $(FLAVOR) \
		--network $(NETWORK) \
		--security-group $(SECURITY_GROUP) \
		--key-name $(KEY_NAME) \
		$(VM2_NAME)

start-all:
	openstack server start $(VM_NAME) $(VM2_NAME)

stop-all:
	openstack server stop $(VM_NAME) $(VM2_NAME)

status-all:
	openstack server list

delete-second:
	openstack server delete $(VM2_NAME)