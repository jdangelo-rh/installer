#!/usr/bin/env python

# Este script toma como parametro un path a un archivo de configuracion terraform.tfvars
# Como resultado imprime la configuracion del server DHCP y los comandos de GOVC para controlar el VMware

import os
import re
import subprocess
import sys
import stat
import datetime

### Validar prerequisitos: terraform, govc, dig, dhcpd
print ("\n## Validando prerequisitos: terraform, govc, dig, dhcpd")
for cmd in ["terraform", "govc", "dig", "dhcpd"]:
    if os.system("which " + cmd) != 0:
        print(" * ERROR * el comando: " + cmd + " no se encuentra instalado")
        #sys.exit(1)


### Proceso el archivo leyendo las variables del mismo, por suerte el formato de variables de terraform es igual al de python
filename = sys.argv[1]

terraform_file = open(filename, "r")

print("\n## Procesando archivo: " + filename)

for line in terraform_file:
    #print(line)

    comment = re.search("^//", line)
    control_plane_ignition = re.search("END_OF_MASTER_IGNITION", line)
    compute_ignition = re.search("END_OF_WORKER_IGNITION", line)

    if (comment or control_plane_ignition or compute_ignition):
      continue

    exec(line)


### Genero los comandos para apagar las VMs
print("\n## Apagado de las VMs")
for node in bootstrap_name+control_plane_names+compute_names:
    print("govc vm.power -off /%s/vm/%s/%s" % (vsphere_datacenter, cluster_id, node))


### Genero los comandos para encender las VMs
print("\n## Levantar las VMs")
for node in bootstrap_name+control_plane_names+compute_names:
    print("govc vm.power -on /%s/vm/%s/%s" % (vsphere_datacenter, cluster_id, node))


### Genero los comandos para setar las MAC Address
print("\n## Setear MAC addressess")

node_mac = {}
for node in bootstrap_name+control_plane_names+compute_names:
    govc_proc = subprocess.Popen("govc device.info -vm='/%s/vm/%s/%s' ethernet-0" % (vsphere_datacenter, cluster_id, node), stdout=subprocess.PIPE, shell=True)

    node_mac[node] = "00:00:00:00:00:00"

    for line in iter(govc_proc.stdout.readline, ""):
        #print line
        mac_re = re.search("MAC Address", line)

        if (mac_re):
            mac_address = line.split(": ")[1].strip()
            node_mac[node] = mac_address
            print ("govc vm.network.change -vm /%s/vm/%s/%s -net '%s' -net.address %s ethernet-0" % (vsphere_datacenter, cluster_id, node, vm_network, mac_address))



### Verificar que los registros DNS esten bien
print("\n## Verificando registros DNS")

# Generacion de mapping entre hostnames y direcciones IP
hostname_ip = {}

for i in range(len(bootstrap_name)):
    hostname_ip[bootstrap_name[i]] = bootstrap_ip[i]

for i in range(len(control_plane_names)):
    hostname_ip[control_plane_names[i]] = control_plane_ips[i]

for i in range(len(compute_names)):
    hostname_ip[compute_names[i]] = compute_ips[i]

# Verificacion de registros DNS directo y reverso
for node in bootstrap_name+control_plane_names+compute_names:
    dig_proc = subprocess.Popen("dig %s.%s +short" % (node, cluster_domain), stdout=subprocess.PIPE, shell=True)

    found = False

    print ("dig %s.%s +short" % (node, cluster_domain) + " <=> " + hostname_ip[node])

    for line in iter(dig_proc.stdout.readline, ""):
        if line.strip() == hostname_ip[node]:
          found = True

    if found == False:
        print (" * ERROR * fallo la verificacion de DNS del host: " + node)
        #os.system("dig %s.%s +short" % (node, cluster_domain))
        sys.exit(1)

    digx_proc = subprocess.Popen("dig -x %s +short" % (hostname_ip[node]), stdout=subprocess.PIPE, shell=True)

    found = False

    node_fqdn = node + "." + cluster_domain + "."
    print ("dig -x %s +short" % (hostname_ip[node]) + " <=> " + node_fqdn)

    for line in iter(digx_proc.stdout.readline, ""):
        if line.strip() == node_fqdn:
          found = True

    if found == False:
        print (" * ERROR * fallo la verificacion de DNS *reverso* del host: " + node)
        #os.system("dig -x %s +short" % (hostname_ip[node]))
        sys.exit(1)

