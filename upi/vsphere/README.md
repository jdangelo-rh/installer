# Reference Documentation:
https://blog.openshift.com/deploying-a-user-provisioned-infrastructure-environment-for-openshift-4-1-on-vsphere/
https://blog.openshift.com/openshift-4-2-vsphere-install-quickstart/
https://docs.openshift.com/container-platform/4.3/installing/installing_vsphere/installing-vsphere.html

# Pre-Requisites

* terraform version 0.11.12 (https://releases.hashicorp.com/terraform/0.11.12)
* VMWare command line tool govc (https://github.com/vmware/govmomi)

# Setup Prerequisites
Download the terraform executable and install it
```
curl -O https://releases.hashicorp.com/terraform/0.11.12/terraform_0.11.12_linux_amd64.zip
unzip terraform_0.11.12_linux_amd64.zip
cp terraform /usr/local/bin
```

Validate version (should be: v0.11.12)
```
terraform version
```

Download and install VMware CLI
```
curl -L https://github.com/vmware/govmomi/releases/download/v0.20.0/govc_linux_amd64.gz > govc_0.20.0_linux_amd64.gz
gunzip govc_0.20.0_linux_amd64.gz
mv govc_0.20.0_linux_amd64 /usr/local/bin/govc
chmod +x /usr/local/bin/govc
```

Configure the CLI with the vSphere settings
```
export GOVC_URL='vcenter.example.com'
export GOVC_USERNAME='admin'
export GOVC_PASSWORD='passw0rd'
export GOVC_NETWORK='VM Network'
export GOVC_DATASTORE='Datastore'
export GOVC_INSECURE=1 # If the host above uses a self-signed cert
```

Test the govc CLI settings
```
govc ls
govc about
```

List resource pools
```
$ govc find / -type p
/Datacenter/host/Cluster/Resources
```

Download the OVA and import it into the Template Repository
```
curl -O https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/4.3/latest/rhcos-4.3.0-x86_64-vmware.ova
govc import.ova -name=rhcos-4.3.0 -pool=/Datacenter/host/Cluster/Resources  ./rhcos-4.3.0-x86_64-vmware.ova
govc vm.markastemplate vm/rhcos-4.3.0
```

# Build a Cluster
Download the OpenShift client
```
curl -O https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-linux-4.3.0.tar.gz
curl -O https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux-4.3.0.tar.gz
tar xzvf openshift-install-linux-4.3.0.tar.gz
tar xzvf openshift-client-linux-4.3.0.tar.gz
```


# Build a Cluster

1. Create an install-config.yaml.
The machine CIDR for the dev cluster is 139.178.89.192/26.

```
apiVersion: v1
baseDomain: devcluster.openshift.com
metadata:
  name: mstaeble
networking:
  machineCIDR: "139.178.89.192/26"
platform:
  vsphere:
    vCenter: vcsa.vmware.devcluster.openshift.com
    username: YOUR_VSPHERE_USER
    password: YOUR_VSPHERE_PASSWORD
    datacenter: dc1
    defaultDatastore: nvme-ds1
pullSecret: YOUR_PULL_SECRET
sshKey: YOUR_SSH_KEY
```

2. Run `openshift-install create ignition-configs`.

3. Fill out a terraform.tfvars file with the ignition configs generated.
There is an example terraform.tfvars file in this directory named terraform.tfvars.example. 
The example file is set up for use with the dev cluster running at vcsa.vmware.devcluster.openshift.com. 
At a minimum, you need to set values for the following variables.
* cluster_id
* cluster_domain
* vsphere_user
* vsphere_password
* ipam_token
* bootstrap_ignition_url
* control_plane_ignition
* compute_ignition
(The bootstrap ignition config must be placed in a location that will be accessible by the bootstrap machine. 
For example, you could store the bootstrap ignition config in a gist.)

4. Run `terraform init`.

5. Ensure that you have you AWS profile set and a region specified. 
The installation will use create AWS route53 resources for routing to the OpenShift cluster.

6. Run `terraform apply -auto-approve`.
This will reserve IP addresses for the VMs.

7. Run `openshift-install wait-for bootstrap-complete`. 
Wait for the bootstrapping to complete.

8. Run `terraform apply -auto-approve -var 'bootstrap_complete=true'`.
This will destroy the bootstrap VM.

9. Run `openshift-install wait-for install-complete`. 
Wait for the cluster install to finish.

10. Enjoy your new OpenShift cluster.

11. Run `terraform destroy -auto-approve`.

