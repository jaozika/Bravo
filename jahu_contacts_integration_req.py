import requests
import json
import ast


# GERA UMA TABELA PARA COMPARAÇÃO
def gera_tabela_verificacao(contato):
    tabela_retorno = {}

    for campo in contato:
        tabela_retorno[campo] = contato[campo]

    return tabela_retorno


# contact_info --> {'active': False, 'address': None, 'custom_fields': {'tarefas': None},...}
# database --> {"bruno@bravosolutions.com.br": {"active": True, "address": None, "background_information": None, ....}}
def verifica_contato(contact_info, database):
    # Retorna um array de tuplas, onde a posição 0 de cada tupla é o nome do campo a ser mudado e a posição 1 é o valor

    ignore_keys = ["id", "active", "language", "created_at", "updated_at", "custom_fields"]
    contact_email = contact_info['contact']['email']
    return_table = []

    if contact_email in database:
        for key in contact_info['contact']:
            if key in database[contact_email] and key not in ignore_keys:
                if contact_info['contact'][key] != database[contact_email][key]:
                    return_table.append((key, database[contact_email][key]))
    else:
        print("Contato não registrado na base!")

    return return_table if len(return_table) > 0 else False


def gera_request_body(table):
    result = {}

    for tup in table:
        result[tup[0]] = tup[1]

    return result


url = '''https://bravosolutionshelp.freshdesk.com/api/v2/agents'''
headers = {"Authorization": "Basic akxWVlR0ck56M2hMTVJaVlE4RWw="}

freshdesk_agents = requests.get(url, headers=headers).json()

# REMOVE ASSINATURAS
for agent in freshdesk_agents:
    agent['signature'] = ""

freshdesk_agents = str(freshdesk_agents).replace("None", '"None"')\
    .replace("'", '"')\
    .replace("True", '"True"')\
    .replace("False", '"False"')

freshdesk_agents = json.loads(freshdesk_agents)

with open("freshservice_req.txt", "r", encoding="utf-8") as database_file:
    data = database_file.read()
    database_info = ast.literal_eval(data)

    for agent in freshdesk_agents:
        freshdesk_id = agent['id']

        ver_result = verifica_contato(agent, database_info)
        print(ver_result)

        if ver_result:
            url = 'https://bravosolutionshelp.freshdesk.com/api/v2/agents/' + str(freshdesk_id)
            headers = {"Authorization": "Basic akxWVlR0ck56M2hMTVJaVlE4RWw=", "Content-Type": "application/json"}
            body = gera_request_body(ver_result)

            r = requests.put(url=url, data=json.dumps(body), headers=headers)
            print(r)
            print(r.json())
        else:
            print("Contato já atualizado!")
