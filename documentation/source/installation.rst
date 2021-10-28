Installation
============
Устанавливаем систему на операционную систему Ubuntu Desktop 20.04.3.

Установка состоит из двух частей.

Grafana
+++++++
Выбираем Open-Source (OSS) версию Grafana, так как пользоваться хотим бесплатным продуктом.

Enterprise-версия отличается от OSS только наличием заблокированных возможностей, которыми можно пользоваться, 
купив лицению.

Согласно `инструкциям <https://grafana.com/docs/grafana/latest/installation/debian/#install-on-debian-or-ubuntu>`_ выполняем следующие шаги:

#. Добавляем ключ:

   .. code-block:: bash
      
      $ wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

#. Добавляем для пакетного менеджера ссылку на репозиторий Grafana:

   .. code-block:: bash
      
      $ echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

#. Обновляем список пакетов:

   .. code-block:: bash

      $ sudo apt update

#. Устанавливаем Grafana:

   .. code-block:: bash

      $ sudo apt install grafana

#. Разрешим запускаться Grafan'е автоматически при включении компьютера:

   .. code-block:: bash

      $ sudo systemctl enable grafana-server

#. Запустим Grafan'у:

   .. code-block:: bash
  
      $ sudo systemctl start grafana-server

#. Проверяем, работает ли Grafana. Для этого запускаем браузер и в строке адреса пишем: ``http://localhost:3000``.
   Если мы всё сделали правильно, появится чёрная страница, на которой в качестве имени пользователя и пароля необходимо ввести ``admin``.  
   Сразу же перейдём на страницу смены пароля, а, сменив его, увидим стартовую страницу Grafan'ы:

   .. image:: pics/grafana.png

Установка Grafan'ы завершена.

Описание настройки работы совместно с Victoriametrics - ниже.

Victoriametrics
+++++++++++++++