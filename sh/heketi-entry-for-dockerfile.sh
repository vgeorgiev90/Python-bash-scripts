#!/bin/bash
## This script is intended to be used with the following dockerfile
####################################################################
#FROM ubuntu:latest
#RUN apt-get update; apt-get install wget openssh-client vim -y
#RUN ssh-keygen -N "" -f ~/.ssh/id_rsa
#COPY heketi-entry.sh /root/heketi-entry.sh
#RUN wget https://github.com/heketi/heketi/releases/download/v8.0.0/heketi-v8.0.0.linux.amd64.tar.gz -P /root && tar -xzf /root/heketi-v8.0.0.linux.amd64.tar.gz -C /root && mv /root/heketi/heketi /usr/bin/ && chmod +x /usr/bin/heketi && chmod +x /root/heketi-entry.sh
#EXPOSE 8080 8081
#VOLUME /var/lib/heketi
#VOLUME /etc/heketi
#ENTRYPOINT /root/heketi-entry.sh $CLUSTER_SIZE
####################################################################
##Ref: https://hub.docker.com/r/viktor90/heketi/


cluster_members="${1}"

#### Check if there is heketi files
if [ ! -f /etc/heketi/heketi.json ];then


#### Generate topology file based on members number
cat > /etc/heketi/topology.json << EOF
{
  "clusters": [
   {
     "nodes": [
EOF

for i in `seq 1 $((${cluster_members} - 1))`;do
  cat >> /etc/heketi/topology.json << EOF
{ "node": {
           "hostnames": { "manage": ["node${i}"], "storage": ["node${i}"], "zone": 1  },
           "zone": 1
          },
         "devices": ["/dev/vdb"]
       },
EOF
done

## Because of the ... trailing ,
cat >> /etc/heketi/topology.json << EOF
{ "node": {
           "hostnames": { "manage": ["node${cluster_members}"], "storage": ["node${cluster_members}"], "zone": 1  },
           "zone": 1
          },
         "devices": ["/dev/vdb"]
       }
EOF

cat >> /etc/heketi/topology.json << EOF
     ]
     }
   ]
}
EOF


######### install and configure heketi #############

mkdir -p /var/lib/heketi/.ssh
mkdir /etc/heketi
useradd -d /var/lib/heketi heketi
cp ~/.ssh/id_rsa /var/lib/heketi/.ssh
chmod 700 /var/lib/heketi/.ssh
chmod 400 /var/lib/heketi/.ssh/id_rsa
chown -R heketi:heketi /var/lib/heketi

cat > /etc/heketi/heketi.json << EOF

{
  "_port_comment": "Heketi Server Port Number",
  "port": "8080",

        "_enable_tls_comment": "Enable TLS in Heketi Server",
        "enable_tls": false,

        "_cert_file_comment": "Path to a valid certificate file",
        "cert_file": "",

        "_key_file_comment": "Path to a valid private key file",
        "key_file": "",


  "_use_auth": "Enable JWT authorization. Please enable for deployment",
  "use_auth": false,

  "_jwt": "Private keys for access",
  "jwt": {
    "_admin": "Admin has access to all APIs",
    "admin": {
      "key": "My Secret"
    },
    "_user": "User only has access to /volumes endpoint",
    "user": {
      "key": "My Secret"
    }
  },

  "_backup_db_to_kube_secret": "Backup the heketi database to a Kubernetes secret when running in Kubernetes. Default is off.",
  "backup_db_to_kube_secret": false,

  "_glusterfs_comment": "GlusterFS Configuration",
  "glusterfs": {
    "_executor_comment": [
      "Execute plugin. Possible choices: mock, ssh",
      "mock: This setting is used for testing and development.",
      "      It will not send commands to any node.",
      "ssh:  This setting will notify Heketi to ssh to the nodes.",
      "      It will need the values in sshexec to be configured.",
      "kubernetes: Communicate with GlusterFS containers over",
      "            Kubernetes exec api."
    ],
    "executor": "ssh",

    "_sshexec_comment": "SSH username and private key file information",
    "sshexec": {
      "keyfile": "/var/lib/heketi/.ssh/id_rsa",
      "user": "root",
      "port": "22",
      "fstab": "/etc/fstab",
      "backup_lvm_metadata": false
    },

    "_kubeexec_comment": "Kubernetes configuration",
    "kubeexec": {
      "host" :"https://kubernetes.host:8443",
      "cert" : "/path/to/crt.file",
      "insecure": false,
      "user": "kubernetes username",
      "password": "password for kubernetes user",
      "namespace": "OpenShift project or Kubernetes namespace",
      "fstab": "Optional: Specify fstab file on node.  Default is /etc/fstab",
      "backup_lvm_metadata": false
    },

    "_db_comment": "Database file name",
    "db": "/var/lib/heketi/heketi.db",

     "_refresh_time_monitor_gluster_nodes": "Refresh time in seconds to monitor Gluster nodes",
    "refresh_time_monitor_gluster_nodes": 120,

    "_start_time_monitor_gluster_nodes": "Start time in seconds to monitor Gluster nodes when the heketi comes up",
    "start_time_monitor_gluster_nodes": 10,

    "_loglevel_comment": [
      "Set log level. Choices are:",
      "  none, critical, error, warning, info, debug",
      "Default is warning"
    ],
    "loglevel" : "debug",

    "_auto_create_block_hosting_volume": "Creates Block Hosting volumes automatically if not found or exsisting volume exhausted",
    "auto_create_block_hosting_volume": true,

    "_block_hosting_volume_size": "New block hosting volume will be created in size mentioned, This is considered only if auto-create is enabled.",
    "block_hosting_volume_size": 500,

    "_block_hosting_volume_options": "New block hosting volume will be created with the following set of options. Removing the group gluster-block option is NOT recommended. Additional options can be added next to it separated by a comma.",
    "block_hosting_volume_options": "group gluster-block"
  }
}
EOF

chown -R heketi: /etc/heketi
/usr/bin/heketi --config=/etc/heketi/heketi.json

### If there are files (container restarted) just run heketi

else
/usr/bin/heketi --config=/etc/heketi/heketi.json
fi
