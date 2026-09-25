# COMP 488 — Week 4: Chameleon Cloud bare-metal VM management
#
# Run from WSL with:
#   source ~/.venvs/chameleon/bin/activate
#   export OS_CLIENT_CONFIG_FILE="$HOME/.config/openstack/chameleon-clouds.yaml"
#
# A Chameleon bare-metal VM requires a physical-host reservation.
# Create the lease first, then obtain its reservation ID:
#   make lease-info
#
# Example:
#   make lease
#   make lease-info
#   make create RESERVATION_ID=<reservation-id>
#
# To reserve enough hosts for two bare-metal VMs:
#   make lease HOSTS=2

SHELL := /bin/bash

OPENSTACK ?= openstack

LEASE_NAME ?= comp488-kbass4-chameleon
VM_NAME ?= comp488-kbass4-chameleon-vm
SECOND_VM_NAME ?= comp488-kbass4-chameleon-vm-2

IMAGE ?= CC-Ubuntu24.04
FLAVOR ?= baremetal
NETWORK ?= sharednet1
KEY_NAME ?= kbass4-comp488-chameleon

HOSTS ?= 1
LEASE_HOURS ?= 1
RESERVATION_ID ?=

.PHONY: help check-auth lease lease-info lease-list \
        create create-second start stop status info \
        start-all stop-all status-all \
        delete delete-second delete-all \
        cleanup

help:
	@echo "Chameleon Cloud — COMP 488 Week 4"
	@echo ""
	@echo "Authentication:"
	@echo "  make check-auth"
	@echo ""
	@echo "Lease management:"
	@echo "  make lease                     Reserve one physical host"
	@echo "  make lease HOSTS=2             Reserve two physical hosts"
	@echo "  make lease-info                Show lease and reservation ID"
	@echo "  make lease-list                List leases"
	@echo ""
	@echo "VM management:"
	@echo "  make create RESERVATION_ID=ID"
	@echo "  make create-second RESERVATION_ID=ID"
	@echo "  make status"
	@echo "  make info"
	@echo "  make start"
	@echo "  make stop"
	@echo "  make delete"
	@echo "  make delete-second"
	@echo ""
	@echo "Multiple VMs:"
	@echo "  make status-all"
	@echo "  make start-all"
	@echo "  make stop-all"
	@echo "  make delete-all"
	@echo ""
	@echo "Cleanup:"
	@echo "  make cleanup                   Delete VMs, then lease"

check-auth:
	$(OPENSTACK) token issue -c expires

lease:
	$(OPENSTACK) reservation lease create \
		--reservation "min=$(HOSTS),max=$(HOSTS),resource_type=physical:host" \
		--end-date "$$(date -u -d '+$(LEASE_HOURS) hour' '+%Y-%m-%d %H:%M')" \
		$(LEASE_NAME)

lease-info:
	$(OPENSTACK) reservation lease show $(LEASE_NAME) \
		-c name -c status -c reservations -c end_date

lease-list:
	$(OPENSTACK) reservation lease list

create:
	@test -n "$(RESERVATION_ID)" || \
		(echo "ERROR: Supply RESERVATION_ID from make lease-info"; exit 1)
	$(OPENSTACK) server create \
		--image $(IMAGE) \
		--flavor $(FLAVOR) \
		--network $(NETWORK) \
		--key-name $(KEY_NAME) \
		--hint reservation=$(RESERVATION_ID) \
		$(VM_NAME)

create-second:
	@test -n "$(RESERVATION_ID)" || \
		(echo "ERROR: Supply RESERVATION_ID from make lease-info"; exit 1)
	@echo "Requires a lease reserving at least two physical hosts."
	$(OPENSTACK) server create \
		--image $(IMAGE) \
		--flavor $(FLAVOR) \
		--network $(NETWORK) \
		--key-name $(KEY_NAME) \
		--hint reservation=$(RESERVATION_ID) \
		$(SECOND_VM_NAME)

status:
	$(OPENSTACK) server show $(VM_NAME) \
		-c name -c status -c addresses -c fault

info:
	$(OPENSTACK) server show $(VM_NAME)

start:
	$(OPENSTACK) server start $(VM_NAME)

stop:
	$(OPENSTACK) server stop $(VM_NAME)

status-all:
	$(OPENSTACK) server list

start-all:
	$(OPENSTACK) server start $(VM_NAME)
	$(OPENSTACK) server start $(SECOND_VM_NAME)

stop-all:
	$(OPENSTACK) server stop $(VM_NAME)
	$(OPENSTACK) server stop $(SECOND_VM_NAME)

delete:
	$(OPENSTACK) server delete --wait $(VM_NAME)

delete-second:
	$(OPENSTACK) server delete --wait $(SECOND_VM_NAME)

delete-all:
	@for vm in $(VM_NAME) $(SECOND_VM_NAME); do \
		if $(OPENSTACK) server show "$$vm" >/dev/null 2>&1; then \
			$(OPENSTACK) server delete --wait "$$vm" || exit 1; \
		else \
			echo "$$vm does not exist; skipping."; \
		fi; \
	done

cleanup: delete-all
	@if $(OPENSTACK) reservation lease show $(LEASE_NAME) >/dev/null 2>&1; then \
		$(OPENSTACK) reservation lease delete $(LEASE_NAME); \
	else \
		echo "Lease $(LEASE_NAME) does not exist; skipping."; \
	fi