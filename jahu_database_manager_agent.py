import requests
import json

# ESSE SNIPPET ANTECEDERÁ O DATABASE_MANAGER_REQ

url = 'https://bravosolutions.freshservice.com/api/v2/agents?per_page=100&page=1'
headers = {"Authorization": "Basic RkFza2J1R3M2TnNXSXJXSm8="}

freshservice_agents = requests.get(url=url, headers=headers)
freshservice_agents = freshservice_agents.json()['agents']
print(freshservice_agents)

with open("freshservice_agents.txt", "w", encoding="utf-8") as agents_database:
    agents_database.write("{")

    for agent in freshservice_agents:
        if agent['last_name'] is not None:
            agent['first_name'] = agent['first_name'] + " " + str(agent['last_name'])

        agent['tag'] = ['Agente']

        agents_database.write('"' + agent["email"] + '": ')
        new_agent = str(agent).replace("'", '"')\
            .replace("first_name", "name")\
            .replace("mobile_phone_number", "mobile")\
            .replace("work_phone_number", "phone")\
            .replace("None", '"None"')\
            .replace("True", '"True"')\
            .replace("False", '"False"')\
            .replace('src="', "src='")\
            .replace('.png"', ".png'")

        agents_database.write(new_agent)

        if agent != freshservice_agents[-1]:
            agents_database.write(",\n")

    agents_database.write("}")
