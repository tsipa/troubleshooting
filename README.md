1
Cloud Information collector
===============

**1. Introduction**
--------------
After the cloud is being operational, we need to transmit complete information about 
a cloud to the support team. During the support of the customer installation 
a lot of debug information is required, it is not easy to predict which information 
will be required on next step, and it is impossible to get manually all necessary 
information in advance either.

**2. Purpose**
--------------
We need automation tool which will be able to collect all necessary information about 
cloud in one step to provide the “Support Team” with the collected information.

**3. Scope**
--------------
This software is intended to be utility that collects all possible information. 
It is designed only to provide necessary information to the “Support Team” to understand 
root of the issue and make adequate decision on how to fix it.

**Hardware specification**
- OpenStack nodes: manufacturer and model; CPU, RAM, disk (role), network type and ports
- Network: manufacturer and models for chassis, tor, eor, core layers;     
- Storage: manufacturer and model; disk available; protocol

**Infrastructure Software**
- OS: Distro, version, kernel, customization (extra packages, selinux)
- Hypervisor type, customizations and optimizations

**OpenStack Software**
- Mirantis OpenStack version (or alternate installer type and version)
- Log files: where is stored
- Controllers: H/A or not, their numbers; list all co-located services
- Nova: Ephemeral drive storage, scheduler algorithm
- Keystone: integration
- Cinder: Drivers configured; scheduler, other config, QOS, boot from volume, etc
- MQ (if not rabbit in default config, define the software and config)
- Object Storage: what service is used, settings
- Glance: back-end
- Monitoring: what service, settings
- Services: <Heat/Ceilometer/Savanna/Murano>, settings, deviations from standart settings

**Neutron:**
- Segmentation
- config (l2 and L3) and plugin used
- describe any integration with virtual or physical appliances

**Network**
- Network scheme
- Screenshot of “Fuel networking settings” page
- Nodes spreadsheet (Roles, Interfaces, IP-addresses, Bonding, MACs, IPMI)
- Networks spreadsheet: Name, NIC, IP-range, VLAN
- Switches settings & ports speeds
- Remote access

**After deployment was finished**
- List of changes and reasons we did this
- Problems that were faced and their solutions
- Final “site.pp” and “config.yaml”
- Fuel diagnostic snapshot
    
**Files/outputs from all nodes**
- Configuration files of services (nova.conf, ceph.conf, ...) or tarball of whole /etc directory
- Installed packages, their versions (rpm -qa or dpkg -l)
- Processes, service and their status (ps aux and /etc/init.d/* status)
- Netstat -nlp
- Iptables rules
- Partitions / RAIDs
- OVS related information (ovs-vsctl show; ovs-dpctl show; ovs-dpctl dump-flows)
- ip a; ip ro; ip ne
