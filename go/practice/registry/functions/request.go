package functions

import (
	"fmt"
	"net/http"
	"io/ioutil"
	"crypto/tls"
	"encoding/json"
	"os"
	"strings"
	"os/exec"
	"bufio"
)

type Repos struct {
	Repo []string `json:"repositories"`
}

func Catalog(url, user, pass string) {
	url = fmt.Sprintf("https://%s/v2/_catalog", url)
	transp := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true} }
	client := &http.Client{Transport: transp}

	request, _ := http.NewRequest("GET", url, nil)
	request.SetBasicAuth(user, pass)
	request.Header.Add("Accept", "application/vnd.docker.distribution.manifest.v2+json")

	response, err := client.Do(request)
	if err != nil {
		fmt.Println(err)
	}
	defer response.Body.Close()

	text ,r_err := ioutil.ReadAll(response.Body)
	if r_err != nil {
		fmt.Println(r_err)
	}

	var repository Repos

	d_err := json.Unmarshal(text, &repository)
	if d_err != nil {
		fmt.Println(d_err)
	}

	for _, i := range repository.Repo {
		fmt.Println(i)
	}
}

type Tags struct {
	Name string `json:"name"`
	Tag []string `json:"tags"`
}

func GetTags(url, user, pass, repo string) {
        url = fmt.Sprintf("https://%s/v2/%s/tags/list", url, repo)
        transp := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true} }
        client := &http.Client{Transport: transp}

        request, _ := http.NewRequest("GET", url, nil)
        request.SetBasicAuth(user, pass)
        request.Header.Add("Accept", "application/vnd.docker.distribution.manifest.v2+json")

        response, err := client.Do(request)
        if err != nil {
                fmt.Println(err)
        }
        defer response.Body.Close()

        text ,r_err := ioutil.ReadAll(response.Body)
        if r_err != nil {
                fmt.Println(r_err)
        }

        var repo_tags Tags

        d_err := json.Unmarshal(text, &repo_tags)
        if d_err != nil {
                fmt.Println(d_err)
        }

	fmt.Println("Repo Name:", repo_tags.Name)
	fmt.Println("Tags:")
        for _, i := range repo_tags.Tag {
		fmt.Println("-------")
                fmt.Println(i)
        }
}


func DeleteTag(url, user, pass, repo, tag string) {
	digest_url := fmt.Sprintf("https://%s/v2/%s/manifests/%s", url, repo, tag)
        transp := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true} }
        client := &http.Client{Transport: transp}

        request, _ := http.NewRequest("GET", digest_url, nil)
        request.SetBasicAuth(user, pass)
        request.Header.Add("Accept", "application/vnd.docker.distribution.manifest.v2+json")

        response, err := client.Do(request)
        if err != nil {
                fmt.Println(err)
        }

	digest := response.Header["Docker-Content-Digest"][0]
	defer response.Body.Close()

	del_url := fmt.Sprintf("https://%s/v2/%s/manifests/%s", url, repo, digest)
	transp2 := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true} }
        client2 := &http.Client{Transport: transp2}

        request2, _ := http.NewRequest("DELETE", del_url, nil)
        request2.SetBasicAuth(user, pass)
        request2.Header.Add("Accept", "application/vnd.docker.distribution.manifest.v2+json")

	response2, delete_err := client2.Do(request2)
        if delete_err != nil {
                fmt.Println(delete_err)
        }
	defer response2.Body.Close()

	_, r_err := ioutil.ReadAll(response2.Body)
	if r_err != nil {
		fmt.Println(r_err)
	}

	fmt.Sprintf("Successfully deleted tag: %s/%s", repo, tag )
}


func GenerateConfig() {
	reader := bufio.NewReader(os.Stdin)
	fmt.Print("Registry domain: ")
	url, _ := reader.ReadString('\n')
        fmt.Print("Registry user: ")
	user, _ := reader.ReadString('\n')
        fmt.Print("Registry base64 encoded password: ")
	pass, _ := reader.ReadString('\n')

	url = strings.TrimSpace(url)
	user = strings.TrimSpace(user)
	pass = strings.TrimSpace(pass)

	content := fmt.Sprintf(`
{
	"url": "%s",
	"user": "%s",
	"password": "%s"
}
`, url, user, pass)
	path := ".registry.json"

	_ = ioutil.WriteFile(path, []byte(content), 0600)
}


type Conf struct {
	Url string `json:"url"`
	User string `json:"user"`
	Pass string `json:"password"`
}

func Config() Conf {
	var config Conf
	file, err := os.Open(".registry.json")
	if err != nil {
		GenerateConfig()
	}

	jsonParse := json.NewDecoder(file)
	jsonParse.Decode(&config)
	return config
}

func GetPassword(hash string) (pass string) {
	cmd := fmt.Sprintf("echo '%s' | base64 -d", hash)
	out, err := exec.Command("bash", "-c", cmd).Output()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	return string(out)
}
