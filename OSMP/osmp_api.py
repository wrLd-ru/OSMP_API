from osmpPublicApiV1 import Osmp
import json
import argparse
import sys
    
def main():
    parser = argparse.ArgumentParser(description="Скрипт для работы с API OSMP. " \
    "Перед началом использования необходимо ввести в секцию Main в переменную osmp домен XDR и API токен!")
    
    # Добавляем возможные действия
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Парсер для создания коллекторов
    parser_create = subparsers.add_parser("get_tenants", help="Returns the list of tenants")

    # Парсер для создания ресурса
    parser_create = subparsers.add_parser("get_alerts", help="Returns a list of alerts for the specified tenants")
    parser_create.add_argument("--id", required=False, help="")
    parser_create.add_argument("--tenantID", required=True, help="")
    parser_create.add_argument("--start", required=False, help="Начало временного интервала, используемого для фильтрации списка алертов. Формат: 2025-05-14T00:00:00Z")
    parser_create.add_argument("--end", required=False, help='Конец временного интервала, используемого для фильтрации списка алертов. Формат: 2025-05-14T00:00:00Z')
    parser_create.add_argument("--status", required=False, help='')
    parser_create.add_argument("-o", "--output", required=False, help="Save output to a file")

    args = parser.parse_args()

    # Здесь необходимо ввести корректные данные !
    osmp = Osmp(xdrdomain='xdr.soc-lab.local', token='')

    # Выбираем действие на основе переданной команды
    if args.command == "get_tenants":
        print(f"\n[START] Получение списка тенантов...\n")
        osmp.get_tenants()
    elif args.command == "get_alerts":
        print(f"\n[START] Получение алертов...\n")
        response = osmp.get_alerts(
            id=args.id, 
            tenantID=args.tenantID, 
            start=args.start, 
            end=args.end, 
            status=args.status
        )
        json_str = json.dumps(response, indent=4, ensure_ascii=False)
        if args.output:
        # Сохраняем в файл
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"\n[INFO] Результат сохранён в файл: {args.output}")
            total = response.get("Total")
            print(f"Total alerts: {total}")
        else:
            # Иначе выводим в консоль
            print(json_str)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()