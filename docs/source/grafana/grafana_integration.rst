Интеграция с Grafana
====================
Установим платформу и Grafana: :ref:`installation`.

Grafana получает данные из платформы по протоколу MQTT, а также может
отправлять данные в платформу.

Для этого необходимы два плагина:

#. `MQTT data source <https://grafana.com/grafana/plugins/grafana-mqtt-datasource/>`_
#. `Ручной ввод данных <https://github.com/mp-co-ru/grafana-ui-plugin/releases/download/v0.2.0/mp-co-peresvet-app-0-2-0.zip>`_

Оба плагина уже находятся в контейнере с Grafana,
развёрнутом в процессе установки.

Первый запуск Grafana
---------------------
#. Откройте браузер и в строке адреса введите http://localhost/grafana/
#. В форме авторизации введите ``admin`` в качестве пользователя
   и ``admin`` в качестве пароля.
#. Вам будет предложено изменить пароль. Введите новый пароль и в следующий раз
   пользуйтесь им.

Подключение к платформе по протоколу MQTT
-----------------------------------------
В меню Grafana переходим в раздел ``Connections → Add new connection``:

.. figure:: ../pics/mqtt_01.png
   :align: center

   Меню "Новое соединение"

В списке источников данных выбираем MQTT:

.. figure:: ../pics/mqtt_02.png
   :align: center

   MQTT

В новом окне нажимаем кнопку ``Add new data source``:

.. figure:: ../pics/mqtt_03.png
   :align: center

   Добавление нового источника данных

Заполняем параметры источника данных:

.. figure:: ../pics/mqtt_04.png
   :align: center

   Параметры источника данных

#. **URI**: ``tcp://rabbitmq:1883``
#. **Username**: ``prs``
#. **Password**: ``Peresvet21``.

После ввода данных нажимаем кнопку ``Save and test``, после чего должна
появиться надпись с зелёным фоном о том, что тест источника данных прошёл
успешно:

.. figure:: ../pics/mqtt_05.png
   :align: center

   Источник данных создан

Панель для отображения данных
-----------------------------
При создании панели для отображения данных выбираем источник данных, который
создали на предыдущем шаге, а в поле ``Topic`` вписываем id тега, из которого
хотим забирать данные:

.. figure:: ../pics/mqtt_06.png
   :align: center

   Новая панель данных

.. warning::
   После создания панели необходимо:

   1. Сохранить экран
   2. Выключить обновление экрана

   .. figure:: ../pics/mqtt_07.png
      :align: center

      Период обновления экрана



Отправка данных из Grafana в платформу
--------------------------------------

Для отправки данных из Grafana необходимо установить плагин формы ручного ввода.

Установка плагина
~~~~~~~~~~~~~~~~~

Linux/MacOS
"""""""""""

.. code-block:: sh

   wget "https://github.com/mp-co-ru/grafana-ui-plugin/mp-co-peresvet-app-1-0-0.zip" -O <директория для плагинов в Grafana>/mp-co-peresvet-app-1-0-0.zip
   unzip <директория для плагинов в Grafana>/mp-co-peresvet-app-1-0-0.zip -d <директория для плагинов в Grafana>/mp-co-peresvet-app-1-0-0
   rm <директория для плагинов в Grafana>/mp-co-peresvet-app-1-0-0.zip

.. note::
   Директория для плагинов в Grafana по умолчанию находится по пути `/usr/local/var/lib/grafana/plugins`.

Docker
""""""

.. code-block:: sh

   docker run -d -p 3000:3000 --name=grafana \
   -e "GF_INSTALL_PLUGINS=https://github.com/mp-co-ru/grafana-ui-plugin/mp-co-peresvet-app-1-0-0.zip;mp-co-peresvet-app" \
   grafana/grafana-enterprise

Для его работы дополнительная настройка Grafana не требуется
Подробнее про запуск, конфигурацию и работу плагина

`Плагин для формы ручного ввода в Grafana <./grafana_plugin.rst>`
