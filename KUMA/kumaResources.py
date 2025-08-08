from kumaPublicApiV3 import Kuma
import json
import argparse
import sys

def action_update_collectors(kuma, name, kind, id):
    page = 1
    name = name
    kind_collector = kind
    id_normalizer = id

    # ------------------ поиск коллекторов по названию
    print("\n")
    print(f"[INFO] Запуск поиска ресурсов с типом {kind_collector} по названию {name}...\n")
    collectors_list = kuma.resources_search(page=page, name=name, kind=kind_collector)
    #print(collectors_list)

    collectors_filtered = [
        {
            'id': collector['id'],
            'kind': collector['kind'],
            'name': collector['name'],
            'tenantID': collector['tenantID'],
        }
        for collector in collectors_list
    ]
    print("Найденные ресурсы:\n")
    
    if collectors_filtered:
        print("Найденные ресурсы:\n")
        for collector in collectors_filtered:
            print(
                f"ID: {collector['id']}\n"
                f"Type: {collector['kind']}\n"
                f"Name: {collector['name']}\n"
                f"Tenant: {collector['tenantID']}\n"
                "----------------------------------"
            )
    else:
        print("Коллекторы не найдены, список пустой")
        return

    # ----------------- получение и изменение ресурса нормализатор
    def get_filtered_normalizer(kind, id):
        normalizer = kuma.get_kind_resources(kind, id)

        modified_normalizer = normalizer.copy()

        filtered_normalizer = {}

        filtered_normalizer['normalizer'] = {
            'id': modified_normalizer.get('payload', {}).get('id', ''),
            'name': modified_normalizer.get('payload', {}).get('name', ''),
            'kind': modified_normalizer.get('payload', {}).get('kind', ''),
            'expressions': modified_normalizer.get('payload', {}).get('expressions', '')
        }
        return filtered_normalizer

    # ---------------- получение и изменение ресурса коллектора
    def get_and_modified_collector(kind_collector, id_collector, id_normalizer):
        resource = kuma.get_kind_resources(kind_collector, id_collector)

        modified_data = resource.copy()

        # изменение ресурса коллектора 
        filtered_collector = {
            'id': modified_data.get('id',''),
            'tenantID': modified_data.get('tenantID',''),
            'kind': modified_data.get('kind',''),
            'name': modified_data.get('name',''),
            'description': modified_data.get('description',''),
            'version': modified_data.get('version','')
        }

        destinations_cleaned = [
            {
                'id': d['id'],
                'name': d['name'],
                'kind': d['kind'],
                'connection': {
                    'kind': d['connection'].get('kind'),
                    'urls': d['connection'].get('urls', [])
                }
            }
            for d in modified_data.get('payload', {}).get('destinations', [])
        ]


        connector = modified_data.get('payload', {}).get('connector', {})
        connector_cleaned = {
                        'id': connector.get('id'),
                        'name': connector.get('name'),
                        'kind': connector.get('kind'),
                        'delimiter': connector.get('delimiter'),
                        'connections': [
                    {
                                    'kind': conn.get('kind'),
                                    'urls': conn.get('urls', [])
                            }
                    for conn in connector.get('connections', [])
                ]
        }

        #print(connector_cleaned)
        normalizers = modified_data.get('payload', {}).get('normalizers', [])
        normalizers_cleaned = [
            {'normalizer': item['normalizer']}
            for item in normalizers
        ]

        enrichment = modified_data.get('payload', {}).get('enrichment', [])
        for item in enrichment:
            filter_dict = item.get('filter')
            if filter_dict is not None:
            # Проверяем, что у Правила обогащения в поле filter пустые id и name
                if filter_dict.get('id', '') == '' and filter_dict.get('name', '') == '':
            # Удаляем ключ 'filter' из элемента
                    item.pop('filter')

        filtered_collector['payload'] = {
            'id': modified_data.get('payload', {}).get('id', ''),
            'name': modified_data.get('payload', {}).get('name', ''),
            'connector': connector_cleaned,
            'normalizers': normalizers_cleaned,
            'destinations': destinations_cleaned,
            'filters': modified_data.get('payload', {}).get('filters', ''),
            'enrichment': enrichment,
            'rules': modified_data.get('payload', {}).get('rules', ''),
            'workers': modified_data.get('payload', {}).get('workers', ''),
            'debug': modified_data.get('payload', {}).get('debug', ''),
            'shared': modified_data.get('payload', {}).get('shared', ''),
            'accountsConfig': modified_data.get('payload', {}).get('accountsConfig', ''),
            'sourceID': modified_data.get('payload', {}).get('sourceID', ''),
            'eventSourceIdentity': modified_data.get('payload', {}).get('eventSourceIdentity', ''),
            'banned': modified_data.get('payload', {}).get('banned', ''),
        }

        filtered_collector['payload']['id'] = ''
        filtered_collector['payload']['name'] = ''
        filtered_collector['payload']['normalizers'][0] = get_filtered_normalizer('normalizer', id_normalizer)

        return filtered_collector

    def validate_collectors_with_new_normalizers(collectors_filtered, id_normalizer, excluded_tenant_ids):
        for collector in collectors_filtered:
            if collector['tenantID'] not in excluded_tenant_ids:
                current_id = collector["id"]
                current_kind = collector["kind"]
                collector_new = get_and_modified_collector(current_kind, current_id, id_normalizer)
                #json_str = json.dumps(collector_new, indent=4, ensure_ascii=False)
                #with open('test.txt', "w", encoding="utf-8") as f:
                #    f.write(json_str)
                print(f"[INFO] Коллектору {collector_new['name']} изменен нормализатор!")
                print(f"[INFO] Запуск валидации ресурса {collector_new['name']}...")
                answer = kuma.resources_validate(current_kind, collector_new)
                print(f"Получен ответ: {answer}\n")

    def validate_and_update_collectors_with_new_normalizers(collectors_filtered, id_normalizer, excluded_tenant_ids):
        for collector in collectors_filtered:
            if collector['tenantID'] not in excluded_tenant_ids:
                current_id = collector["id"]
                current_kind = collector["kind"]
                collector_new = get_and_modified_collector(current_kind, current_id, id_normalizer)
                print(f"[INFO] Коллектору {collector_new['name']} изменен нормализатор!")
                print(f"[INFO] Запуск валидации ресурса {collector_new['name']}...")
                answer = kuma.resources_validate(current_kind, collector_new)
                print(f"Получен ответ: {answer}\n")
                if answer == '[Status 204: OK] Resource is valid!':
                    print(f"[INFO] Запуск обновления ресурса {collector_new['name']}...")
                    answer = kuma.put_kind_resources(current_kind, current_id, collector_new)
                    print(f"Получен ответ: {answer}\n")


    excluded_tenant_ids = ['5d84b79c-b490-4acd-8f5b-ea6244254f28', 'f8a3b634-8a92-4cb0-93ce-819940ff6e2f'] #вставить id теннатов если нужно исключить
    new_normalizer = kuma.get_kind_resources('normalizer', id_normalizer)
    print("\n")
    print(f"[INFO] Валидация нормализатора {new_normalizer['name']} на всех коллекторах...\n")
    validate_collectors_with_new_normalizers(collectors_filtered, id_normalizer, excluded_tenant_ids)

    print(f"[INFO] Валидация и изменение нормализатора {new_normalizer['name']} на всех коллекторах...\n")
    validate_and_update_collectors_with_new_normalizers(collectors_filtered, id_normalizer, excluded_tenant_ids)

