import requests

url = '''https://bravosolutions.freshservice.com/api/v2/requesters?query="agente_fd: 'Sim'"'''
headers = {"Authorization": "Basic RkFza2J1R3M2TnNXSXJXSm8="}

freshservice_requesters = requests.get(url=url, headers=headers).json()['requesters']

with open("freshservice_req.txt", "w", encoding="utf-8") as req_database:
    req_database.write("{")

    for req in freshservice_requesters:
        if req['last_name'] is not None:
            req['first_name'] = req['first_name'] + " " + str(req['last_name'])

        req_database.write('"' + req["primary_email"] + '": ')
        new_req = str(req).replace("'", '"') \
            .replace("first_name", "name") \
            .replace("mobile_phone_number", "mobile") \
            .replace("work_phone_number", "phone") \
            .replace("None", '"None"') \
            .replace("True", '"True"') \
            .replace("False", '"False"') \
            .replace('src="', "src='") \
            .replace('.png"', ".png'")

        req_database.write(new_req)

        if req != freshservice_requesters[-1]:
            req_database.write(",\n")

    req_database.write("}")
