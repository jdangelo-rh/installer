#!/usr/bin/env python

# Este script toma como parametro un path a un archivo de configuracion terraform.tfvars
# Como resultado imprime la configuracion del server DHCP y los comandos de GOVC para controlar el VMware

import os
import re
import subprocess
import sys
import stat
import datetime

### NTP servers:
# NOTA: Los NTP se configuran despues mediante el machine config, no se configuran mas por DHCP

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

### Verficar que me hayan pasado los parametros correctos
if len(sys.argv) != 2:
    print(bcolors.FAIL + " * ERROR * " + bcolors.ENDC + "Cantidad de parametros incorrecta")
    print("USO: config-gen.py terraform.tfvars")
    sys.exit(1)

### Validar prerequisitos: terraform, govc, dig, dhcpd
print ("\n## Validando prerequisitos: terraform, govc, dig, dhcpd")
for cmd in ["terraform", "govc", "dig", "dhcpd"]:
    if os.system("which " + cmd) != 0:
        print(bcolors.FAIL + " * ERROR * " + bcolors.ENDC + " el comando: " + cmd + " no se encuentra instalado")
        sys.exit(1)


### Validar los parametros de govc
print ("\n## Validando los parametros de govc")
if  os.getenv('GOVC_URL') == None or \
    os.getenv('GOVC_USERNAME') == None or \
    os.getenv('GOVC_PASSWORD') == None or \
    os.getenv('GOVC_NETWORK') == None or \
    os.getenv('GOVC_DATASTORE') == None or \
    os.getenv('GOVC_INSECURE') == None:
    print(bcolors.FAIL + " * ERROR * " + bcolors.ENDC + " el entorno de govc no se encuentra configurado.")
    print("Por favor configure el entorno especificando el valor de las siguientes variables:")
    print('''
export GOVC_URL='vcenter.example.com'
export GOVC_USERNAME='VSPHERE_ADMIN_USER'
export GOVC_PASSWORD='VSPHERE_ADMIN_PASSWORD'
export GOVC_NETWORK='VM Network'
export GOVC_DATASTORE='Datastore'
export GOVC_INSECURE=1 # If the host above uses a self-signed cert
    ''')
    sys.exit(1)


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


### Genero los comandos para crear los roles
print('''
## Role creation
govc role.create ocp-terraform-network \\
	Network.Assign
govc role.create ocp-terraform-datastore \\
	Datastore.AllocateSpace \\
	Datastore.FileManagement 
govc role.create ocp-terraform-vcenter \\
	StorageProfile.View
govc role.create ocp-terraform-resource \\
	Resource.AssignVAppToPool \\
	Resource.AssignVMToPool \\
	Resource.CreatePool \\
	Resource.DeletePool
govc role.create ocp-terraform-vm \\
	VApp.ApplicationConfig \\
	VApp.Clone \\
	VApp.ExtractOvfEnvironment \\
	VApp.InstanceConfig VApp.ResourceConfig \\
	Folder.Create Folder.Delete \\
	VirtualMachine.Config.AddNewDisk \\
	VirtualMachine.Config.AdvancedConfig \\
	VirtualMachine.Config.CPUCount \\
	VirtualMachine.Config.DiskExtend \\
	VirtualMachine.Config.EditDevice \\
	VirtualMachine.Config.Memory \\
	VirtualMachine.Config.Rename \\
	VirtualMachine.Config.Resource \\
	VirtualMachine.Config.Settings \\
	VirtualMachine.GuestOperations.Execute \\
	VirtualMachine.GuestOperations.Modify \\
	VirtualMachine.GuestOperations.ModifyAliases \\
	VirtualMachine.GuestOperations.Query \\
	VirtualMachine.GuestOperations.QueryAliases \\
	VirtualMachine.Interact.ConsoleInteract \\
	VirtualMachine.Interact.GuestControl \\
	VirtualMachine.Interact.Pause \\
	VirtualMachine.Interact.PowerOff \\
	VirtualMachine.Interact.PowerOn \\
	VirtualMachine.Interact.Reset \\
	VirtualMachine.Interact.SetCDMedia \\
	VirtualMachine.Interact.Suspend \\
	VirtualMachine.Interact.ToolsInstall \\
	VirtualMachine.Inventory.Create \\
	VirtualMachine.Inventory.CreateFromExisting \\
	VirtualMachine.Inventory.Delete \\
	VirtualMachine.Inventory.Move \\
	VirtualMachine.Inventory.Register \\
	VirtualMachine.Inventory.Unregister \\
	VirtualMachine.Provisioning.Clone \\
	VirtualMachine.Provisioning.CloneTemplate \\
	VirtualMachine.Provisioning.CreateTemplateFromVM \\
	VirtualMachine.Provisioning.Customize \\
	VirtualMachine.Provisioning.DeployTemplate \\
	VirtualMachine.Provisioning.DiskRandomAccess \\
	VirtualMachine.Provisioning.DiskRandomRead \\
	VirtualMachine.Provisioning.FileRandomAccess \\
	VirtualMachine.Provisioning.GetVmFiles \\
	VirtualMachine.Provisioning.MarkAsTemplate \\
	VirtualMachine.Provisioning.MarkAsVM \\
	VirtualMachine.Provisioning.ModifyCustSpecs \\
	VirtualMachine.Provisioning.PromoteDisks \\
	VirtualMachine.Provisioning.PutVmFiles \\
	VirtualMachine.Provisioning.ReadCustSpecs
''')