def action_create_collectors(kuma, id, kind, name):
    def get_filtered_normalizer(kind, id):
        normalizer = kuma.get_kind_resources(kind, id)

        modified_normalizer = normalizer.copy()

        filtered_normalizer = {}

        filtered_normalizer['normalizer'] = {
            'id': modified_normalizer.get('payload', {}).get('id', ''),
            'name': modified_normalizer.get('payload', {}).get('name', ''),
            'kind': modified_normalizer.get('payload', {}).get('kind', '')
        }
        return filtered_normalizer
    
    def get_and_filtered_example_collector(kind_collector, id_collector):
        resource = kuma.get_kind_resources(kind_collector, id_collector)

        modified_data = resource.copy()
        
        # изменение ресурса коллектора 
        filtered_collector = {
            key: modified_data[key] for key in ['id', 'tenantID', 'kind', 'name', 'description']
        }

        destinations_cleaned = [
            {
                'id': d['id'],
                'name': d['name'],
                'kind': d['kind'],
                'connection': {
                    'kind': d['connection'].get('kind'),
                    'urls': d['connection'].get('urls', [])
                }
            }
            for d in modified_data.get('payload', {}).get('destinations', [])
        ]


        connector = modified_data.get('payload', {}).get('connector', {})
        connector_cleaned = {
                        'id': connector.get('id'),
                        'name': connector.get('name'),
                        'kind': connector.get('kind'),
                        'connections': [
                    {
                                    'kind': conn.get('kind'),
                                    'urls': conn.get('urls', [])
                            }
                    for conn in connector.get('connections', [])
                ]
        }
      
        normalizers = modified_data.get('payload', {}).get('normalizers', [])
        normalizers_cleaned = [
            {'normalizer': item['normalizer']}
            for item in normalizers
        ]
        
        id_normalizer = normalizers_cleaned[0]['normalizer']['id']
        
        filtered_collector['payload'] = {
            'id': modified_data.get('payload', {}).get('id', ''),
            'name': modified_data.get('payload', {}).get('name', ''),
            'normalizers': normalizers_cleaned,
            'connector': connector_cleaned,
            'destinations': destinations_cleaned
        }

        filtered_collector['payload']['id'] = ''
        filtered_collector['payload']['name'] = ''
        filtered_collector['payload']['normalizers'][0] = get_filtered_normalizer('normalizer', id_normalizer)

        return filtered_collector

        # --------------- получение id нужных тенантов
    
    def validate_and_create_new_collectors(collector_new, tenant_name):
        current_kind = collector_new["kind"]
        current_tenant = tenant_name
        print(f"[INFO] Создается новый коллектор {collector_new['name']} в тенанте {current_tenant}")
        print(f"[INFO] Запуск валидации ресурса {collector_new['name']}...")
        answer = kuma.resources_validate(current_kind, collector_new)
        print(f"Получен ответ: {answer}\n")
