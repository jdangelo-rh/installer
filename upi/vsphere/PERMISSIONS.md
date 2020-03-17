
## Required Privileges

In order to use Terraform provider as non priviledged user, a Role within vCenter must be assigned the following privileges:

-   Datastore
    -   Allocate space
    -   Browse datastore
    -   Low level file operations
    -   Remove file
    -   Update virtual machine files
    -   Update virtual machine metadata
-   Folder (all)
    -   Create folder
    -   Delete folder
    -   Move folder
    -   Rename folder
-   Network
    -   Assign network
-   Resource
    -   Apply recommendation
    -   Assign virtual machine to resource pool
-   Virtual Machine
    -   Configuration (all) - for now
    -   Guest Operations (all) - for now
    -   Interaction (all)
    -   Inventory (all)
    -   Provisioning (all)

These settings were tested with  [vSphere 6.0](https://pubs.vmware.com/vsphere-60/index.jsp?topic=%2Fcom.vmware.vsphere.security.doc%2FGUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html)  and  [vSphere 5.5](https://pubs.vmware.com/vsphere-55/index.jsp?topic=%2Fcom.vmware.vsphere.security.doc%2FGUID-18071E9A-EED1-4968-8D51-E0B4F526FDA3.html). For additional information on roles and permissions, please refer to official VMware documentation
- [Required Privileges for Common Tasks](https://docs.vmware.com/en/VMware-vSphere/6.5/com.vmware.vsphere.security.doc/GUID-4D0F8E63-2961-4B71-B365-BBFA24673FDB.html)
- [Defined Privileges](https://docs.vmware.com/en/VMware-vSphere/6.7/com.vmware.vsphere.security.doc/GUID-ED56F3C4-77D0-49E3-88B6-B99B8B437B62.html)