## Busco la carpeta donde esta alojado el template
govc_find_proc = subprocess.Popen("govc find -type m -name=%s" % (vm_template), shell=True, stdout=subprocess.PIPE)

vm_template_path = ""

for line in iter(govc_find_proc.stdout.readline, ""):
    vm_template_path = line.rstrip()
    break

if vm_template_path == "":
    print(bcolors.FAIL + " * ERROR * " + bcolors.ENDC + " no se encontro la ruta del template especificado: " + vm_template)
else:
    print("Se encontro el template en la ruta: " + vm_template_path)

govc_find_proc.stdout.close()

## Busco el nombre del Resource Pool
govc_find_proc = subprocess.Popen("for ResourcePool in $(govc find / -type p); do govc ls -l -i $ResourcePool; done", shell=True, stdout=subprocess.PIPE)

vm_resource_pool = ""

for line in iter(govc_find_proc.stdout.readline, ""):
    if line.find(vm_resource_pool_id) != -1:
        #vm_resource_pool = line.rstrip()
        #print(line.rstrip())
        vm_resource_pool = line.rstrip().split(" ")[1]

if vm_resource_pool == "":
    print(bcolors.FAIL + " * ERROR * " + bcolors.ENDC + " no se encontro el resource pool asociado al ID especificado: " + vm_resource_pool_id)
else:
    print("Se encontro el resource group en la ruta: " + vm_resource_pool)

govc_find_proc.stdout.close()

### Genero los comandos para establecer los permisos
print("\n## Set permissions on vCenter objects")
print("govc permissions.set -principal %s -role ocp-terraform-vm -propagate=true \"/%s/vm/%s\"" % (vsphere_user, vsphere_datacenter, vm_folder))
print("govc permissions.set -principal %s -role ocp-terraform-vm -propagate=false \"/%s/vm/%s\"" % (vsphere_user, vsphere_datacenter, vm_template_path))
print("govc permissions.set -principal %s -role ocp-terraform-network -propagate=false \"/%s/network/%s\"" % (vsphere_user, vsphere_datacenter, vm_network))
print("govc permissions.set -principal %s -role ocp-terraform-datastore -propagate=false \"/%s/datastore/%s\"" % (vsphere_user, vsphere_datacenter, vsphere_datastore))
print("govc permissions.set -principal %s -role ocp-terraform-resource -propagate=false \"/%s\"" % (vsphere_user, vm_resource_pool))
print("govc permissions.set -principal %s -role ocp-terraform-vcenter -propagate=false \"/\"" % (vsphere_user))

sys.exit(1)

### Genero los comandos para apagar las VMs
print("\n## Apagado de las VMs")
for node in bootstrap_name+control_plane_names+compute_names:
    print("govc vm.power -off /%s/vm/%s/%s" % (vsphere_datacenter, vm_folder, node))


### Genero los comandos para encender las VMs
print("\n## Levantar las VMs")
for node in bootstrap_name+control_plane_names+compute_names:
    print("govc vm.power -on /%s/vm/%s/%s" % (vsphere_datacenter, vm_folder, node))


