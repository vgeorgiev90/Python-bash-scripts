* GET /tokens/list                ---     List all avaialble user tokens
* POST /tokens/create/{user}      ---     Create new user and token
* DELETE /tokens/delete/{user}    ---     Delete existing user
* POST /exec/{name}               ---     Endpoint for future functionalities( expects body with content {"content": "some info"})
* GET /help                       ---     Print this help message
* POST /nfs/connections/{action}  ---     create, delete or get nfs connection string(json body containing {"nfs_host": "1.1.1.1", "key_path": "/path/to/private/key", "kube_api": "2.2.2.2:6443", "kube_token": "some-token-here"}) , for get only nfs host can be provided - {"nfs_host": "127.0.0.1"}
* POST /nfs/volume/{action}       ---     Provision NFS volune(json body {"directory": "/export/dir", "nfs_host": "2.2.2.2", "pvc_size": "1Gi", "pvc_name": "Something", "pvc_namespace": "default"}) action - either create or delete
