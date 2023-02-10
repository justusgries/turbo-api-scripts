import requests
import urllib3
import json
import sys

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
cloud_accounts = s.get(turboURI+"/search", headers=headers, verify=False, params={"scopes": "Market", "types": "BusinessAccount", "environment_type" : "CLOUD"})

with open('account_list.json', 'wb') as outf:
    outf.write(cloud_accounts.content) 
#print("Get call for cloud account list")
#print("\n")
#accounts = cloud_accounts.content.decode("utf8")
#print(accounts)


# Get all scale actions associated with each account
action_payload = {
"uuid":["Market"],
"groupBy":["businessUnit"],
"types":["Workload"],
"environmentType":"CLOUD"
}
post_action_response = s.post(turboURI+"/supplychains/stats", headers=headers, data = json.dumps(action_payload), verify=False)

with open('account_actions.json', 'wb') as outf:
    outf.write(post_action_response.content)
#print("Get all actions for each account")
#print("\n")
#actions = post_action_response.content.decode("utf8")
#print(actions)

savings_payload = {
    "actionInput":
        {
            "groupBy":["businessUnit"],"environmentType":"CLOUD","actionTypeList":["DEACTIVATE","RESIZE","ACTIVATE","SUSPEND","ALLOCATE","START","SCALE","RECONFIGURE","MOVE","DELETE","NONE","PROVISION"]
        },
    "scopes":["Market"]
}
#Get all the savings opportunity by accounts
savings_list = s.post(turboURI+"/actions/stats", headers=headers, data = json.dumps(savings_payload), verify=False)

with open('account_savings.json', 'wb') as outf:
    outf.write(savings_list.content)
#print("Get savings opportunity for each account")
#print("\n")
#savings = savings_list.content.decode("utf8")
#print(savings_list)

