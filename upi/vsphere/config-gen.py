#!/usr/bin/env python

# Este script toma como parametro un path a un archivo de configuracion terraform.tfvars
# Como resultado imprime la configuracion del server DHCP y los comandos de GOVC para controlar el VMware

import os
import sys
import re

# Primer paso es importar el archivo
filename = sys.argv[1]

terraform_file = open(filename, "r")

# Proceso el archivo leyendo las variables del mismo, por suerte el formato de variables de terraform es igual al de python
for line in terraform_file:
    #print(line)
    
    comment = re.search("^//", line)
    control_plane_ignition = re.search("END_OF_MASTER_IGNITION", line)
    compute_ignition = re.search("END_OF_WORKER_IGNITION", line)

    if (comment or control_plane_ignition or compute_ignition):
      continue

    exec(line)
    
#print (compute_names)

# Generar los comandos para apagar las VMs
for node in bootstrap_name+control_plane_names+compute_names:
    print("govc vm.power -off /%s/vm/%s/%s" % (vsphere_datacenter, cluster_id, node))

# Generar la configuracion del server DHCP
# Grabar un archivo dhpcd.conf y mostrar el comando para copiarlo a /etc + start/stop/enable del dhpcd + yum install (suponer que arrancamos de 0) + echo "" > /var/lib/dhpcd/lease
print("vi /etc/dhcp/dhcpd.conf\n" \
"\n" \
"systemctl stop dhcpd\n" \
"\n" \
"echo "" > /var/lib/dhcpd/dhcpd.leases\n" \
"echo "" > /var/lib/dhcpd/dhcpd.leases~\n" \
"\n" \
"systemctl start dhcpd\n" \
"\n" \
"systemctl status dhcpd\n")

# Generar los comandos para encender las VMs
for node in bootstrap_name+control_plane_names+compute_names:
    print("govc vm.power -on /%s/vm/%s/%s" % (vsphere_datacenter, cluster_id, node))

# Generar los comandos para planchar las MAC Address



