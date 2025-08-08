packer {
  required_plugins {
    qemu = {
      source  = "github.com/hashicorp/qemu"
      version = ">= 1.0.0"
    }
  }
}

variable "iso_url" {
  type    = string
  default = "iso.iso"
}

variable "iso_checksum" {
  type    = string
  default = "none"
}

variable "winrm_username" {
  type    = string
  default = "Administrator"
}

variable "winrm_password" {
  type    = string
  default = "Packer!123"
}

source "qemu" "win10" {
  iso_url      = var.iso_url
  iso_checksum = var.iso_checksum

  communicator   = "winrm"
  winrm_username = var.winrm_username
  winrm_password = var.winrm_password
  winrm_use_ssl  = true
  winrm_insecure = true

  disk_size        = 40960
  format           = "qcow2"
  headless         = true
  shutdown_command = "shutdown /s /t 10"
}

build {
  sources = ["source.qemu.win10"]

  provisioner "powershell" {
    inline = [
      "New-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon' -Name AutoAdminLogon -Value 1 -Force",
      "New-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon' -Name DefaultUsername -Value '${var.winrm_username}' -Force",
      "New-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon' -Name DefaultPassword -Value '${var.winrm_password}' -Force"
    ]
  }

  provisioner "powershell" {
    inline = [
      "$cert = New-SelfSignedCertificate -DnsName 'packer' -CertStoreLocation Cert:\\LocalMachine\\My",
      "New-Item -Path WSMan:\\Localhost\\Listener -Transport HTTPS -Address * -CertificateThumbprint $cert.Thumbprint -Force",
      "Set-Item WSMan:\\localhost\\Service\\AllowUnencrypted -Value false",
      "Set-Item WSMan:\\localhost\\Service\\Auth\\Basic -Value false",
      "Set-Item WSMan:\\localhost\\Service\\Auth\\Certificate -Value true",
      "Set-Item WSMan:\\localhost\\Service\\Auth\\Kerberos -Value true",
      "Set-Item WSMan:\\localhost\\Service\\Auth\\Negotiate -Value true"
    ]
  }

  provisioner "powershell" {
    inline = [
      "$ProgressPreference = 'SilentlyContinue'",
      "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile $env:TEMP\\vcredist.exe",
      "Start-Process $env:TEMP\\vcredist.exe -ArgumentList '/install /quiet /norestart' -Wait",
      "Invoke-WebRequest -Uri 'https://download.sysinternals.com/files/Sysmon.zip' -OutFile $env:TEMP\\Sysmon.zip",
      "Expand-Archive $env:TEMP\\Sysmon.zip -DestinationPath $env:TEMP\\Sysmon -Force",
      "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml' -OutFile $env:TEMP\\sysmonconfig.xml",
      "Start-Process $env:TEMP\\Sysmon\\Sysmon64.exe -ArgumentList '-accepteula -i $env:TEMP\\sysmonconfig.xml' -Wait",
      "Invoke-WebRequest -Uri 'https://artifacts.elastic.co/downloads/beats/winlogbeat/winlogbeat-8.11.3-windows-x86_64.zip' -OutFile $env:TEMP\\winlogbeat.zip",
      "Expand-Archive $env:TEMP\\winlogbeat.zip -DestinationPath 'C:\\Program Files' -Force",
      "Rename-Item 'C:\\Program Files\\winlogbeat-8.11.3-windows-x86_64' 'C:\\Program Files\\Winlogbeat'",
      "New-Service -Name Winlogbeat -BinaryPathName 'C:\\Program Files\\Winlogbeat\\winlogbeat.exe' -DisplayName 'Winlogbeat' -StartupType Disabled"
    ]
  }

  provisioner "powershell" {
    inline = [
      "Start-Process -FilePath 'C:\\Windows\\System32\\Sysprep\\sysprep.exe' -ArgumentList '/oobe /generalize /shutdown /quiet' -Wait"
    ]
  }
}

