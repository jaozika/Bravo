import requests
import json
import ast

UPDATED_CONTACTS = []
DEPARTMENTS_GROUPS_MAPPING = {'Atendimento': (15000219739, 63000246205),
                              'Desenvolvimento': (15000034190, 63000246206),
                              'Financeiro': (15000034193, 63000246207),
                              'IT': (15000034196, 63000246208),
                              'Operations': (15000034195, 63000246209),
                              'RH': (15000034194, 63000246210),
                              'Sales': (15000034191, 63000246211),
                              'Suporte ao cliente': (15000034192, 63000246212)}


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

    ignore_keys = ["id", "active", "language", "created_at", "updated_at", "time_zone", "custom_fields"]
    contact_email = contact_info['email']
    return_table = []

    if contact_email in database:
        for key in contact_info:
            if key in database[contact_email] and key not in ignore_keys:
                if contact_info[key] != database[contact_email][key]:
                    return_table.append((key, database[contact_email][key]))
    else:
        print("Contato - " + contact_email + " - não consta na base de dados!")

    UPDATED_CONTACTS.append(contact_email)

    return return_table if len(return_table) > 0 else False


def gera_request_body(table):
    result = {}

    for tup in table:
        result[tup[0]] = tup[1]

    return result


def create_contact_freshdesk(contact_info):
    email = contact_info['email']
    name = contact_info['name']
    mobile = contact_info['mobile']
    address = contact_info['address']
    language = contact_info['language']
    time_zone = contact_info['time_zone']

    fd_headers = {"Authorization": "Basic akxWVlR0ck56M2hMTVJaVlE4RWw=", "Content-Type": "application/json"}

    if len(contact_info['department_ids']) > 0:
        department_id = contact_info['department_ids'][0]

        for department in DEPARTMENTS_GROUPS_MAPPING:
            if DEPARTMENTS_GROUPS_MAPPING[department][0] == department_id:
                department_name = department

                contact_body = {'email': email, 'name': name, 'address': address,
                                'language': language, 'time_zone': time_zone,
                                'tags': ['Agente'], 'mobile': mobile,
                                'custom_fields': {'grupo_no_freshservice': department_name}}

                agent_creation_result = requests.post("https://bravosolutionshelp.freshdesk.com/api/v2/contacts",
                                                      headers=fd_headers,
                                                      data=json.dumps(contact_body)).json()

                return agent_creation_result
    else:
        contact_body = {'email': email, 'name': name, 'address': address,
                        'tags': ['Agente'], 'mobile': mobile,
                        'language': language, 'time_zone': time_zone}

        agent_creation_result = requests.post("https://bravosolutionshelp.freshdesk.com/api/v2/contacts",
                                              headers=fd_headers,
                                              data=json.dumps(contact_body)).json()

        return agent_creation_result


url = '''https://bravosolutionshelp.freshdesk.com/api/v2/search/contacts?query="tag:'Agente'"'''
headers = {"Authorization": "Basic akxWVlR0ck56M2hMTVJaVlE4RWw="}

freshdesk_contacts_filtered = requests.get(url=url, headers=headers)

freshdesk_contacts_filtered = freshdesk_contacts_filtered.json()['results']
freshdesk_contacts_filtered = str(freshdesk_contacts_filtered).replace("None", '"None"')\
    .replace("'", '"')\
    .replace("True", '"True"')\
    .replace("False", '"False"')

print("FRESHDESK CONTACTS" + str(freshdesk_contacts_filtered) + "\n")
freshdesk_contacts_filtered = json.loads(freshdesk_contacts_filtered)

with open("freshservice_agents.txt", "r", encoding="utf-8") as database_file:
    data = database_file.read()
    fs_agents_info = ast.literal_eval(data)

    for contact in freshdesk_contacts_filtered:
        freshdesk_id = contact['id']

        ver_result = verifica_contato(contact, fs_agents_info)

        if ver_result:
            url = 'https://bravosolutionshelp.freshdesk.com/api/v2/contacts/' + str(freshdesk_id)
            headers = {"Authorization": "Basic akxWVlR0ck56M2hMTVJaVlE4RWw=", "Content-Type": "application/json"}
            body = gera_request_body(ver_result)

            r = requests.put(url=url, data=json.dumps(body), headers=headers)
            print(r)
        else:
            print("Contato já atualizado!")

    print("\nCONTATOS ATUALIZADOS: " + str(UPDATED_CONTACTS) + "\n")

    for contact in fs_agents_info:
        if contact not in UPDATED_CONTACTS:
            created_contact = create_contact_freshdesk(fs_agents_info[contact])
            print(created_contact)
