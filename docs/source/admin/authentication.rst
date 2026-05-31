.. _administration_auth:

.. include:: ../_include/head.rst

==============
Authentication
==============

In case your primary authentication method is not working for some reason - you can enter the application with a local user at: :code:`/a/login/fallback`

.. _administration_auth_header:

HTTP Header Authentication
##########################

Ansible-WebUI can trust a username supplied by a reverse proxy in an HTTP header.

This mode expects the reverse proxy to perform authentication before requests reach Ansible-WebUI. Unknown users are not created automatically; the header value must match an existing Django username.

Setup
*****

1. Enable header authentication:

  .. code-block:: yaml

      AUTH: 'header'
      REMOTE_USER_HEADER: 'HTTP_REMOTE_USER'

  The default :code:`REMOTE_USER_HEADER` value is :code:`HTTP_REMOTE_USER`. A proxy HTTP header named :code:`Remote-User` is exposed to Django as :code:`HTTP_REMOTE_USER`.

2. Create the users in advance.

  For the initial administrator, set :code:`AW_ADMIN` to the same username the proxy sends in the configured header.

3. Ensure Ansible-WebUI is only reachable through the trusted reverse proxy.

  The proxy must remove any inbound user header before setting its own value. HAProxy example:

  .. code-block:: haproxy

      http-request del-header Remote-User
      http-request set-header Remote-User %[...authenticated-user...]

Logout
******

Local logout does not end the proxy-side authentication session. If the proxy continues sending the user header, Django will authenticate the user again on the next request. The WebUI therefore hides its logout button in this mode.

.. note::

    In header mode the default ``ModelBackend`` (local password authentication) is disabled. All login paths — including Django's :code:`/admin/` interface — require the proxy-supplied header. If direct database access is ever needed, use Django's :code:`createsuperuser` management command together with a temporary local-auth setup.

.. _administration_auth_saml:

SAML SSO
########

**Tested config examples**: `Google Workspace <https://github.com/O-X-L/ansible-webui/blob/latest/examples/saml_google_workspace.yml>`_

This app is integrating the `grafana/django-saml2-auth module <https://github.com/grafana/django-saml2-auth>`_ (indirect `pysaml2 <https://github.com/IdentityPython/pysaml2>`_).

If you have troubles with getting SAML to work - check out :ref:`Administration - Troubleshooting - SAML <administration_troubleshooting_saml>`

----

Setup
*****

1. Add the :code:`SAML` config-block to your config-file. See: :ref:`Getting Started - Config - File <start_config_file>`

  For options see: `Module settings <https://github.com/grafana/django-saml2-auth?tab=readme-ov-file#module-settings>`_

  Example:

  .. code-block:: yaml

      HOSTNAMES: '<YOUR-DOMAIN>'
      AUTH: 'saml'
      SAML:
          METADATA_AUTO_CONF_URL: 'https://<YOUR-IDP>/metadata'
          # METADATA_LOCAL_FILE_PATH: '/etc/ansible-webui/saml-metadata.txt'

          # replace with your scheme, domain and port!
          ASSERTION_URL: 'http://localhost:8000'
          ENTITY_ID: 'http://localhost:8000/a/saml/acs/'
          DEFAULT_NEXT_URL: 'http://localhost:8000/'

          CREATE_USER: true
          NEW_USER_PROFILE:
              USER_GROUPS: []  # The default group name when a new user logs in
              ACTIVE_STATUS: true
              STAFF_STATUS: true  # allow user to view 'System - Admin' page
              SUPERUSER_STATUS: false  # full system admin privileges

          ATTRIBUTES_MAP:  # email or username and token are required!
              # mapping: django => IDP
              email: 'email'
              username: 'email'
              token: 'id'
              # optional:
              first_name: 'firstName'
              last_name: 'lastName'
              groups: 'Groups'  # Optional

          DEBUG: false  # DO NOT PERMANENTLY ENABLE!

          GROUPS_MAP:  # map IDP groups to django groups
              'IDP GROUP': 'AW Job Managers'

          # NAME_ID_FORMAT: 'user.email'
          # KEY_FILE: '/etc/ansible-webui/saml.key'
          # CERT_FILE: '/etc/ansible-webui/saml.crt'

2. SSO identity provider settings:

  **ACS URL**: :code:`http://localhost:8000/a/saml/acs/`

  **Entity ID/Audience URL**: :code:`http://localhost:8000/a/saml/acs/`

  Note: Replace *http://localhost:8000* with your scheme, domain and port


3. For non-Docker setups: Install the :code:`xmlsec` package that is used internally (see: `details <https://github.com/IdentityPython/pysaml2?tab=readme-ov-file#external-dependencies>`_)


You should now be able to see :code:`[INFO] [main] Using Auth-Mode: saml` logged on startup.

----

Docker
******

Example:

.. code-block:: bash

    # save all needed SAML files to /etc/ansible-webui/ on your host system
    sudo docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 --env AW_CONFIG=/etc/aw/config.yml --volume /etc/ansible-webui/:/etc/aw/ oxlorg/ansible-webui:latest
