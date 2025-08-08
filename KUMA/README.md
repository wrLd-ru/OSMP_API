Библиотека для работы API KUMA: kuma_osmpPublicApiV3.py

Описание: https://support.kaspersky.com/help/XDR/1.3/common/KUMA_RestAPI/dist/index.html?urls.primaryName=KUMA

Функции:
positional arguments: {create_collectors,create_resource,update_collectors,update_enrichment_on_collector,delete_enrichment_on_collector get_resource}
                        Доступные команды
    create_collectors                   Массовое создание коллекторов по всем тенантам
    create_resource                     Создание ресурса
    update_collectors                   Обновление нормализатора на коллекторах по всем тенантам
    update_enrichment_on_collector      Добавление обогащения на коллекторах по всем тенантам
    delete_enrichment_on_collector      Удаление обогащения на коллекторах по всем тенантам
    get_resource                        Получение ресурса

options:
  -h, --help            show this help message and exit

Запуск на Windows:

Изменение нормализатора на коллекторах (поиск коллектора по имени регуляркой):
```
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe "C:\Users\admin\Documents\API_KUMA\OSMP_API\kuma_osmpResources.py" update_collectors --id_normalizer f2f9a835-6fdf-4dea-91b3-1ccc1a270582 --name '^test.*' --kind collector
```

Удаление правила обогащения на коллекторе:
```
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe "C:\Users\admin\Documents\API_KUMA\OSMP_API\kuma_osmpResources.py" delete_enrichment_on_collector --id_enrichment 9cdb307a-19e6-430c-ad41-6755460a8c51 --name '^test collector$' --kind collector
```

Получение ресурса:
```
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe "C:\Users\admin\Documents\API_KUMA\OSMP_API\kuma_osmpResources.py" get_resource --id_resource b3d6f37c-fb3d-4f22-995a-2e8d559ea496 --kind enrichmentRule
```