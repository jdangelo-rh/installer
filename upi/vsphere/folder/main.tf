resource "vsphere_folder" "folder" {
  path          = "${var.parent}/${var.path}"
  type          = "vm"
  datacenter_id = "${var.datacenter_id}"
}

