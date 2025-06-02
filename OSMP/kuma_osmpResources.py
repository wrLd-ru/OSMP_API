from OSMP.kuma_osmpPublicApiV3 import Kuma
import json
import argparse
import sys

def action_update_collectors(kuma_osmp, name, kind, id):

    page = 1
    name = name
    kind_collector = kind
    id_normalizer = id


    # ------------------ поиск коллекторов по названию
    print("\n")
    print(f"[INFO] Запуск поиска ресурсов с типом {kind_collector} по названию {name}...\n")
    collectors_list = kuma_osmp.resources_search(page=page, name=name, kind=kind_collector)
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


    # ----------------- получение и изменение ресурса нормализатор
    def get_filtered_normalizer(kind, id):
        normalizer = kuma_osmp.get_kind_resources(kind, id)

        modified_normalizer = normalizer.copy()

        filtered_normalizer = {}

        filtered_normalizer['normalizer'] = {
            'id': modified_normalizer.get('payload', {}).get('id', ''),
            'name': modified_normalizer.get('payload', {}).get('name', ''),
            'kind': modified_normalizer.get('payload', {}).get('kind', '')
        }
        return filtered_normalizer

    # ---------------- получение и изменение ресурса коллектора
    def get_and_modified_collector(kind_collector, id_collector, id_normalizer):
        resource = kuma_osmp.get_kind_resources(kind_collector, id_collector)

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

    def validate_collectors_with_new_normalizers(collectors_filtered, id_normalizer):
        for collector in collectors_filtered:
            current_id = collector["id"]
            current_kind = collector["kind"]
            collector_new = get_and_modified_collector(current_kind, current_id, id_normalizer)
            print(f"[INFO] Коллектору {collector_new['name']} изменен нормализатор!")
            print(f"[INFO] Запуск валидации ресурса {collector_new['name']}...")
            answer = kuma_osmp.resources_validate(current_kind, collector_new)
            print(f"Получен ответ: {answer}\n")

    def validate_and_update_collectors_with_new_normalizers(collectors_filtered, id_normalizer):
        for collector in collectors_filtered:
            current_id = collector["id"]
            current_kind = collector["kind"]
            collector_new = get_and_modified_collector(current_kind, current_id, id_normalizer)
            print(f"[INFO] Коллектору {collector_new['name']} изменен нормализатор!")
            print(f"[INFO] Запуск валидации ресурса {collector_new['name']}...")
            answer = kuma_osmp.resources_validate(current_kind, collector_new)
            print(f"Получен ответ: {answer}\n")
            if answer == '[Status 204: OK] Resource is valid!':
                print(f"[INFO] Запуск обновления ресурса {collector_new['name']}...")
                answer = kuma_osmp.put_kind_resources(current_kind, current_id, collector_new)
                print(f"Получен ответ: {answer}\n")


    new_normalizer = kuma_osmp.get_kind_resources('normalizer', id_normalizer)
    print("\n")
    print(f"[INFO] Валидация нормализатора {new_normalizer['name']} на всех коллекторах...\n")
    validate_collectors_with_new_normalizers(collectors_filtered, id_normalizer)

    print(f"[INFO] Валидация и изменение нормализатора {new_normalizer['name']} на всех коллекторах...\n")
    validate_and_update_collectors_with_new_normalizers(collectors_filtered, id_normalizer)

def action_create_collectors(kuma_osmp, id, kind, name):
    def get_filtered_normalizer(kind, id):
        normalizer = kuma_osmp.get_kind_resources(kind, id)

        modified_normalizer = normalizer.copy()

        filtered_normalizer = {}

        filtered_normalizer['normalizer'] = {
            'id': modified_normalizer.get('payload', {}).get('id', ''),
            'name': modified_normalizer.get('payload', {}).get('name', ''),
            'kind': modified_normalizer.get('payload', {}).get('kind', '')
        }
        return filtered_normalizer
    
    def get_and_filtered_example_collector(kind_collector, id_collector):
        resource = kuma_osmp.get_kind_resources(kind_collector, id_collector)

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
        answer = kuma_osmp.resources_validate(current_kind, collector_new)
        print(f"Получен ответ: {answer}\n")
#        if answer == '[Status 204: OK] Resource is valid!':
#            print(f"[INFO] Запуск обновления ресурса {collector_new['name']}...")
#            answer = kuma_osmp.resources_create(current_kind, collector_new)
#            print(f"Получен ответ: {answer}\n")
    
    collector = get_and_filtered_example_collector(kind, id)
    
    original_list = kuma_osmp.get_tenants()

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
   
def action_create_resource(kuma_osmp, kind, tenantID, tenantName, resource):
    resource['tenantID'] = tenantID
    resource['tenantName'] = tenantName
    print(f"[INFO] Запуск валидации ресурса {resource['name']}...")
    answer = kuma_osmp.resources_validate(kind, resource)
    print(f"Получен ответ: {answer}\n")
    if answer == '[Status 204: OK] Resource is valid!':
        print(f"[INFO] Запуск обновления ресурса {resource['name']}...")
        answer = kuma_osmp.resources_create(kind, resource)
        print(f"Получен ответ: {answer}\n")

def main():
    parser = argparse.ArgumentParser(description="Скрипт для управления ресурсами kuma_osmp. " \
    "Перед началом использования необходимо ввести в секцию Main в переменную kuma_osmp адрес Ядра и API токен!")
    
    # Добавляем возможные действия
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Парсер для создания коллекторов
    parser_create = subparsers.add_parser("create_collectors", help="Массовое создание коллекторов по всем тенантам")
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

    # Парсер для получения ресурса
    parser_update = subparsers.add_parser("get_resource", help="Получение ресурса")
    parser_update.add_argument("--id_resource", required=True, help="ID ресурса")
    parser_update.add_argument("--kind", required=True, help="Тип ресурса")

    args = parser.parse_args()

    # Здесь необходимо ввести корректные данные ! Для KUMA в XDR OSMP
    kuma_osmp = Kuma(xdrdomain='xdr.soc-lab.local', token='')
 

    # Выбираем действие на основе переданной команды
    if args.command == "create_collectors":
        print(f"\n[START] Запуск массового создания коллекторов по всем тенантам по примеру...\n")
        action_create_collectors(kuma_osmp, args.id, args.kind, args.name)
    elif args.command == "update_collectors":
        print(f"\n[START] Запуск обновления коллекторов...\n")
        action_update_collectors(kuma_osmp, args.name, args.kind, args.id_normalizer)
    elif args.command == "create_resource":
        if args.resource.startswith('@'):
            file_path = args.resource[1:]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    args.resource = json.loads(content)  # Парсим JSON в объект
                    action_create_resource(kuma_osmp, args.kind, args.tenantID, args.tenantName, args.resource)
            except json.JSONDecodeError as e:
                sys.exit(f"Ошибка парсинга JSON: {str(e)}")
            except Exception as e:
                sys.exit(f"Ошибка чтения файла: {str(e)}")
        else:
            action_create_resource(kuma_osmp, args.kind, args.tenantID, args.tenantName, args.resource)
    elif args.command == "get_resource":
        print(f"\n[START] Запуск получения ресурса с типом {args.kind}...\n")
        print(kuma_osmp.get_kind_resources(args.kind, args.id_resource))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()