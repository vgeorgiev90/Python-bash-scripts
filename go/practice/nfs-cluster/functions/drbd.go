package functions

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"text/template"
)

type Drbdconfigs struct {
	Resource_name string
	Device        string
	Disk          string
	Host1 struct {
		Hostname string
		Ip       string
	}

	Host2 struct {
		Hostname string
		Ip       string
	}
}

func Install() {
	cmd := "apt-get install ntp drbd8-utils pacemaker -y"
	cmd2 := "systemctl enable ntp; systemctl start ntp; systemctl disable drbd;"

	commands := []string{cmd, cmd2}
	for _, c := range commands {
		_, err := exec.Command("bash", "-c", c).Output()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
	}

}

func ConfigureDrbd(directory, resource_name, device, disk string, hostnames, ips []string) {
	if _, err := os.Stat(directory); os.IsNotExist(err) {
           os.Mkdir(directory, 0750)
        }

	t, _ := template.New("drbd").Parse(`
resource {{ .Resource_name }} {
 protocol C;
 device {{ .Device }};
 disk {{ .Disk }};
 meta-disk internal;
 on {{ .Host1.Hostname }} {
  address {{ .Host1.Ip }}:7788;
 }
 on {{ .Host2.Hostname }} {
  address {{ .Host2.Ip }}:7788;
 }
}
`)

	var values Drbdconfigs
	values.Resource_name = resource_name
	values.Device = device
	values.Disk = disk
	values.Host1.Hostname = hostnames[0]
	values.Host1.Ip = ips[0]
	values.Host2.Hostname = hostnames[1]
	values.Host2.Ip = ips[1]

	path := []string{"/etc/drbd.d/", resource_name, ".res"}
	f, err := os.Create(strings.Join(path, ""))
	if err != nil {
		fmt.Println(err)
	}

	template_err := t.Execute(f, values)
	if template_err != nil {
		fmt.Println(template_err)
	}

	cmd_args1 := []string{"drbdadm create-md", values.Resource_name, "&&", "drbdadm up", values.Resource_name}
	cmd1 := strings.Join(cmd_args1, " ")

	out, err := exec.Command("bash", "-c", cmd1).Output()
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println(string(out))
}

func InitDrbd(resource_name, device ,fs_type string) {


	cmd1_args := []string{"drbdadm -- --clear-bitmap new-current-uuid ",resource_name, "/0"}
	cmd1 := strings.Join(cmd1_args, "")

	cmd2_args := []string{"drbdadm primary ", resource_name}
	cmd2 := strings.Join(cmd2_args, "")

	cmd3_args := []string{"mkfs.", fs_type," ",device}
	cmd3 := strings.Join(cmd3_args, "")

	cmd4_args := []string{"drbdadm secondary ", resource_name}
	cmd4 := strings.Join(cmd4_args, "")

	cmd_list := []string{cmd1, cmd2, cmd3, cmd4}
	for _, cmd := range cmd_list {
	_, err := exec.Command("bash", "-c", cmd).Output()
	if err != nil {
		fmt.Println(err)
	}
}
}