#        if answer == '[Status 204: OK] Resource is valid!':
#            print(f"[INFO] Запуск обновления ресурса {collector_new['name']}...")
#            answer = kuma.resources_create(current_kind, collector_new)
#            print(f"Получен ответ: {answer}\n")
    
    collector = get_and_filtered_example_collector(kind, id)
    
    original_list = kuma.get_tenants()

    tenants_mapping = {
        'tenant1Fullname': 'shortname1',
        'tenant2Fullname': 'shortname2'
    }

    target_tenants = [
        {
            'TenantID': item['id'], 
            'tenantName': tenants_mapping.get(item['name'], "UNKNOWN_TENANT")
        }
        for item in original_list
        if item['name'] != 'Shared' and item['id'] != collector['tenantID']
    ]


    for tenant in target_tenants:
        collector['tenantID'] = tenant['TenantID']
        collector['id'] = ''
        collector['name'] = f'{name} {tenant['tenantName']}'
        tenant_name = f'{tenant['tenantName']}'
        validate_and_create_new_collectors(collector, tenant_name)
   
def action_create_resource(kuma, kind, tenantID, tenantName, resource):
    resource['tenantID'] = tenantID
    resource['tenantName'] = tenantName
    print(f"[INFO] Запуск валидации ресурса {resource['name']}...")
    answer = kuma.resources_validate(kind, resource)
    print(f"Получен ответ: {answer}\n")
    if answer == '[Status 204: OK] Resource is valid!':
        print(f"[INFO] Запуск обновления ресурса {resource['name']}...")
        answer = kuma.resources_create(kind, resource)
        print(f"Получен ответ: {answer}\n")