### Genero los comandos para setar las MAC Address
print("\n## Setear MAC addressess")

node_mac = {}
for node in bootstrap_name+control_plane_names+compute_names:
    govc_proc = subprocess.Popen("govc device.info -vm='/%s/vm/%s/%s' ethernet-0" % (vsphere_datacenter, vm_folder, node), stdout=subprocess.PIPE, shell=True)

    node_mac[node] = "00:00:00:00:00:00"

    for line in iter(govc_proc.stdout.readline, ""):
        #print line
        mac_re = re.search("MAC Address", line)

        if (mac_re):
            mac_address = line.split(": ")[1].strip()
            node_mac[node] = mac_address
            print ("govc vm.network.change -vm /%s/vm/%s/%s -net '%s' -net.address %s ethernet-0" % (vsphere_datacenter, vm_folder, node, vm_network, mac_address))



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
def dns_verify(dns_ip):
    for node in bootstrap_name+control_plane_names+compute_names:
        dig_cmd = "dig %s.%s +short" % (node, cluster_domain) + " @" + dns_ip
        
        dig_proc = subprocess.Popen(dig_cmd, stdout=subprocess.PIPE, shell=True)

        found = False

        print (dig_cmd + " <=> " + hostname_ip[node])

        for line in iter(dig_proc.stdout.readline, ""):
            if line.strip() == hostname_ip[node]:
              found = True

        if found == False:
            print (bcolors.FAIL + " * ERROR * " + bcolors.ENDC + " fallo la verificacion de DNS del host: " + node)
            print ("DNS Server: " + dns_ip)
            #os.system("dig %s.%s +short" % (node, cluster_domain))
            sys.exit(1)

        digx_cmd = "dig -x %s +short" % (hostname_ip[node]) + " @" + dns_ip

        digx_proc = subprocess.Popen(digx_cmd, stdout=subprocess.PIPE, shell=True)

        found = False

        node_fqdn = node + "." + cluster_domain + "."
        print (digx_cmd + " <=> " + node_fqdn)

        for line in iter(digx_proc.stdout.readline, ""):
            if line.strip() == node_fqdn:
              found = True

        if found == False:
            print (bcolors.FAIL + " * ERROR * " + bcolors.ENDC + " fallo la verificacion de DNS *reverso* del host: " + node)
            print ("DNS Server: " + dns_ip)
            #os.system("dig -x %s +short" % (hostname_ip[node]))
            sys.exit(1)

    print ("\nRegistros DNS A y reverso" + bcolors.OKGREEN + " * OK *" + bcolors.ENDC)

for dns_ip in dns_ips:
    #print(dns_ip)
    dns_verify(dns_ip)

#sys.exit(1)

# Verificacion de registros etcd
print("\n## Verificacion de registros etcd")
for i in range(len(control_plane_names)):
    dig_proc = subprocess.Popen("dig etcd-%s.%s +short" % (i, cluster_domain), stdout=subprocess.PIPE, shell=True)

    found = False

    for line in iter(dig_proc.stdout.readline, ""):
        if line.strip() == hostname_ip[control_plane_names[i]]:
          found = True

    if found == False:
      print (bcolors.FAIL + " * ERROR * " +  bcolors.ENDC + "fallo la verificacion de DNS *reverso* del host: " + control_plane_names[i])
      sys.exit(1)

print ("\nRegistros DNS etcd" + bcolors.OKGREEN + " * OK *" + bcolors.ENDC)

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
dhcpd_file = os.open("dhcpd.conf", os.O_WRONLY | os.O_CREAT | os.O_TRUNC)

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

dhcpd_conf_general = \
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

dhcpd_conf_hosts = ""

for node in bootstrap_name+control_plane_names+compute_names:
    dhcpd_conf_hosts += \
    '''
host %s {
  hardware ethernet %s;
  option host-name "%s";
  fixed-address %s;
}
    ''' % (node, node_mac[node], node + "." + cluster_domain, hostname_ip[node])
    #print(node + " -> " + node_mac[node])
    #print (test)

dhcpd_conf = dhcpd_conf_general + dhcpd_conf_hosts + "\n"

#print(dhcpd_conf)
#sys.exit(0)

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


