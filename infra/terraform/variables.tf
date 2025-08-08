variable "proxmox_api_url" {
  type    = string
  default = "https://proxmox.example.com:8006/api2/json"
}

variable "proxmox_token_id" {
  type    = string
  default = ""
}

variable "proxmox_token_secret" {
  type    = string
  default = ""
}

variable "libvirt_uri" {
  type    = string
  default = "qemu:///system"
}