print ("\nRegistros DNS A y reverso *OK*")

# Verificacion de registros etcd
print("\n## Verificacion de registros etcd")
for i in range(len(control_plane_names)):
    dig_proc = subprocess.Popen("dig etcd-%s.%s +short" % (i, cluster_domain), stdout=subprocess.PIPE, shell=True)

    found = False

    for line in iter(dig_proc.stdout.readline, ""):
        if line.strip() == hostname_ip[control_plane_names[i]]:
          found = True

    if found == False:
      print (" * ERROR * fallo la verificacion de DNS *reverso* del host: " + control_plane_names[i])
      sys.exit(1)

print ("\nRegistros DNS etcd *OK*")

# Verificacion de registros SRV
print("\n## Verificacion de registros SRV")
print ("dig _etcd-server-ssl._tcp.%s SRV +short" % cluster_domain)
os.system("dig _etcd-server-ssl._tcp.%s SRV +short" % cluster_domain)

# Verificacion de APIs
print("\n## Verificacion de APIs")
print ("dig api.%s +short" % cluster_domain)
os.system("dig api.%s +short" % cluster_domain)

print ("dig api-int.%s +short" % cluster_domain)
os.system("dig api-int.%s +short" % cluster_domain)

print ("dig *.apps.%s +short" % cluster_domain)
os.system("dig *.apps.%s +short" % cluster_domain)

### Genero la configuracion del server DHCP
# Grabar un archivo dhpcd.conf y mostrar el comando para copiarlo a /etc + start/stop/enable del dhpcd + yum install (suponer que arrancamos de 0) + echo "" > /var/lib/dhpcd/lease
print("\n## Configurando y levantando el DHCP server")

# Crear un archivo de configuracion /etc/dhcp/dhcpd.conf con las MAC Address
dhcpd_file = os.open("dhcpd.conf", os.O_RDWR | os.O_CREAT)

# Obtengo la subred y la mascara
def cidr_to_netmask(cidr):
  cidr = int(cidr)
  mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
  return (str( (0xff000000 & mask) >> 24)   + '.' +
          str( (0x00ff0000 & mask) >> 16)   + '.' +
          str( (0x0000ff00 & mask) >> 8)    + '.' +
          str( (0x000000ff & mask)))

subnet = machine_cidr.split("/")[0]
cidr = machine_cidr.split("/")[1]

netmask = cidr_to_netmask(cidr)

dhcpd_conf = \
'''
# dhcpd.conf
# Generated by: config-gen.py

option domain-name "%s";
option domain-name-servers %s, %s, %s;

default-lease-time 600;
max-lease-time 7200;

# Use this to send dhcp log messages to a different log file (you also
# have to hack syslog.conf to complete the redirection).
log-facility local7;

subnet %s netmask %s {
    option routers %s;
}
''' % (cluster_domain, dns_ips[0], dns_ips[1], dns_ips[2], subnet, netmask, gateway_ip)

for node in bootstrap_name+control_plane_names+compute_names:
    dhcpd_conf += \
    '''
    host %s {
      hardware ethernet %s;
      option host-name "%s";
      fixed-address %s;
    }
    ''' % (node, node_mac[node], node + "." + cluster_domain, hostname_ip[node])
    #print(node + " -> " + node_mac[node])
    #print (test)

dhcpd_conf += "\n"
#print(dhcpd_conf)

ret = os.write(dhcpd_file, dhcpd_conf)

os.close(dhcpd_file)

os.chmod("dhcpd.conf", stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

# Hacer backup del archivo dhcpd.conf
os.system("cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf-" + datetime.datetime.now().strftime("%Y%m%d%M%S"))

# Copiar el archivo generado a /etc/dhcp/dhcpd.conf
print ("cp dhcpd.conf /etc/dhcp/dhcpd.conf")

# Detener el dhcpd
print ("systemctl stop dhcpd")

# Borrar los leases
print ("echo '' > /var/lib/dhcpd/dhcpd.leases")
print ("echo '' > /var/lib/dhcpd/dhcpd.leases~")

# Iniciar el dhcpd
print ("systemctl start dhcpd")

# Mostrar el status
print ("systemctl status dhcpd")


