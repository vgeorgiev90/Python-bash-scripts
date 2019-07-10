* GET /tokens/list                ---     List all avaialble user tokens
* POST /tokens/create/{user}      ---     Create new user and token
* DELETE /tokens/delete/{user}    ---     Delete existing user
* POST /exec/{name}               ---     Endpoint for future functionalities( expects body with content {"content": "some info"})
* GET /help                       ---     Print this help message
* POST /nfs/connections/{action}  ---     create, delete or get nfs connection string(json body containing {"nfs_host": "1.1.1.1", "key_path": "/path/to/private/key", "kube_api": "2.2.2.2:6443", "kube_token": "some-token-here"}) , for get only nfs host can be provided - {"nfs_host": "127.0.0.1"}
* POST /nfs/volume/{action}       ---     Provision NFS volume(json body {"directory": "/export/dir", "nfs_host": "2.2.2.2", "pvc_size": "1Gi", "pvc_name": "Something", "pvc_namespace": "default"}) action - either create or delete


Some Examples:

* curl -k -XPOST https://localhost:8000/nfs/connections/create -H "Authorization: admin XCRh5Laf3jDkO6667VToHN2HizIHy2ATBjfgjVKc" --data '{"nfs_host": "127.0.0.1", "key_path": "/root/.ssh/id_rsa", "kube_api": "10.0.8.115:6443", "kube_token": "some kube tokeb here"}'

* curl -k -XPOST https://localhost:8000/nfs/volume/create -H "Authorization: admin XCRh5Laf3jDkO6667VToHN2HizIHy2ATBjfgjVKc" --data '{"directory": "/test", "nfs_host": "127.0.0.1", "pvc_size": "1Gi", "pvc_name": "apitest", "pvc_namespace": "default"}'

* curl -k https://localhost:8000/tokens/create/viktor -H "Authorization: admin ko50n4OAAzI3aM0A9ZZk99MZzDcJwwA1DwmWr5Kn"

Api run
Init database
* ./rest_api -cmd db-init -db localhost

Run
* ./rest_api -cmd run -db localhost -cert /path/to/file.crt -key /path/to/file.key
