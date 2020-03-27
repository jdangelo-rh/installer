resource "vsphere_folder" "parent" {
  path          = "${var.parent}"
  type          = "vm"
  datacenter_id = "${var.datacenter_id}"
}

resource "vsphere_folder" "folder" {
  path          = "${vsphere_folder.parent.path}/${var.path}"
  type          = "vm"
  datacenter_id = "${var.datacenter_id}"
}