def action_update_new_resource(kuma, name, kind, id): 
    page = 1
    name = name
    kind_collector = 'collector'
    kind_new_rule = kind
    id_new_rule = id

    # ------------------ поиск коллекторов по названию
    print("\n")
    print(f"[INFO] Запуск поиска ресурсов с типом {kind_collector} по названию {name}...\n")
    collectors_list = kuma.resources_search(page=page, name=name, kind=kind_collector)
    #print(collectors_list)

    collectors_filtered = [
        {
            'id': collector['id'],
            'kind': collector['kind'],
            'name': collector['name'],
            'tenantID': collector['tenantID'],
        }
        for collector in collectors_list
    ]
    if collectors_filtered:
        print("Найденные ресурсы:\n")
        for collector in collectors_filtered:
            print(
                f"ID: {collector['id']}\n"
                f"Type: {collector['kind']}\n"
                f"Name: {collector['name']}\n"
                f"Tenant: {collector['tenantID']}\n"
                "----------------------------------"
            )
    else:
        print("Коллекторы не найдены, список пустой")
        return
       
    
    # ----------------- получение и изменение ресурса enrichmentRule или filter
    def get_new_rule(kind, id):
        rule = kuma.get_kind_resources(kind, id)

        modified_rule = rule.copy()

        filtered_rule = modified_rule.get('payload', {})

        return filtered_rule

    # ---------------- получение и изменение ресурса коллектора
    def get_and_modified_collector(kind_collector, id_collector, id_new_rule):
        resource = kuma.get_kind_resources(kind_collector, id_collector)

        modified_data = resource.copy()

        # изменение ресурса коллектора 
        filtered_collector = {
            key: modified_data[key] for key in ['id', 'tenantID', 'kind', 'name', 'description','version']

        }

        destinations_cleaned = [
            {
                'id': d['id'],
                'name': d['name'],
                'kind': d['kind'],
                'connection': {
                    'kind': d['connection'].get('kind'),
                    'urls': d['connection'].get('urls', [])
                }
            }
            for d in modified_data.get('payload', {}).get('destinations', [])
        ]


        connector = modified_data.get('payload', {}).get('connector', {})
        connector_cleaned = {
                        'id': connector.get('id'),
                        'name': connector.get('name'),
                        'kind': connector.get('kind'),
                        'delimiter': connector.get('delimiter'),
                        'connections': [
                    {
                                    'kind': conn.get('kind'),
                                    'urls': conn.get('urls', [])
                            }
                    for conn in connector.get('connections', [])
                ]
        }
       
        normalizers = modified_data.get('payload', {}).get('normalizers', [])
        normalizers_cleaned = [
            {'normalizer': item['normalizer']}
            for item in normalizers
        ]
        
        normalizer = normalizers_cleaned[0]['normalizer'] 
        filtered_normalizer = {k: normalizer[k] for k in ("id", "name", "kind", "expressions") if k in normalizer}
        normalizers_cleaned[0]['normalizer'] = filtered_normalizer
        

        enrichment = modified_data.get('payload', {}).get('enrichment', [])
        for item in enrichment:
            filter_dict = item.get('filter')
            if filter_dict is not None:
            # Проверяем, что у Правила обогащения в поле filter пустые id и name
                if filter_dict.get('id', '') == '' and filter_dict.get('name', '') == '':
            # Удаляем ключ 'filter' из элемента
                    item.pop('filter')  

        filtered_collector['payload'] = {
            'id': modified_data.get('payload', {}).get('id', ''),
            'name': modified_data.get('payload', {}).get('name', ''),
            'connector': connector_cleaned,
            'normalizers': normalizers_cleaned,
            'destinations': destinations_cleaned,
            'filters': modified_data.get('payload', {}).get('filters', ''),
            'enrichment': enrichment,
            'rules': modified_data.get('payload', {}).get('rules', ''),
            'workers': modified_data.get('payload', {}).get('workers', ''),
            'debug': modified_data.get('payload', {}).get('debug', ''),
            'shared': modified_data.get('payload', {}).get('shared', ''),
            'accountsConfig': modified_data.get('payload', {}).get('accountsConfig', ''),
            'sourceID': modified_data.get('payload', {}).get('sourceID', ''),
            'eventSourceIdentity': modified_data.get('payload', {}).get('eventSourceIdentity', ''),
            'banned': modified_data.get('payload', {}).get('banned', ''),
        }

        filtered_collector['payload']['id'] = ''
        filtered_collector['payload']['name'] = ''

        if kind_new_rule == 'enrichmentRule':
            filtered_collector['payload']['enrichment'].append(get_new_rule('enrichmentRule', id_new_rule))
        elif kind_new_rule == 'filter':
            filtered_collector['payload']['filters'].append(get_new_rule('filter', id_new_rule))
        else: 
            print('Ошибка. Неподдерживаемый тип')

        return filtered_collector

    def validate_collectors_with_new_enrichment(collectors_filtered, id_new_rule):
        for collector in collectors_filtered:
            current_id = collector["id"]
            current_kind = collector["kind"]
            collector_new = get_and_modified_collector(current_kind, current_id, id_new_rule)
            # json_str = json.dumps(collector_new, indent=4, ensure_ascii=False)
            # with open('test.txt', "w", encoding="utf-8") as f:
            #     f.write(json_str)
            print(f"[INFO] Коллектору {collector_new['name']} добавлено новое правило!")
            print(f"[INFO] Запуск валидации ресурса {collector_new['name']}...")
            answer = kuma.resources_validate(current_kind, collector_new)
            print(f"Получен ответ: {answer}\n")

    def validate_and_update_collectors_with_new_enrichment(collectors_filtered, id_new_rule):
        for collector in collectors_filtered:
            current_id = collector["id"]
            current_kind = collector["kind"]
            collector_new = get_and_modified_collector(current_kind, current_id, id_new_rule)
            print(f"[INFO] Коллектору {collector_new['name']} добавлено новое правило!")
            print(f"[INFO] Запуск валидации ресурса {collector_new['name']}...")
            answer = kuma.resources_validate(current_kind, collector_new)
            print(f"Получен ответ: {answer}\n")
            if answer == '[Status 204: OK] Resource is valid!':
                print(f"[INFO] Запуск обновления ресурса {collector_new['name']}...")
                answer = kuma.put_kind_resources(current_kind, current_id, collector_new)
                print(f"Получен ответ: {answer}\n")


    new_rule = kuma.get_kind_resources(kind_new_rule, id_new_rule)
    print("\n")
    print(f"[INFO] Валидация нового ресурса {new_rule['name']} на всех коллекторах...\n")
    validate_collectors_with_new_enrichment(collectors_filtered, id_new_rule)

    print(f"[INFO] Валидация и добавления нового ресурса {new_rule['name']} на всех коллекторах...\n")
    validate_and_update_collectors_with_new_enrichment(collectors_filtered, id_new_rule)

