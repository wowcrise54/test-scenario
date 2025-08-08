terraform {
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = ">=0.40.0"
    }
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = ">=0.7.0"
    }
    local = {
      source  = "hashicorp/local"
      version = ">=2.4.0"
    }
  }
}

variable "infra_provider" {
  description = "Infrastructure provider: proxmox or libvirt"
  type        = string
  default     = "proxmox"
}

# Proxmox provider configuration
provider "proxmox" {
  endpoint  = var.proxmox_api_url
  api_token = "${var.proxmox_token_id}=${var.proxmox_token_secret}"
  insecure  = true
}

# Libvirt provider configuration
provider "libvirt" {
  uri = var.libvirt_uri
}
