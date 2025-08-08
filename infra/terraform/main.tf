module "mgmt_net" {
  source         = "./modules/network"
  infra_provider = var.infra_provider
  name           = "mgmt"
  cidr           = "10.10.0.0/24"
  gateway        = "10.10.0.1"
}

module "corp_net" {
  source         = "./modules/network"
  infra_provider = var.infra_provider
  name           = "corp"
  cidr           = "10.20.0.0/24"
  gateway        = "10.20.0.1"
}

module "soc_net" {
  source         = "./modules/network"
  infra_provider = var.infra_provider
  name           = "soc"
  cidr           = "10.30.0.0/24"
  gateway        = "10.30.0.1"
}

module "pfsense" {
  source         = "./modules/vm_linux"
  infra_provider = var.infra_provider
  name           = "pfsense"
  ip             = "10.10.0.2"
  gateway        = module.mgmt_net.gateway
  dns            = ["8.8.8.8"]
  bridge         = module.mgmt_net.name
  iso            = "pfsense.iso"
  tags           = ["router"]
}

module "dc01" {
  source         = "./modules/vm_windows"
  infra_provider = var.infra_provider
  name           = "dc01"
  ip             = "10.20.0.10"
  gateway        = module.corp_net.gateway
  dns            = ["10.20.0.10"]
  bridge         = module.corp_net.name
  iso            = "windows-server.iso"
  tags           = ["ad", "dc"]
}

module "win01" {
  source         = "./modules/vm_windows"
  infra_provider = var.infra_provider
  name           = "win01"
  ip             = "10.20.0.11"
  gateway        = module.corp_net.gateway
  dns            = ["10.20.0.10"]
  bridge         = module.corp_net.name
  iso            = "windows-10.iso"
  tags           = ["workstation"]
}

module "lin01" {
  source         = "./modules/vm_linux"
  infra_provider = var.infra_provider
  name           = "lin01"
  ip             = "10.20.0.12"
  gateway        = module.corp_net.gateway
  dns            = ["10.20.0.10"]
  bridge         = module.corp_net.name
  iso            = "ubuntu.iso"
  tags           = ["server"]
}

module "soc01" {
  source         = "./modules/vm_linux"
  infra_provider = var.infra_provider
  name           = "soc01"
  ip             = "10.30.0.10"
  gateway        = module.soc_net.gateway
  dns            = ["8.8.8.8"]
  bridge         = module.soc_net.name
  iso            = "ubuntu-soc.iso"
  tags           = ["siem"]
}

locals {
  inventory = {
    pfsense = { name = module.pfsense.name, ip = module.pfsense.ip }
    dc01    = { name = module.dc01.name, ip = module.dc01.ip }
    win01   = { name = module.win01.name, ip = module.win01.ip }
    lin01   = { name = module.lin01.name, ip = module.lin01.ip }
    soc01   = { name = module.soc01.name, ip = module.soc01.ip }
  }
}

resource "local_file" "inventory" {
  filename = "${path.module}/inventory.json"
  content  = jsonencode(local.inventory)
}

output "vm_names" {
  value = { for k, v in local.inventory : k => v.name }
}

output "vm_ips" {
  value = { for k, v in local.inventory : k => v.ip }
}

output "inventory_file" {
  value = local_file.inventory.filename
}
