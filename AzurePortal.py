import tkinter as tk
from tkinter import ttk, messagebox
import os

class AzureVMGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure VM PowerShell Generator")

        # Dropdown-Optionen
        self.regions = [
            "northeurope",
            "westeurope",
            "francecentral",
            "italynorth",
            "spaincentral",
            "canadacentral",
            "canadaeast",
            "mexicocentral",
            "global",
            "eastus",
            "westcentralus",
            "centralindia"
        ]

        self.vm_skus = [
            "standard_b2ms",
            "standard_b1s",
            "standard_ds1_v2",
            "standard_d2s_v3"
        ]

        # Eingabefelder
        self.fields = {
            "Resource Group": tk.StringVar(),
            "Region": tk.StringVar(value=self.regions[0]),
            "VM Name": tk.StringVar(),
            "VM Size (SKU)": tk.StringVar(value=self.vm_skus[0]),
            "VNet CIDR": tk.StringVar(value="10.0.0.0/16"),
            "Subnet CIDR": tk.StringVar(value="10.0.0.0/24"),
            "Admin Username": tk.StringVar(),
            "Admin Password": tk.StringVar(),
        }

        self._build_form()

    def _build_form(self):
        row = 0
        for label, var in self.fields.items():
            ttk.Label(self.root, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=5)

            if label == "Region":
                ttk.Combobox(self.root, textvariable=var, values=self.regions, state="readonly").grid(row=row, column=1, padx=5, pady=5)
            elif label == "VM Size (SKU)":
                ttk.Combobox(self.root, textvariable=var, values=self.vm_skus, state="readonly").grid(row=row, column=1, padx=5, pady=5)
            elif "Password" in label:
                ttk.Entry(self.root, textvariable=var, show="*").grid(row=row, column=1, padx=5, pady=5)
            else:
                ttk.Entry(self.root, textvariable=var).grid(row=row, column=1, padx=5, pady=5)

            row += 1

        # Button
        ttk.Button(self.root, text="Generate .ps1", command=self.generate).grid(row=row, column=0, columnspan=2, pady=10)

    def generate(self):
        # Daten auslesen
        data = {k: v.get().strip() for k, v in self.fields.items()}
        if not all(data.values()):
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        # PowerShell Script
        script = f"""
# Azure VM Deployment Script
param()

$rg = "{data['Resource Group']}"
$loc = "{data['Region']}"
$vmName = "{data['VM Name']}"
$vmSize = "{data['VM Size (SKU)']}"
$vnetCidr = "{data['VNet CIDR']}"
$subnetCidr = "{data['Subnet CIDR']}"
$adminUser = "{data['Admin Username']}"
$adminPass = ConvertTo-SecureString "{data['Admin Password']}" -AsPlainText -Force

New-AzResourceGroup -Name $rg -Location $loc

# VNet + Subnet
$vnet = New-AzVirtualNetwork -Name "$vmName-vnet" -ResourceGroupName $rg -Location $loc -AddressPrefix $vnetCidr
Add-AzVirtualNetworkSubnetConfig -Name "$vmName-subnet" -AddressPrefix $subnetCidr -VirtualNetwork $vnet | Set-AzVirtualNetwork

# Public IP
$pip = New-AzPublicIpAddress -Name "$vmName-pip" -ResourceGroupName $rg -Location $loc -AllocationMethod Dynamic -Sku Standard

# NSG mit RDP Regel
$nsg = New-AzNetworkSecurityGroup -ResourceGroupName $rg -Location $loc -Name "$vmName-nsg"
$nsg | Add-AzNetworkSecurityRuleConfig -Name "AllowRDP" -Protocol Tcp -Direction Inbound -Priority 1000 -SourceAddressPrefix * -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange 3389 -Access Allow | Set-AzNetworkSecurityGroup

# NIC
$subnet = Get-AzVirtualNetworkSubnetConfig -Name "$vmName-subnet" -VirtualNetwork $vnet
$nic = New-AzNetworkInterface -Name "$vmName-nic" -ResourceGroupName $rg -Location $loc -Subnet $subnet -PublicIpAddress $pip -NetworkSecurityGroup $nsg

# VM Config
$cred = New-Object System.Management.Automation.PSCredential($adminUser, $adminPass)
$vmConfig = New-AzVMConfig -VMName $vmName -VMSize $vmSize |
    Set-AzVMOperatingSystem -Windows -ComputerName $vmName -Credential $cred -ProvisionVMAgent -EnableAutoUpdate |
    Set-AzVMSourceImage -PublisherName "MicrosoftWindowsServer" -Offer "WindowsServer" -Skus "2025-datacenter-azure-edition" -Version "latest" |
    Add-AzVMNetworkInterface -Id $nic.Id |
    Set-AzVMOSDisk -CreateOption FromImage -StorageAccountType StandardSSD_LRS

New-AzVM -ResourceGroupName $rg -Location $loc -VM $vmConfig
"""

        # Speicherort: Desktop des aktuellen Benutzers
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop, f"{data['VM Name']}_deploy.ps1")
        with open(path, "w", encoding="utf-8") as f:
            f.write(script)

        messagebox.showinfo("Success", f"PowerShell script saved to:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AzureVMGui(root)
    root.mainloop()