def action_delete_enrichment(kuma, name, kind, id):
    page = 1
    name = name
    kind_collector = kind
    id_enrichment = id

    # ------------------ поиск коллекторов по названию
    print("\n")
    print(f"[INFO] Запуск поиска ресурсов с типом {kind_collector} по названию {name}...\n")
    collectors_list = kuma.resources_search(page=page, name=name, kind=kind_collector)
    #print(collectors_list)

    collectors_filtered = [
        {
            'id': collector['id'],
            'kind': collector['kind'],
            'name': collector['name'],
            'tenantID': collector['tenantID'],
        }
        for collector in collectors_list
    ]
    print("Найденные ресурсы:\n")
    for collector in collectors_filtered:
        print(
            f"ID: {collector['id']}\n"
            f"Type: {collector['kind']}\n"
            f"Name: {collector['name']}\n"
            f"Tenant: {collector['tenantID']}\n"
            "-----------------------"
        )

    # ---------------- получение и изменение ресурса коллектора
    def get_and_modified_collector(kind_collector, id_collector, id_enrichment):
        resource = kuma.get_kind_resources(kind_collector, id_collector)

        modified_data = resource.copy()

        # изменение ресурса коллектора 
        filtered_collector = {
            key: modified_data[key] for key in ['id', 'tenantID', 'kind', 'name', 'description','version']

        }

        destinations_cleaned = [
            {
                'id': d['id'],
                'name': d['name'],
                'kind': d['kind'],
                'connection': {
                    'kind': d['connection'].get('kind'),
                    'urls': d['connection'].get('urls', [])
                }
            }
            for d in modified_data.get('payload', {}).get('destinations', [])
        ]


        connector = modified_data.get('payload', {}).get('connector', {})
        connector_cleaned = {
                        'id': connector.get('id'),
                        'name': connector.get('name'),
                        'kind': connector.get('kind'),
                        'delimiter': connector.get('delimiter'),
                        'connections': [
                    {
                                    'kind': conn.get('kind'),
                                    'urls': conn.get('urls', [])
                            }
                    for conn in connector.get('connections', [])
                ]
        }
       
        normalizers = modified_data.get('payload', {}).get('normalizers', [])
        normalizers_cleaned = [
            {'normalizer': item['normalizer']}
            for item in normalizers
        ]


        filtered_collector['payload'] = {
            'id': modified_data.get('payload', {}).get('id', ''),
            'name': modified_data.get('payload', {}).get('name', ''),
            'connector': connector_cleaned,
            'normalizers': normalizers_cleaned,
            'destinations': destinations_cleaned,
            'filters': modified_data.get('payload', {}).get('filters', ''),
            'enrichment': modified_data.get('payload', {}).get('enrichment', ''),
            'rules': modified_data.get('payload', {}).get('rules', ''),
            'workers': modified_data.get('payload', {}).get('workers', ''),
            'debug': modified_data.get('payload', {}).get('debug', ''),
            'shared': modified_data.get('payload', {}).get('shared', ''),
            'accountsConfig': modified_data.get('payload', {}).get('accountsConfig', ''),
            'sourceID': modified_data.get('payload', {}).get('sourceID', ''),
            'eventSourceIdentity': modified_data.get('payload', {}).get('eventSourceIdentity', ''),
            'banned': modified_data.get('payload', {}).get('banned', ''),
        }

        filtered_collector['payload']['id'] = ''
        filtered_collector['payload']['name'] = ''

        filtered_collector['payload']['enrichment'] = [
            item for item in filtered_collector['payload']['enrichment']
            if item.get('id') != id_enrichment
        ]
        #filtered_collector['payload']['enrichment'].append(get_enrichmentRule('enrichmentRule', id_enrichment))

        return filtered_collector

    def validate_collectors_with_new_resource(collectors_filtered, id_resource):
        for collector in collectors_filtered:
            current_id = collector["id"]
            current_kind = collector["kind"]
            collector_new = get_and_modified_collector(current_kind, current_id, id_resource)
            # json_str = json.dumps(collector_new, indent=4, ensure_ascii=False)
            # with open('test.txt', "w", encoding="utf-8") as f:
            #     f.write(json_str)
            print(f"[INFO] Коллектору {collector_new['name']} изменен нормализатор!")
            print(f"[INFO] Запуск валидации ресурса {collector_new['name']}...")
            answer = kuma.resources_validate(current_kind, collector_new)
            print(f"Получен ответ: {answer}\n")

    def validate_and_update_collectors_with_new_resource(collectors_filtered, id_resource):
        for collector in collectors_filtered:
            current_id = collector["id"]
            current_kind = collector["kind"]
            collector_new = get_and_modified_collector(current_kind, current_id, id_resource)
            print(f"[INFO] Коллектору {collector_new['name']} изменен нормализатор!")
            print(f"[INFO] Запуск валидации ресурса {collector_new['name']}...")
            answer = kuma.resources_validate(current_kind, collector_new)
            print(f"Получен ответ: {answer}\n")
            if answer == '[Status 204: OK] Resource is valid!':
                print(f"[INFO] Запуск обновления ресурса {collector_new['name']}...")
                answer = kuma.put_kind_resources(current_kind, current_id, collector_new)
                print(f"Получен ответ: {answer}\n")

    del_enrichment = kuma.get_kind_resources('enrichmentRule', id_enrichment)
    print("\n")
    print(f"[INFO] Валидация удаления правила обогащения {del_enrichment['name']} на всех коллекторах...\n")
    validate_collectors_with_new_resource(collectors_filtered, id_enrichment)

    print(f"[INFO] Валидация и удаление правила обогащения {del_enrichment['name']} на всех коллекторах...\n")
    validate_and_update_collectors_with_new_resource(collectors_filtered, id_enrichment)

