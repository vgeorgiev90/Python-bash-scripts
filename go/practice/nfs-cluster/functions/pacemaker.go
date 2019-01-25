package functions

import (
        "fmt"
        "os"
        "os/exec"
        "strings"
        "text/template"
)

type Pm_config struct {
	Node1 string
	Node2 string
}

func PacemakerSetup(nodes []string) {
	var pm Pm_config
	pm.Node1 = nodes[0]
	pm.Node2 = nodes[1]

	t, err := template.New("corosync").Parse(`
totem {
  version: 2
  secauth: off
  cluster_name: nfs
  transport: udpu
  rrp_mode: passive
}
nodelist {
  node {
  ring0_addr: {{ .Node1 }}
  nodeid: 1
  }
  node {
  ring0_addr: {{ .Node2 }}
  nodeid: 2
  }
}
quorum {
  provider: corosync_votequorum
  two_node: 1
}
logging {
  to_syslog: yes
}
`)

	f, err := os.Create("/etc/corosync/corosync.conf")
	t_err := t.Execute(f, pm)
	if t_err != nil {
		fmt.Println(err)
	}

	cmd := "systemctl enable corosync ; systemctl start corosync ; systemctl enable pacemaker; systemctl start pacemaker"
	_, e_err := exec.Command("bash", "-c", cmd).Output()
	if e_err != nil {
		fmt.Println(err)
	}
	fmt.Println("Before proceeding restart corosync and pacemaker service on both nodes after pacemaker setup is done and verify that cluster is formed with: crm status")

}


func PacemakerAdditional() {
	cmd := "crm configure property no-quorum-policy=ignore && crm configure property stonith-enabled=false"
	_, err := exec.Command("bash", "-c", cmd).Output()
	if err != nil {
		fmt.Println(err)
	}
}


func DrbdResources(resource_name, device, fs_type, directory string) {

	p_drbd_parts := []string{"crm configure primitive p_drbd_r0 ocf:linbit:drbd params drbd_resource=", resource_name, " op start interval=0s timeout=240s op stop interval=0s timeout=100s op monitor interval=31s timeout=20s role=Slave op monitor interval=29s timeout=20s role=Master && crm configure ms ms_drbd_r0 p_drbd_r0 meta master-max=1 master-node-max=1 clone-max=2 clone-node-max=1 notify=true"}
	p_drbd_cmd := strings.Join(p_drbd_parts, "")

	p_fs_parts := []string{"crm configure primitive p_fs_drbd1 ocf:heartbeat:Filesystem params device=", device, " directory=", directory, " fstype=", fs_type ," options=noatime,nodiratime op start interval=0 timeout=60s op stop interval=0 timeout=60s op monitor interval=20 timeout=40s && crm configure order drbd-before-fs inf: ms_drbd_r0:promote p_fs_drbd1:start && crm configure colocation fs-with-drbd inf: p_fs_drbd1 ms_drbd_r0:Master"}
	p_fs_cmd := strings.Join(p_fs_parts, "")

	commands := []string{p_drbd_cmd, p_fs_cmd}

	for _, c := range commands {
		_, err := exec.Command("bash", "-c", c).Output()
		if err != nil {
		    fmt.Println(err)
		}
	}
}

func NfsResources() {
      //Configure nfs service and exports

}
