Администрирование
=================
Создание тэгов
++++++++++++++
Для записи данных необходимо сначала создать тэги.

Формат атрибута `prsStore`: 

.. code-block:: json

   {
       "metric": "metric_name",
       "tags": {
           "t1": "v1",
           "t2": "v2"
       }
   }

В случае, если в атрибуте `prsStore` будет отсутствовать ключ `metric` или он будет равен None, то в качестве
имени метрики будет взято имя тэга:

.. code-block:: json

   {
       "metric": "<tag_cn>"
   }

При записи данных в **VictoriaMetrics** **Пересвет** добавит к этой структуре ключи `value` и `timestamp` (`см. пример 
<http://opentsdb.net/docs/build/html/api_http/put.html#example-multiple-data-point-put>`_).