def main():
    parser = argparse.ArgumentParser(description="Скрипт для управления ресурсами KUMA. " \
    "Перед началом использования необходимо ввести в секцию Main в переменную kuma адрес Ядра и API токен!")
    
    # Добавляем возможные действия
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Парсер для создания коллекторов
    parser_create = subparsers.add_parser("create_collectors", help="TEST.Массовое создание коллекторов по всем тенантам")
    parser_create.add_argument("--id", required=True, help="ID-коллектора примера")
    parser_create.add_argument("--kind", required=True, help="Тип ресурса (коллектор)")
    parser_create.add_argument("--name", required=True, help="Имя коллектора без метки тенанта")

    # Парсер для создания ресурса
    parser_create = subparsers.add_parser("create_resource", help="Создание ресурса")
    parser_create.add_argument("--kind", required=True, help="Тип создаваемого ресурса")
    parser_create.add_argument("--tenantID", required=True, help="ID тенанта")
    parser_create.add_argument("--tenantName", required=True, help="Имя тенанта")
    parser_create.add_argument("--resource", required=True, help='Тело ресурса в формате JSON. Для чтения из файла укажите "@путь_к_файлу"')

    # Парсер для обновления ресурса коллектор
    parser_update = subparsers.add_parser("update_collectors", help="Обновление нормализатора на коллекторах по всем тенантам")
    parser_update.add_argument("--id_normalizer", required=True, help="ID нового нормализатора")
    parser_update.add_argument("--name", required=True, help="Имя коллектора")
    parser_update.add_argument("--kind", required=True, help="Тип ресурса")
    
    # Парсер для добавления правила обогащения или фильтра
    parser_update = subparsers.add_parser("update_resource_on_collector", help="Добавление обогащения на коллекторах по всем тенантам")
    parser_update.add_argument("--id_new", required=True, help="ID нового правила обогащения или фильтра")
    parser_update.add_argument("--kind", required=True, help="Тип добавляемого ресурса. В данной функции допустимые значения --kind filter и enrichmentRule")
    parser_update.add_argument("--name", required=True, help="Имя коллектора")
    

    # Парсер для добавления правила обогащения
    parser_update = subparsers.add_parser("delete_enrichment_on_collector", help="Удаление обогащения на коллекторах по всем тенантам")
    parser_update.add_argument("--id_enrichment", required=True, help="ID правила обогащения, которое необходимо отвязать от коллектора")
    parser_update.add_argument("--name", required=True, help="Имя коллектора")
    parser_update.add_argument("--kind", required=True, help="Тип ресурса. В данной функции --kind collector")

    # Парсер для получения ресурса
    parser_get = subparsers.add_parser("get_resource", help="Получение ресурса")
    parser_get.add_argument("--id_resource", required=True, help="ID ресурса")
    parser_get.add_argument("--kind", required=True, help="Тип ресурса")
    parser_get.add_argument("-o", "--output", required=False, help="Сохранять вывод в файл")

    args = parser.parse_args()

    # Здесь необходимо ввести корректные данные ! Для KUMA Standalone
    kuma = Kuma(address='FQDN или IP KUMA', port='7223', token='')
 

    # Выбираем действие на основе переданной команды
    if args.command == "create_collectors":
        print(f"\n[START] Запуск массового создания коллекторов по всем тенантам по примеру...\n")
        action_create_collectors(kuma, args.id, args.kind, args.name)
    elif args.command == "update_collectors":
        print(f"\n[START] Запуск обновления нормализатора на коллекторах...\n")
        action_update_collectors(kuma, args.name, args.kind, args.id_normalizer)
    elif args.command == "update_resource_on_collector":
        print(f"\n[START] Запуск добавления обогащения или фильтра на коллекторах...\n")
        action_update_new_resource(kuma, args.name, args.kind, args.id_new)
    elif args.command == "delete_enrichment_on_collector":
        print(f"\n[START] Запуск удаления правила обогащения на коллекторах...\n")
        action_delete_enrichment(kuma, args.name, args.kind, args.id_enrichment)
    elif args.command == "create_resource":
        if args.resource.startswith('@'):
            file_path = args.resource[1:]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    args.resource = json.loads(content)  # Парсим JSON в объект
                    action_create_resource(kuma, args.kind, args.tenantID, args.tenantName, args.resource)
            except json.JSONDecodeError as e:
                sys.exit(f"Ошибка парсинга JSON: {str(e)}")
            except Exception as e:
                sys.exit(f"Ошибка чтения файла: {str(e)}")
        else:
            action_create_resource(kuma, args.kind, args.tenantID, args.tenantName, args.resource)
    elif args.command == "get_resource":
        print(f"\n[START] Запуск получения ресурса с типом {args.kind}...\n")
        response = kuma.get_kind_resources(args.kind, args.id_resource)
        json_str = json.dumps(response, indent=4, ensure_ascii=False)
        if args.output:
        # Сохраняем в файл
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"\n[INFO] Результат сохранён в файл: {args.output}")
        else:
            # Иначе выводим в консоль
            print(response)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()