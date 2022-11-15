# Access To Memory replication playbook

## IMPORTANT: This playbook is now deprecated and no longer being supported

For a newer, improved version of the AtoM replication playbook, please see: 

* https://github.com/artefactual-labs/ansible-atom-replication

-----

This playbook will take care of:
 - Configure ES snapshots on source and destination servers
 - Create elasticsearch and mysql backups for the source atom instance
 - Copy ES / Mysql dumps from source to destination
 - Load the backups in the destination host


## Prerequisites

 You need ansible , and ssh access to all involved hosts

## How this works?

- Change the "hosts" file, to reflect the ip of your source atom instance. If both elasticsearch and mysql are in the same host, put the same ip twice
- Do the same for the destination atom instance

- Configure group_vars/all to reflect the username, database and password for mysql source atom database and destination one.

- Run the playbook with:
  ansible-playbook -i hosts playbook.yml

- **Note**: After replication you should [clear the symfony and php-fpm (apcu) caches](https://www.accesstomemory.org/en/docs/latest/admin-manual/maintenance/clear-cache/) for the updates to display properly on the destination AtoM instance. 
