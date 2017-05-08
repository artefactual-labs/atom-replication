How this works?

- Change the "hosts" file, to reflect the ip of your source atom instance. If both elasticsearch and mysql are in the same host, put the same ip twice
- Do the same for the destination atom instance

- Configure group_vars/all to reflect the username, database and password for mysql source atom database and destination one. 

- Run the playbook with:
  ansible-playbook -i hosts playbook.yml

This playbook will take care of:
 - Create folder to save dumps
 - Configure ES snapshots on source and destination servers
 - Create elasticsearch and mysql backups for the source atom instance
 - Copy ES / Mysql dumps from source to destination
 - Load the backups in the destination host


