terraform {
  required_providers {
    proxmox = { source = "bpg/proxmox" }
    libvirt = { source = "dmacvicar/libvirt" }
  }
}

variable "infra_provider" { type = string }
variable "name" { type = string }
variable "cidr" { type = string }
variable "gateway" { type = string }

resource "proxmox_virtual_environment_network_linux_bridge" "this" {
  count     = var.infra_provider == "proxmox" ? 1 : 0
  name      = var.name
  node_name = "pve"
  address   = var.cidr
  gateway   = var.gateway
}

resource "libvirt_network" "this" {
  count     = var.infra_provider == "libvirt" ? 1 : 0
  name      = var.name
  mode      = "nat"
  domain    = var.name
  addresses = [var.cidr]
}

output "name" {
  value = var.name
}

output "gateway" {
  value = var.gateway
}
