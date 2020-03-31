
## Required Privileges

In order to use Terraform provider as non priviledged user, some Roles within vCenter must be assigned the following privileges:

- Datastore (Role: ocp-terraform-datastore)
  - Allocate space
  - Low level file operations
- Folder (Role: ocp-terraform-vm)
  - Create folder
  - Delete folder
- StorageProfile (Role: ocp-terraform-vcenter]
  - View
- Network (Role: ocp-terraform-network)
  - Assign network
- Resource (Role: ocp-terraform-resource)
  - Assign vApp to resource pool
  - Assign virtual machine to resource pool
  - Create resource pool
  - Remove resource pool
- vApp (Role: ocp-terraform-vm)
  - Clone
  - View OVF environment
  - vApp application configuration
  - vApp instance configuration
  - vApp resource configuration
- Virtual machine (Role: ocp-terraform-vm)
  - Change Configuration (all)
  - Edit Inventory (all)
  - Guest operations (all)
  - Interaction (all)
  - Provisioning (all)

And these roles have to be given permission on the following entities:
Role | Entity | Propagate to Children | Description
---- | ------ | --------- | -----------
ocp-terraform-vm | VM Folder | Yes | The folder where VMs will be alocated
ocp-terraform-vm | Virtual Machine | No | The OVA template that will be cloned
ocp-terraform-network | VM Network | No | The VM Network the VMs will attach  to
ocp-terraform-datastore | Datastore | No | The Datastore where the VMs disk0 will reside
ocp-terraform-resource | Resource Pool |  No | The Resource Pool the VMs will we added to
ocp-terraform-vcenter | vCenter | No | Profile-driven storage view

Example:
```
govc permissions.set -principal ocp-terraform@vsphere.local -role ocp-terraform-vm -propagate=true "/Datacenter/vm/openshift/ocp"
govc permissions.set -principal ocp-terraform@vsphere.local -role ocp-terraform-vm -propagate=false "/Datacenter/vm/templates/rhcos"
govc permissions.set -principal ocp-terraform@vsphere.local -role ocp-terraform-network -propagate=false "/Datacenter/network/VM Network"
govc permissions.set -principal ocp-terrafom@vsphere.local -role ocp-terraform-datastore -propagate=false "/Datacenter/datastore/Datastore"
govc permissions.set -principal ocp-terraform@vsphere.local -role ocp-terraform-resource -propagate=false "/Datacenter/host/Cluster/Resources/openshift"
govc permissions.set -principal ocp-terraform@vsphere.local -role ocp-terraform-vcenter -propagate=false "/"
```

The config-gen.py script generates the commands needed to create these roles and assign them to the corresponding vCenter objects.

These settings have been tested with:
- [vSphere 6.7](https://pubs.vmware.com/vsphere-60/index.jsp?topic=%2Fcom.vmware.vsphere.security.doc%2FGUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html)
- [vSphere 6.0](https://pubs.vmware.com/vsphere-60/index.jsp?topic=%2Fcom.vmware.vsphere.security.doc%2FGUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html)
- [vSphere 5.5](https://pubs.vmware.com/vsphere-55/index.jsp?topic=%2Fcom.vmware.vsphere.security.doc%2FGUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html). 

For additional information on roles and permissions, please refer to official VMware documentation:
- [Required Privileges for Common Tasks](https://docs.vmware.com/en/VMware-vSphere/6.7/com.vmware.vsphere.security.doc/GUID-4D0F8E63-2961-4B71-B365-BBFA24673FDB.html)
- [Using Roles to Assign Privileges](https://docs.vmware.com/en/VMware-vSphere/6.7/com.vmware.vsphere.security.doc/GUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html)
- [Defined Privileges](https://docs.vmware.com/en/VMware-vSphere/6.7/com.vmware.vsphere.security.doc/GUID-ED56F3C4-77D0-49E3-88B6-B99B8B437B62.html)
