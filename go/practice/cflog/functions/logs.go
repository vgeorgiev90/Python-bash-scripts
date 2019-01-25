package functions

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"
	"strings"
)

func Logs(date string, hour int) {
	//Create an http client
	client := &http.Client{}

	api_url := "https://api.cloudflare.com/client/v4/zones/ZONE_ID/logs/received?"
	mail := "cf-mail"
	key := "cf-key"

	var hour2 int
	var date2 string = date
	//Get the hour and add +1 as this is the maximum time period for the cf log api
	if hour == 23 {
		hour2 = 00
		days := strings.Split(date2, "-")
		day := days[2]
		int_day, _ := strconv.Atoi(day)
		int_day = int_day + 1
		str_day := strconv.Itoa(int_day)

		days2 := []string{days[0], days[1], str_day}
		date2 = strings.Join(days2, "-")
	} else {
		hour2 = hour + 1
	}

	str_hour := strconv.Itoa(hour)
	str_hour2 := strconv.Itoa(hour2)

	fields := "CacheCacheStatus,CacheResponseBytes,CacheResponseStatus,CacheTieredFill,ClientASN,ClientCountry,ClientDeviceType,ClientIP,ClientIPClass,ClientRequestBytes,ClientRequestHost,ClientRequestMethod,ClientRequestPath,ClientRequestProtocol,ClientRequestReferer,ClientRequestURI,ClientSSLProtocol,EdgeColoID,EdgePathingOp,EdgePathingSrc,EdgePathingStatus,EdgeRateLimitAction,EdgeRateLimitID,EdgeRequestHost,EdgeResponseStatus,EdgeServerIP,OriginIP,OriginResponseStatus,OriginResponseTime,ParentRayID,RayID,SecurityLevel,WAFAction,WAFFlags,WAFMatchedVar,WAFProfile,WAFRuleID,WAFRuleMessage,"
	
	url_parts := []string{api_url, "start=", date, "T", str_hour, ":00:00Z", "&end=", date2, "T", str_hour2, ":00:00Z", "&fields=", fields}
	url := strings.Join(url_parts, "")

	//Create request and add auth headers
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		panic(err)
	}

	req.Header.Add("X-Auth-Email", mail)
	req.Header.Add("X-Auth-Key", key)
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}

	defer resp.Body.Close()

	text, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}

	fmt.Println(string(text))
}
