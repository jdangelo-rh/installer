#!/usr/bin/env python

# Este script toma como parametro un path a un archivo de configuracion terraform.tfvars
# Como resultado imprime la configuracion del server DHCP y los comandos de GOVC para controlar el VMware

import os
import sys

# Primer paso es importar el archivo
filename = sys.argv[1]

terraform_file = open(filename, "r")

for line in terraform_file:
    eval(line)


# Generar los comandos para apagar las VMs

# Generar la configuracion del server DHCP
# Grabar un archivo dhpcd.conf y mostrar el comando para copiarlo a /etc + start/stop/enable del dhpcd + yum install (suponer que arrancamos de 0) + echo "" > /var/lib/dhpcd/lease

# Generar los comandos para encender las VMs

# Generar los comandos para planchar las MAC Address



