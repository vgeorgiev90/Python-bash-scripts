# Basic RESTfull API script to be used with Ansible playbooks for dynamic nfs provisioning
https://github.com/vgeorgiev90/Ansible/tree/master/dynamic-hostpath-with-nfs

Notes:
* hardcoded execution paths for playbooks "/home/ansible/dynamic-hostpath-with-nfs/hosts" - to be fixed
* Very basic auth with token that needs to be places in config.json in the same dir as the script - to be fixed

Endpoints:
1. /configs   -   List all ansible configs [GET]
2. /configs/NAME 
   * GET    - check the content of the file
   * POST   - create new config file (json body)
   * PUT    - modify option in the config file
   * DELETE - delete file 
3. /configs/help
   * GET    - Check the options that needs to be provided for new file
3. /exec/NAME
   * POST   - exec ansible scripts with config file specified

Example Usage:
* Get configs
curl -XGET IP:5000/configs

* Get content of test-hosts file from configs
curl -XGET IP:5000/configs/test-hosts

* Create new file
curl -XPOST IP:5000/configs/new-file -H "token: TOKEN" -d 'options={"vg_name": "kube-vg", "lv_name": "api-test", "devices": "[\"/dev/vdb1\"]", "lv_size": "1g","fs_type": "ext4","mount_name": "/kubernetes/api","worker_host": "10.0.11.170", "nfs_server": "10.0.11.170", "work_dir": "/api"}'

* Change a value in existing file
curl -XPUT IP:5000/configs/existing-file -H "token: TOKEN" -d 'option=lv_name=api-lv' -d 'replace=lv_name=api2-lv'

* Delete a file
curl -XDELETE IP:5000/configs/file -H "token: TOKEN"

* Exec ansible script with config file
curl -XPOST IP:5000/exec/file -H "token: TOKEN" -H "provision: vginit/volume" -d "state=present/absent"
