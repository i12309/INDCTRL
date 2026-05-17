# control-web

Назначение: Django admin, dashboard, отчеты, экспорт CSV/XLSX и миграции БД.

## Доступ

Dashboard и отчеты доступны ролям `admin`, `director`, `manager`. Роль `worker` не
имеет доступа к управленческим страницам.

## Dashboard

- `GET /dashboard/current-workers/` - активные смены: станок, работник, начало смены,
  последний heartbeat и статус связи.

Статус связи считается по `HEARTBEAT_MAX_AGE_SECONDS`: свежий heartbeat означает
активную связь, старый heartbeat - устаревшую связь, пустой heartbeat - устройство
еще не присылало сигнал после входа.

## Отчет по деталям

- `GET /reports/details/` - таблица деталей с фильтрами и пагинацией;
- `GET /reports/details/export/csv/` - CSV-экспорт с теми же фильтрами;
- `GET /reports/details/export/xlsx/` - Excel-экспорт с теми же фильтрами.

Фильтры: дата с, дата по, станок, работник, смена, тип детали, состояние детали.
В первой версии экспорт ограничен 100 000 строками.
