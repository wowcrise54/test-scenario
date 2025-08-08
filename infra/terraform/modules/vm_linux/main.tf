terraform {
  required_providers {
    proxmox = { source = "bpg/proxmox" }
    libvirt = { source = "dmacvicar/libvirt" }
  }
}

variable "infra_provider" { type = string }
variable "name" { type = string }
variable "ip" { type = string }
variable "gateway" { type = string }
variable "dns" { type = list(string) }
variable "bridge" { type = string }
variable "iso" { type = string }
variable "tags" { type = list(string) }

resource "proxmox_virtual_environment_vm" "vm" {
  count     = var.infra_provider == "proxmox" ? 1 : 0
  name      = var.name
  node_name = "pve"
  tags      = var.tags

  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    size         = 20
  }

  network_device {
    bridge = var.bridge
  }

  initialization {
    datastore_id = "local-lvm"
    ip_config {
      ipv4 {
        address = "${var.ip}/24"
        gateway = var.gateway
      }
    }
    dns {
      servers = var.dns
    }
    user_account {
      username = "ubuntu"
      password = "password"
    }
  }
}

resource "libvirt_volume" "os" {
  count  = var.infra_provider == "libvirt" ? 1 : 0
  name   = "${var.name}.qcow2"
  source = var.iso
}

resource "libvirt_cloudinit_disk" "init" {
  count          = var.infra_provider == "libvirt" ? 1 : 0
  name           = "${var.name}-cloudinit.iso"
  user_data      = <<EOT
#cloud-config
hostname: ${var.name}
ssh_pwauth: true
chpasswd:
  list: |
    ubuntu:password
  expire: False
EOT
  network_config = <<EOT
version: 2
ethernets:
  eth0:
    addresses: [${var.ip}/24]
    gateway4: ${var.gateway}
    nameservers:
      addresses: ${jsonencode(var.dns)}
EOT
}

resource "libvirt_domain" "vm" {
  count  = var.infra_provider == "libvirt" ? 1 : 0
  name   = var.name
  memory = 2048
  vcpu   = 2
  disk {
    volume_id = libvirt_volume.os[count.index].id
  }
  network_interface {
    network_name = var.bridge
  }
  cloudinit = libvirt_cloudinit_disk.init[count.index].id
}

output "name" {
  value = var.name
}

output "ip" {
  value = var.ip
}
