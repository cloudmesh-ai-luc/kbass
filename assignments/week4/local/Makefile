# COMP 488 - Week 4
# Local VM Management with Multipass

VM_NAME = comp488-kbass4
VM2_NAME = comp488-kbass4-2
IMAGE = 22.04
CPUS = 2
MEMORY = 2G
DISK = 10G

.PHONY: help create start stop status info shell delete purge \
	create-second start-all stop-all status-all delete-second

help:
	@echo "COMP 488 - Multipass VM Management"
	@echo "----------------------------------"
	@echo "Single VM:"
	@echo "make create         - Create the primary VM"
	@echo "make start          - Start the primary VM"
	@echo "make stop           - Stop the primary VM"
	@echo "make status         - List all VMs"
	@echo "make info           - Show primary VM information"
	@echo "make shell          - Open a shell in the primary VM"
	@echo "make delete         - Delete the primary VM"
	@echo "make purge          - Permanently purge deleted VMs"
	@echo ""
	@echo "Multiple VMs:"
	@echo "make create-second  - Create the second VM"
	@echo "make start-all      - Start both VMs"
	@echo "make stop-all       - Stop both VMs"
	@echo "make status-all     - List all VMs"
	@echo "make delete-second  - Delete the second VM"

# --------------------------------------------------
# Primary VM
# --------------------------------------------------

create:
	multipass launch $(IMAGE) --name $(VM_NAME) --cpus $(CPUS) --memory $(MEMORY) --disk $(DISK)

start:
	multipass start $(VM_NAME)

stop:
	multipass stop $(VM_NAME)

status:
	multipass list

info:
	multipass info $(VM_NAME)

shell:
	multipass shell $(VM_NAME)

delete:
	multipass delete $(VM_NAME)

purge:
	multipass purge

# --------------------------------------------------
# Multiple VM Management
# --------------------------------------------------

create-second:
	multipass launch $(IMAGE) --name $(VM2_NAME) --cpus $(CPUS) --memory $(MEMORY) --disk $(DISK)

start-all:
	multipass start $(VM_NAME) $(VM2_NAME)

stop-all:
	multipass stop $(VM_NAME) $(VM2_NAME)

status-all:
	multipass list

delete-second:
	multipass delete $(VM2_NAME)
	multipass purge