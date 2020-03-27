data "vsphere_compute_cluster" "compute_cluster" {
  name          = "${var.vsphere_cluster}"
  datacenter_id = "${var.datacenter_id}"
}

/*
resource "vsphere_resource_pool" "parent_resource_pool" {
  name                    = "${var.parent}"
  parent_resource_pool_id = "${data.vsphere_compute_cluster.compute_cluster.resource_pool_id}"
}
*/

resource "vsphere_resource_pool" "resource_pool" {
  name                    = "${var.name}"
//  parent_resource_pool_id = "${vsphere_resource_pool.parent_resource_pool.resource_pool_id}"
  parent_resource_pool_id = "${var.parent}"
}

