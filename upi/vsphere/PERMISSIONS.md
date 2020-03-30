
## Required Privileges

In order to use Terraform provider as non priviledged user, some Roles within vCenter must be assigned the following privileges:

- Datastore [Role: ocp-terraform-datastore]
  - Allocate space
  - Low level file operations
- Folder [Role: ocp-terraform-vm]
  - Create folder
  - Delete folder
- StorageProfile [Role: ocp-terraform-vcenter]
  - View
- Network [Role: ocp-terraform-network]
  - Assign network
- Resource [Role: ocp-terraform-resource]
  - Assign vApp to resource pool
  - Assign virtual machine to resource pool
  - Create resource pool
  - Remove resource pool
- vApp [Role: ocp-terraform-vm]
  - Clone
  - View OVF environment
  - vApp application configuration
  - vApp instance configuration
  - vApp resource configuration
- Virtual machine [Role: ocp-terraform-vm]
  - Change Configuration (all)
  - Edit Inventory (all)
  - Guest operations (all)
  - Interaction (all)
  - Provisioning (all)

And these roles have to be given permission on the following objects:
- [Role: ocp-terraform-vm] "/Datacenter/vm/Production/ocp-folder" (The folder where VMs will be alocated, with propagate to children)
- [Role: ocp-terraform-vm] "/Datacenter/vm/templates/rhcos-4.3.8" (The OVA template that will be cloned)
- [ocp-terraform-network] "/Datacenter/network/VM Network" (The VM Network the VMs will attach  to)
- [ocp-terraform-datastore] "/Datacenter/datastore/Datastore" (The Datastore where the VMs disk0 will reside)
- [Role: ocp-terraform-resource] "/Datacenter/host/Cluster/Resources/openshift" (The Resource Group the VMs will attach to)
- [Role: ocp-terraform-vcenter] "/" (vCenter root)

The config-gen.py script generates the commands needed to create these roles and assign them to the corresponding vCenter objects.

These settings have been tested with:
- [vSphere 6.7](https://pubs.vmware.com/vsphere-60/index.jsp?topic=%2Fcom.vmware.vsphere.security.doc%2FGUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html)
- [vSphere 6.0](https://pubs.vmware.com/vsphere-60/index.jsp?topic=%2Fcom.vmware.vsphere.security.doc%2FGUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html)
- [vSphere 5.5](https://pubs.vmware.com/vsphere-55/index.jsp?topic=%2Fcom.vmware.vsphere.security.doc%2FGUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html). 

For additional information on roles and permissions, please refer to official VMware documentation:
- [Required Privileges for Common Tasks](https://docs.vmware.com/en/VMware-vSphere/6.7/com.vmware.vsphere.security.doc/GUID-4D0F8E63-2961-4B71-B365-BBFA24673FDB.html)
- [Using Roles to Assign Privileges](https://docs.vmware.com/en/VMware-vSphere/6.7/com.vmware.vsphere.security.doc/GUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html)
- [Defined Privileges](https://docs.vmware.com/en/VMware-vSphere/6.7/com.vmware.vsphere.security.doc/GUID-ED56F3C4-77D0-49E3-88B6-B99B8B437B62.html)
