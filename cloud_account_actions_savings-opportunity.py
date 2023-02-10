import requests
import urllib3
import json
import sys
import time
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    instance = str(sys.argv[1])
    turbouser = str(sys.argv[2])
    turbopassword = str(sys.argv[3])
#    entity = str(sys.argv[4])
#    searchTerm = str(sys.argv[5])
except IndexError:
    raise SystemExit("Usage: <instance> <turbouser> <turbopassword> <entity> <searchTerm>")


#define constants 
turboInstance = 'https://' + instance
loginURI = turboInstance + '/vmturbo/rest/login'
turboURI = turboInstance + '/api/v3'
headers = {'content-type': 'application/json'} 

#setup wiring to make authentication request for login
payload = {'username': turbouser,'password': turbopassword}
s = requests.Session()
response = s.post(loginURI, data = payload, verify=False)

if response.status_code == 200:
    print("Connected to API\n")
    content = response.content.decode("utf8")
    js = json.loads(content)
    authToken = js["authToken"]
else:
    print("API Call Failed:", response.status_code, "\n", response.text)
    sys.exit("ERROR, quiting script, see error above")


#Dump cloud account UUID
cloud_accounts_response = s.get(turboURI+"/search", headers=headers, verify=False, params={"scopes": "Market", "types": "BusinessAccount", "environment_type" : "CLOUD"})
cloud_account_list = json.loads(cloud_accounts_response.text)

# Get all scale actions associated with each account
action_payload = {
"uuid":["Market"],
"groupBy":["businessUnit"],
"types":["Workload"],
"environmentType":"CLOUD"
}
#Get all the savings opportunity by accounts
savings_payload = {
    "actionInput":
        {
            "groupBy":["businessUnit"],"environmentType":"CLOUD","actionTypeList":["DEACTIVATE","RESIZE","ACTIVATE","SUSPEND","ALLOCATE","START","SCALE","RECONFIGURE","MOVE","DELETE","NONE","PROVISION"]
        },
    "scopes":["Market"]
}
savings_list_response = s.post(turboURI+"/actions/stats", headers=headers, data = json.dumps(savings_payload), verify=False)
savings_list = json.loads(savings_list_response.text)

date_outputoutput = datetime.datetime.now().strftime("%Y_%m_%d-%I%M%S_%p")

#Use each account UUID to output display name, number of workloads, number of actions, and potential savings
for accounts in cloud_account_list:
    print("Processing account " + accounts["displayName"])
    uuid = accounts["uuid"]
    display_name = accounts["displayName"]
    workloads = accounts["membersCount"]
    for stats in savings_list[0]["stats"][0]["statistics"]:
        #print(stats["filters"][0])
        if stats["filters"][0]["value"] == uuid and stats["name"] == "numActions":
            action_count = stats["value"]
        elif stats["filters"][0]["value"] == uuid and stats["name"] == "costPrice" and stats["filters"][1]["value"] == "savings":
            potential_savings = 730*stats["value"]

    top_account_output = {
        "uuid":uuid,
        "account name:":display_name,
        "workloads":str(workloads),
        "action_count":str(action_count),
        "savings":str(potential_savings)
    }
    with open('top-accounts-output' + date_outputoutput + '.json', 'a') as outf:
        outf.write(json.dumps(top_account_output))
