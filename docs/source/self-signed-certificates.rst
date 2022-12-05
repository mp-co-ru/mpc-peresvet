Создание самоподписанных сертификатов
=====================================
В данном разделе рассмотрим процесс создания самоподписанных сертификатов.

Описание
++++++++
Рассмотрим ситуацию, когда платформа, а также её клиенты
(поставщики и потребители данных) находятся в сети, изолированной
от интернета, а также не имеющей своего сервера DNS.

Необходимо организовать общение платформы с клиентами по шифрованному каналу.

Глава содержит последовательность всех шагов, обеспечивающих необходимый
функционал, без подробного пояснения шагов. Для более подробной информации
можно посмотреть статьи в интернете на заданную тему.

Создадим в домашней папке новую папку `tls` и все действия
будем выполнять в ней.

После выполнения всех шагов мы получим:

#. Папка `rootCA` для хранения корневого сертификата и приватного ключа.
#. Корневой сертификат центра сертификации нашей локальной сети и ключ к нему.
#. Сертификат сервера с ключом.
#. Сертификат клиента на случай, если клиент будет
   аутентифицирован/авторизован по сертификату.

**Все шаги выполнялись на Ubuntu 22.04**

Процедура создания цепочки сертификатов
+++++++++++++++++++++++++++++++++++++++
.. raw:: html

   <details>
   <summary>
        1. Создаём в домашней папке папку <b>tls</b>.
   </summary>

.. code-block:: bash

   $ cd ~
   $ mkdir tls
   $ cd tls

.. raw:: html

   </details>
   <br />

.. raw:: html

   <details>
   <summary>
        2. Создадим корневой сертификат локального сертификационного центра.
   </summary>

.. code-block:: bash

   # создадим для корневого сертификата отдельную папку
   $ mkdir rootCA && cd rootCA

   # создадим одной командой ключ, запрос на подпись и сам сертификат сроком действия 10 лет
   # в процессе выполнения команды будут запрошены данные, вводить можно только
   # Common Name:
   #
   # You are about to be asked to enter information that will be incorporated
   # into your certificate request.
   # What you are about to enter is what is called a Distinguished Name or a DN.
   # There are quite a few fields but you can leave some blank
   # For some fields there will be a default value,
   # If you enter '.', the field will be left blank.
   # -----
   # Country Name (2 letter code) [AU]:
   # State or Province Name (full name) [Some-State]:
   # Locality Name (eg, city) []:
   # Organization Name (eg, company) [Internet Widgits Pty Ltd]:
   # Organizational Unit Name (eg, section) []:
   # Common Name (e.g. server FQDN or YOUR name) []:Local CA
   # Email Address []:
   $ openssl req -new -newkey rsa:4096 -nodes -keyout rootCA.key -x509 -days 3654 -out rootCA.crt
   $ cd ..

.. raw:: html

   </details>
   <br />

.. raw:: html

   <details>
   <summary>
        3. Создаём сертификат для сервера, на котором будет работать наше приложение
   </summary>
   Сертификат и ключ сервера будут храниться в отдельной папке. Для удобства
   пусть папка называется так же, как и сервер. Допустим, <b>MPCServer</b>:

.. code-block:: bash

   $ mkdir MPCServer

Создаём ключ сервера:

.. code-block:: bash

   $ openssl genrsa -out MPCServer/MPCServer.key 4096

Запрос на подпись серверного сертификата.

**Обратите внимание, что в качестве Common Name НЕОБХОДИМО указать имя
сервера. В нашем случае - MPCServer:**

.. code-block:: bash

   # You are about to be asked to enter information that will be incorporated
   # into your certificate request.
   # What you are about to enter is what is called a Distinguished Name or a DN.
   # There are quite a few fields but you can leave some blank
   # For some fields there will be a default value,
   # If you enter '.', the field will be left blank.
   # -----
   # Country Name (2 letter code) [AU]:
   # State or Province Name (full name) [Some-State]:
   # Locality Name (eg, city) []:
   # Organization Name (eg, company) [Internet Widgits Pty Ltd]:
   # Organizational Unit Name (eg, section) []:
   # Common Name (e.g. server FQDN or YOUR name) []:MPCServer
   # Email Address []:

   # Please enter the following 'extra' attributes
   # to be sent with your certificate request
   # A challenge password []:
   # An optional company name []:

   $ openssl req -new -key MPCServer/MPCServer.key -out MPCServer/MPCServer.csr

Создаём сертификат для сервера, подписывая его корневым сертификатом и ключом
нашего локального сертификационного центра:

.. code-block:: bash

   $ openssl x509 -req -in MPCServer/MPCServer.csr -CA rootCA/rootCA.crt -CAkey rootCA/rootCA.key -CAcreateserial -out MPCServer/MPCServer.crt -days 3654

Упакуем сертификат и ключ сервера в один пакет для подгрузки в конфигурацию
NGINX.Unit:

.. code-block:: bash

   $ cat MPCServer/MPCServer.crt MPCServer/MPCServer.key > MPCServer/MPCServer_pack.pem

.. raw:: html

   </details>
   <br />

.. raw:: html

   <details>
   <summary>4. Генерация клиентского сертификата</summary>

В том случае, если аутентификация/авторизация пользователя или клиентского
приложения происходит с помощью сертификата (допустим, клиент -
это программа-поставщик данных), то необходимо создать клиентский сертификат.

Создадим его также в отдельной папке.

.. code-block:: bash

   $ mkdir client && cd client

Создадим клиентский ключ:

.. code-block:: bash

   $ openssl genrsa -out client.key 4096

Запрос на подпись сертификата. В качестве Common Name указываем имя клиента,
по которому будем его аутентифицировать:

.. code-block:: bash

   # You are about to be asked to enter information that will be incorporated
   # into your certificate request.
   # What you are about to enter is what is called a Distinguished Name or a DN.
   # There are quite a few fields but you can leave some blank
   # For some fields there will be a default value,
   # If you enter '.', the field will be left blank.
   # -----
   # Country Name (2 letter code) [AU]:
   # State or Province Name (full name) [Some-State]:
   # Locality Name (eg, city) []:
   # Organization Name (eg, company) [Internet Widgits Pty Ltd]:
   # Organizational Unit Name (eg, section) []:
   # Common Name (e.g. server FQDN or YOUR name) []:some_client
   # Email Address []:

   # Please enter the following 'extra' attributes
   # to be sent with your certificate request
   # A challenge password []:
   # An optional company name []:
   $ openssl req -new -key client.key -out client.csr

Создаём сертификат для клиента, подписывая его корневым сертификатом
локального сертификационного центра:

.. code-block:: bash

   $ openssl x509 -req -in client.csr -CA ../rootCA/rootCA.crt -CAkey ../rootCA/rootCA.key -CAcreateserial -out client.crt -days 3654

.. raw:: html

   </details>
   <br />

Теперь мы имеем коплект сертификатов для организации безопасного канала связи
между платформой и клиентом, включая случай аутентификации/авторизации
пользователя с помощью сертификата.
