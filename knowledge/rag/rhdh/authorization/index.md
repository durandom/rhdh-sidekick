Administrators can authorize users to perform actions and define what
users can do in Developer Hub.

Role-based access control (RBAC) is a security concept that defines how
to control access to resources in a system by specifying a mapping
between users of the system and the actions that those users can perform
on resources in the system. You can use RBAC to define roles with
specific permissions and then assign the roles to users and groups.

RBAC on Developer Hub is built on top of the Permissions framework,
which defines RBAC policies in code. Rather than defining policies in
code, you can use the Developer Hub RBAC feature to define policies in a
declarative fashion by using a simple CSV based format. You can define
the policies by using Developer Hub web interface or REST API instead of
editing the CSV directly.

An administrator can define authorizations in Developer Hub by taking
the following steps:

1.  Enable the RBAC feature and give authorized users access to the
    feature.

2.  Define roles and policies by combining the following methods:

    - The Developer Hub policy administrator uses the Developer Hub web
      interface or REST API.

    - The Developer Hub administrator edits the main Developer Hub
      configuration file.

    - The Developer Hub administrator edits external files.

## Enabling and giving access to the Role-Based Access Control (RBAC) feature {#enabling-and-giving-access-to-rbac}

The Role-Based Access Control (RBAC) feature is disabled by default.
Enable the RBAC plugin and declare policy administrators to start using
RBAC features.

The permission policies for users and groups in the Developer Hub are
managed by permission policy administrators. Only permission policy
administrators can access the Role-Based Access Control REST API.

<div>

::: title
Prerequisites
:::

- You have [added a custom Developer Hub application
  configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index),
  and have necessary permissions to modify it.

- You have [enabled an authentication
  provider](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/authentication_in_red_hat_developer_hub/index).

</div>

<div>

::: title
Procedure
:::

1.  The RBAC plugin is installed but disabled by default. To enable the
    `./dynamic-plugins/dist/backstage-community-plugin-rbac` plugin,
    edit your `dynamic-plugins.yaml` with the following content.

    :::: formalpara
    ::: title
    `dynamic-plugins.yaml` fragment
    :::

    ``` yaml
    plugins:
      - package: ./dynamic-plugins/dist/backstage-community-plugin-rbac
        disabled: false
    ```
    ::::

    See [Installing and viewing plugins in Red Hat Developer
    Hub](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_and_viewing_plugins_in_red_hat_developer_hub/index).

2.  Declare policy administrators to enable a select number of
    authenticated users to configure RBAC policies through the REST API
    or Web UI, instead of modifying the CSV file directly. The
    permissions can be specified in a separate CSV file referenced in
    your `my-rhdh-app-config` config map, or permissions can be created
    using the REST API or Web UI.

    To declare users such as *\<your_policy_administrator_name\>* as
    policy administrators, edit your custom Developer Hub ConfigMap,
    such as `app-config-rhdh`, and add following code to the
    `app-config.yaml` content:

    :::: formalpara
    ::: title
    `app-config.yaml` fragment
    :::

    ``` yaml
    permission:
      enabled: true
      rbac:
        admin:
          users:
            - name: user:default/<your_policy_administrator_name>
    ```
    ::::

3.  In order for the Developer Hub Web UI to display available
    permissions provided by installed plugins, add the corresponding
    plugin IDs to [your custom `app-config.yaml` Developer Hub
    configuration
    file](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index).

    To display available permissions in RBAC UI, edit your custom
    Developer Hub ConfigMap, such as `app-config-rhdh`, and add
    following code to the `app-config.yaml` content:

    :::: formalpara
    ::: title
    `app-config.yaml` fragment
    :::

    ``` yaml
    permission:
      enabled: true
      rbac:
        admin:
          users:
            - name: user:default/<your_policy_administrator_name>
        pluginsWithPermission:
          - catalog
          - scaffolder
          - permission
    ```
    ::::

</div>

<div>

::: title
Verification
:::

1.  Sign out from the existing Red Hat Developer Hub session and log in
    again using the declared policy administrator account.

2.  With RBAC enabled, most features are disabled by default.

    a.  Navigate to the **Catalog** page in RHDH. The **Create** button
        is not visible. You cannot create new components.

    b.  Navigate to the API page. The **Register** button is not
        visible.

</div>

<div>

::: title
Next steps
:::

- Explicitly enable permissions to resources in Developer Hub.

</div>

## Determining permission policy and role configuration source {#proc-determining-policy-and-role-source}

You can configure Red Hat Developer Hub policy and roles by using
different sources. To maintain data consistency, Developer Hub
associates each permission policy and role with one unique source. You
can only use this source to change the resource.

The available sources are:

Configuration file

:   Configure roles and policies in the Developer Hub `app-config.yaml`
    configuration file, for instance to [declare your policy
    administrators](#enabling-and-giving-access-to-rbac).

    The Configuration file pertains to the default
    `role:default/rbac_admin` role provided by the RBAC plugin. The
    default role has limited permissions to create, read, update, delete
    permission policies or roles, and to read catalog entities.

    :::: note
    ::: title
    :::

    In case the default permissions are insufficient for your
    administrative requirements, you can create a custom admin role with
    the required permission policies.
    ::::

REST API

:   Configure roles and policies [by using the Developer Hub Web
    UI](#managing-authorizations-by-using-the-web-ui) or by using the
    REST API.

CSV file

:   Configure roles and policies by using external CSV files.

Legacy

:   The legacy source applies to policies and roles defined before RBAC
    backend plugin version `2.1.3`, and is the least restrictive among
    the source location options.

    :::: important
    ::: title
    :::

    Replace the permissions and roles using the legacy source with the
    permissions using the REST API or the CSV file sources.
    ::::

<div>

::: title
Procedure
:::

- To determine the source of a role or policy, use a `GET` request.

</div>

## Managing role-based access controls (RBAC) using the Red Hat Developer Hub Web UI {#managing-authorizations-by-using-the-web-ui}

Policy administrators can use the Developer Hub web interface (Web UI)
to allocate specific roles and permissions to individual users or
groups. Allocating roles ensures that access to resources and
functionalities is regulated across the Developer Hub.

With the policy administrator role in Developer Hub, you can assign
permissions to users and groups. This role allows you to view, create,
modify, and delete the roles using Developer Hub Web UI.

### Creating a role in the Red Hat Developer Hub Web UI {#proc-rbac-ui-create-role_title-authorization}

You can create a role in the Red Hat Developer Hub using the Web UI.

<div>

::: title
Prerequisites
:::

- You [have enabled RBAC, have a policy administrator role in Developer
  Hub, and have added plugins with
  permission](#enabling-and-giving-access-to-rbac).

</div>

<div>

::: title
Procedure
:::

1.  Go to **Administration** at the bottom of the sidebar in the
    Developer Hub.

    The **RBAC** tab appears, displaying all the created roles in the
    Developer Hub.

2.  (Optional) Click any role to view the role information on the
    **OVERVIEW** page.

3.  Click **CREATE** to create a role.

4.  Enter the name and description of the role in the given fields and
    click **NEXT**.

5.  Add users and groups using the search field, and click **NEXT**.

6.  Select **Plugin** and **Permission** from the drop-downs in the
    **Add permission policies** section.

7.  Select or clear the **Policy** that you want to set in the **Add
    permission policies** section, and click **NEXT**.

8.  Review the added information in the **Review and create** section.

9.  Click **CREATE**.

</div>

:::: formalpara
::: title
Verification
:::

The created role appears in the list available in the **RBAC** tab.
::::

### Editing a role in the Red Hat Developer Hub Web UI {#proc-rbac-ui-edit-role_title-authorization}

You can edit a role in the Red Hat Developer Hub using the Web UI.

:::: note
::: title
:::

The policies generated from a `policy.csv` or ConfigMap file cannot be
edited or deleted using the Developer Hub Web UI.
::::

<div>

::: title
Prerequisites
:::

- You [have enabled RBAC, have a policy administrator role in Developer
  Hub, and have added plugins with
  permission](#enabling-and-giving-access-to-rbac).

- The role that you want to edit is created in the Developer Hub.

</div>

<div>

::: title
Procedure
:::

1.  Go to **Administration** at the bottom of the sidebar in the
    Developer Hub.

    The **RBAC** tab appears, displaying all the created roles in the
    Developer Hub.

2.  (Optional) Click any role to view the role information on the
    **OVERVIEW** page.

3.  Select the edit icon for the role that you want to edit.

4.  Edit the details of the role, such as name, description, users and
    groups, and permission policies, and click **NEXT**.

5.  Review the edited details of the role and click **SAVE**.

</div>

After editing a role, you can view the edited details of a role on the
**OVERVIEW** page of a role. You can also edit a role's users and groups
or permissions by using the edit icon on the respective cards on the
**OVERVIEW** page.

### Deleting a role in the Red Hat Developer Hub Web UI {#proc-rbac-ui-delete-role_title-authorization}

You can delete a role in the Red Hat Developer Hub using the Web UI.

:::: note
::: title
:::

The policies generated from a `policy.csv` or ConfigMap file cannot be
edited or deleted using the Developer Hub Web UI.
::::

<div>

::: title
Prerequisites
:::

- You [have enabled RBAC and have a policy administrator role in
  Developer Hub](#enabling-and-giving-access-to-rbac).

- The role that you want to delete is created in the Developer Hub.

</div>

<div>

::: title
Procedure
:::

1.  Go to **Administration** at the bottom of the sidebar in the
    Developer Hub.

    The **RBAC** tab appears, displaying all the created roles in the
    Developer Hub.

2.  (Optional) Click any role to view the role information on the
    **OVERVIEW** page.

3.  Select the delete icon from the **Actions** column for the role that
    you want to delete.

    **Delete this role?** pop-up appears on the screen.

4.  Click **DELETE**.

</div>

## Managing authorizations by using the REST API

To automate the maintenance of Red Hat Developer Hub permission policies
and roles, you can use Developer Hub role-based access control (RBAC)
REST API.

You can perform the following actions with the REST API:

- Retrieve information about:

  - All permission policies

  - Specific permission policies

  - Specific roles

  - Static plugins permission policies

- Create, update, or delete:

  - Permission policy

  - Role

### Sending requests to the RBAC REST API by using the curl utility {#proc-sending-requests-to-the-rbac-rest-api-by-using-curl_title-authorization}

You can send RBAC REST API requests by using the curl utility.

<div>

::: title
Prerequisites
:::

- [You have access to the RBAC
  feature](#enabling-and-giving-access-to-rbac).

</div>

<div>

::: title
Procedure
:::

1.  Find your Bearer token to authenticate to the REST API.

    a.  In your browser, open the web console **Network** tab.

    b.  In the main screen, reload the Developer Hub **Homepage**.

    c.  In the web console **Network** tab, search for the `query?term=`
        network call.

    d.  Save the **token** in the response JSON for the next steps.

2.  In a terminal, run the curl command and review the response:

    :::: formalpara
    ::: title
    `GET` or `DELETE` request
    :::

        curl -v \
          -H "Authorization: Bearer <token>" \
          -X <method> "https://<my_developer_hub_url>/<endpoint>" \
    ::::

    :::: formalpara
    ::: title
    `POST` or `PUT` request requiring JSON body data
    :::

        curl -v -H "Content-Type: application/json" \
          -H "Authorization: Bearer <token>" \
          -X POST "https://<my_developer_hub_url>/<endpoint>" \
          -d <body>
    ::::

    *\<token\>*

    :   Enter your saved authorization token.

    *\<method\>*

    :   Enter the HTTP method for your [API
        endpoint](#ref-rbac-rest-api-endpoints_title-authorization).

        - `GET`: To retrieve specified information from a specified
          resource endpoint.

        - `POST`: To create or update a resource.

        - `PUT`: To update a resource.

        - `DELETE`: To delete a resource.

    https://*\<my_developer_hub_url\>*

    :   Enter your Developer Hub URL.

    *\<endpoint\>*

    :   Enter the [API
        endpoint](#ref-rbac-rest-api-endpoints_title-authorization) to
        which you want to send a request, such as
        `/api/permission/policies`.

    *\<body\>*

    :   Enter the JSON body with data that your [API
        endpoint](#ref-rbac-rest-api-endpoints_title-authorization)
        might need with the HTTP `POST` or `PUT` request.

    :::: formalpara
    ::: title
    Example request to create a role
    :::

        curl -v -H "Content-Type: application/json" \
          -H "Authorization: Bearer <token>" \
          -X POST "https://<my_developer_hub_url>/api/permission/roles" \
          -d '{
              "memberReferences": ["group:default/example"],
              "name": "role:default/test",
              "metadata": { "description": "This is a test role" }
            }'
    ::::

    :::: formalpara
    ::: title
    Example request to update a role
    :::

        curl -v -H "Content-Type: application/json" \
          -H "Authorization: Bearer <token>" \
          -X PUT "https://<my_developer_hub_url>/api/permission/roles/role/default/test" \
          -d '{
                  "oldRole": {
                    "memberReferences":  [ "group:default/example" ],
                    "name": "role:default/test"
                  },
                  "newRole": {
                    "memberReferences": [ "group:default/example", "user:default/test" ],
                    "name": "role:default/test"
                  }
                }'
    ::::

    :::: formalpara
    ::: title
    Example request to create a permission policy
    :::

        curl -v -H "Content-Type: application/json" \
          -H "Authorization: Bearer $token" \
          -X POST "https://<my_developer_hub_url>/api/permission/policies" \
          -d '[{
              "entityReference":"role:default/test",
              "permission": "catalog-entity",
              "policy": "read", "effect":"allow"
            }]'
    ::::

    :::: formalpara
    ::: title
    Example request to update a permission policy
    :::

        curl -v -H "Content-Type: application/json" \
          -H "Authorization: Bearer $token" \
          -X PUT "https://<my_developer_hub_url>/api/permission/policies/role/default/test" \
          -d '{
                 "oldPolicy": [
                   {
                     "permission": "catalog-entity", "policy": "read", "effect": "allow"
                   }
                 ],
                 "newPolicy":
                   [
                     {
                       "permission": "policy-entity", "policy": "read", "effect": "allow"
                     }
                   ]
               }'
    ::::

    :::: formalpara
    ::: title
    Example request to create a condition
    :::

        curl -v -H "Content-Type: application/json" \
          -H "Authorization: Bearer $token" \
          -X POST "https://<my_developer_hub_url>/api/permission/roles/conditions" \
          -d '{
              "result": "CONDITIONAL",
              "roleEntityRef": "role:default/test",
              "pluginId": "catalog",
              "resourceType": "catalog-entity",
              "permissionMapping": ["read"],
              "conditions": {
                "rule": "IS_ENTITY_OWNER",
                "resourceType": "catalog-entity",
                "params": {"claims": ["group:default/janus-authors"]}
              }
            }'
    ::::

    :::: formalpara
    ::: title
    Example request to update a condition
    :::

        curl -v -H "Content-Type: application/json" \
          -H "Authorization: Bearer $token" \
          -X PUT "https://<my_developer_hub_url>/api/permission/roles/conditions/1" \
          -d '{
                  "result":"CONDITIONAL",
                  "roleEntityRef":"role:default/test",
                  "pluginId":"catalog",
                  "resourceType":"catalog-entity",
                  "permissionMapping": ["read",  "update", "delete"],
                  "conditions": {
                    "rule": "IS_ENTITY_OWNER",
                    "resourceType": "catalog-entity",
                    "params": {"claims": ["group:default/janus-authors"]}
                  }
               }'
    ::::

</div>

<div>

::: title
Verification
:::

- Review the returned HTTP status code:

  `200` OK

  :   The request was successful.

  `201` Created

  :   The request resulted in a new resource being successfully created.

  `204` No Content

  :   The request was successful, and the response payload has no more
      content.

  `400` Bad Request

  :   Input error with the request.

  `401` Unauthorized

  :   Lacks valid authentication for the requested resource.

  `403` Forbidden

  :   Refusal to authorize request.

  `404` Not Found

  :   Could not find requested resource.

  `409` Conflict

  :   Request conflict with the current state and the target resource.

</div>

### Sending requests to the RBAC REST API by using a REST client {#proc-rbac-sending-requests-to-the-rbac-rest-api-by-using-a-rest-client_title-authorization}

You can send RBAC REST API requests using any REST client.

<div>

::: title
Prerequisites
:::

- [You have access to the RBAC
  feature](#enabling-and-giving-access-to-rbac).

</div>

<div>

::: title
Procedure
:::

1.  Find your Bearer token to authenticate to the REST API.

    a.  In your browser, open the web console **Network** tab.

    b.  In the main screen, reload the Developer Hub **Homepage**.

    c.  In the web console **Network** tab, search for the `query?term=`
        network call.

    d.  Save the **token** in the response JSON for the next steps.

2.  In your REST client, run a command with the following parameters and
    review the response:

    Authorization

    :   Enter your saved authorization token.

    HTTP method

    :   Enter the HTTP method for your [API
        endpoint](#ref-rbac-rest-api-endpoints_title-authorization).

        - `GET`: To retrieve specified information from a specified
          resource endpoint.

        - `POST`: To create or update a resource.

        - `PUT`: To update a resource.

        - `DELETE`: To delete a resource.

    URL

    :   Enter your Developer Hub URL and [API
        endpoint](#ref-rbac-rest-api-endpoints_title-authorization):
        https://*\<my_developer_hub_url\>*/*\<endpoint\>*, such as
        `https://<my_developer_hub_url>/api/permission/policies`.

    Body

    :   Enter the JSON body with data that your [API
        endpoint](#ref-rbac-rest-api-endpoints_title-authorization)
        might need with the HTTP `POST` request.

</div>

### Supported RBAC REST API endpoints {#ref-rbac-rest-api-endpoints_title-authorization}

The RBAC REST API provides endpoints for managing roles, permissions,
and conditional policies in the Developer Hub and for retrieving
information about the roles and policies.

#### Roles {#_roles}

The RBAC REST API supports the following endpoints for managing roles in
the Red Hat Developer Hub.

\[GET\] /api/permission/roles

:   Returns all roles in Developer Hub.

    :::: formalpara
    ::: title
    Example response (JSON)
    :::

    ``` json
    [
      {
        "memberReferences": ["user:default/username"],
        "name": "role:default/guests"
      },
      {
        "memberReferences": [
          "group:default/groupname",
          "user:default/username"
        ],
        "name": "role:default/rbac_admin"
      }
    ]
    ```
    ::::

\[GET\] /api/permission/roles/*\<kind\>*/*\<namespace\>*/*\<name\>*

:   Returns information for a single role in Developer Hub.

    :::: formalpara
    ::: title
    Example response (JSON)
    :::

    ``` json
    [
      {
        "memberReferences": [
          "group:default/groupname",
          "user:default/username"
        ],
        "name": "role:default/rbac_admin"
      }
    ]
    ```
    ::::

\[POST\] /api/permission/roles/*\<kind\>*/*\<namespace\>*/*\<name\>*

:   Creates a role in Developer Hub.

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `body`  | The `memberReferences`,       | Request | Required        |
    |         | `group`, `namespace`, and     | body    |                 |
    |         | `name` the new role to be     |         |                 |
    |         | created.                      |         |                 |
    +---------+-------------------------------+---------+-----------------+

    : Request parameters

    :::: formalpara
    ::: title
    Example request body (JSON)
    :::

    ``` json
    {
      "memberReferences": ["group:default/test"],
      "name": "role:default/test_admin"
    }
    ```
    ::::

    :::: formalpara
    ::: title
    Example response
    :::

        201 Created
    ::::

\[PUT\] /api/permission/roles/*\<kind\>*/*\<namespace\>*/*\<name\>*

:   Updates `memberReferences`, `kind`, `namespace`, or `name` for a
    role in Developer Hub.

    :::: formalpara
    ::: title
    Request parameters
    :::

    The request body contains the `oldRole` and `newRole` objects:
    ::::

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `body`  | The `memberReferences`,       | Request | Required        |
    |         | `group`, `namespace`, and     | body    |                 |
    |         | `name` the new role to be     |         |                 |
    |         | created.                      |         |                 |
    +---------+-------------------------------+---------+-----------------+

    :::: formalpara
    ::: title
    Example request body (JSON)
    :::

    ``` json
    {
      "oldRole": {
        "memberReferences": ["group:default/test"],
        "name": "role:default/test_admin"
      },
      "newRole": {
        "memberReferences": ["group:default/test", "user:default/test2"],
        "name": "role:default/test_admin"
      }
    }
    ```
    ::::

    :::: formalpara
    ::: title
    Example response
    :::

        200 OK
    ::::

\[DELETE\] /api/permission/roles/*\<kind\>*/*\<namespace\>*/*\<name\>*?memberReferences=\<VALUE\>

:   Deletes the specified user or group from a role in Developer Hub.

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `kind`  | Kind of the entity            | String  | Required        |
    +---------+-------------------------------+---------+-----------------+
    | `nam    | Namespace of the entity       | String  | Required        |
    | espace` |                               |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `name`  | Name of the entity            | String  | Required        |
    +---------+-------------------------------+---------+-----------------+
    | `mem    | Associated group information  | String  | Required        |
    | berRefe |                               |         |                 |
    | rences` |                               |         |                 |
    +---------+-------------------------------+---------+-----------------+

    : Request parameters

    :::: formalpara
    ::: title
    Example response
    :::

        204
    ::::

\[DELETE\] /api/permission/roles/*\<kind\>*/*\<namespace\>*/*\<name\>*

:   Deletes a specified role from Developer Hub.

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `kind`  | Kind of the entity            | String  | Required        |
    +---------+-------------------------------+---------+-----------------+
    | `nam    | Namespace of the entity       | String  | Required        |
    | espace` |                               |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `name`  | Name of the entity            | String  | Required        |
    +---------+-------------------------------+---------+-----------------+

    : Request parameters

    :::: formalpara
    ::: title
    Example response
    :::

        204
    ::::

#### Permission policies {#_permission-policies}

The RBAC REST API supports the following endpoints for managing
permission policies in the Red Hat Developer Hub.

\[GET\] /api/permission/policies

:   Returns permission policies list for all users.

    :::: formalpara
    ::: title
    Example response (JSON)
    :::

    ``` json
    [
      {
        "entityReference": "role:default/test",
        "permission": "catalog-entity",
        "policy": "read",
        "effect": "allow",
        "metadata": {
          "source": "csv-file"
        }
      },
      {
        "entityReference": "role:default/test",
        "permission": "catalog.entity.create",
        "policy": "use",
        "effect": "allow",
        "metadata": {
          "source": "csv-file"
        }
      },
    ]
    ```
    ::::

\[GET\] /api/permission/policies/*\<kind\>*/*\<namespace\>*/*\<name\>*

:   Returns permission policies related to the specified entity
    reference.

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `kind`  | Kind of the entity            | String  | Required        |
    +---------+-------------------------------+---------+-----------------+
    | `nam    | Namespace of the entity       | String  | Required        |
    | espace` |                               |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `name`  | Name related to the entity    | String  | Required        |
    +---------+-------------------------------+---------+-----------------+

    : Request parameters

    :::: formalpara
    ::: title
    Example response (JSON)
    :::

    ``` json
    [
      {
        "entityReference": "role:default/test",
        "permission": "catalog-entity",
        "policy": "read",
        "effect": "allow",
        "metadata": {
          "source": "csv-file"
        }
      },
      {
        "entityReference": "role:default/test",
        "permission": "catalog.entity.create",
        "policy": "use",
        "effect": "allow",
        "metadata": {
          "source": "csv-file"
        }
      }
    ]
    ```
    ::::

\[POST\] /api/permission/policies

:   Creates a permission policy for a specified entity.

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `en     | Reference values of an entity | String  | Required        |
    | tityRef | including `kind`,             |         |                 |
    | erence` | `namespace`, and `name`       |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `perm   | Permission from a specific    | String  | Required        |
    | ission` | plugin, resource type, or     |         |                 |
    |         | name                          |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `       | Policy action for the         | String  | Required        |
    | policy` | permission, such as `create`, |         |                 |
    |         | `read`, `update`, `delete`,   |         |                 |
    |         | or `use`                      |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `       | Indication of allowing or not | String  | Required        |
    | effect` | allowing the policy           |         |                 |
    +---------+-------------------------------+---------+-----------------+

    : Request parameters

    :::: formalpara
    ::: title
    Example request body (JSON)
    :::

    ``` json
    [
      {
        "entityReference": "role:default/test",
        "permission": "catalog-entity",
        "policy": "read",
        "effect": "allow"
      }
    ]
    ```
    ::::

    :::: formalpara
    ::: title
    Example response
    :::

        201 Created
    ::::

\[PUT\] /api/permission/policies/*\<kind\>*/*\<namespace\>*/*\<name\>*

:   Updates a permission policy for a specified entity.

    :::: formalpara
    ::: title
    Request parameters
    :::

    The request body contains the `oldPolicy` and `newPolicy` objects:
    ::::

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `perm   | Permission from a specific    | String  | Required        |
    | ission` | plugin, resource type, or     |         |                 |
    |         | name                          |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `       | Policy action for the         | String  | Required        |
    | policy` | permission, such as `create`, |         |                 |
    |         | `read`, `update`, `delete`,   |         |                 |
    |         | or `use`                      |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `       | Indication of allowing or not | String  | Required        |
    | effect` | allowing the policy           |         |                 |
    +---------+-------------------------------+---------+-----------------+

    :::: formalpara
    ::: title
    Example request body (JSON)
    :::

    ``` json
    {
      "oldPolicy": [
        {
          "permission": "catalog-entity",
          "policy": "read",
          "effect": "allow"
        },
        {
          "permission": "catalog.entity.create",
          "policy": "create",
          "effect": "allow"
        }
      ],
      "newPolicy": [
        {
          "permission": "catalog-entity",
          "policy": "read",
          "effect": "deny"
        },
        {
          "permission": "policy-entity",
          "policy": "read",
          "effect": "allow"
        }
      ]
    }
    ```
    ::::

    :::: formalpara
    ::: title
    Example response
    :::

        200
    ::::

\[DELETE\] /api/permission/policies/*\<kind\>*/*\<namespace\>*/*\<name\>*?permission={value1}&policy={value2}&effect={value3}

:   Deletes a permission policy added to the specified entity.

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `kind`  | Kind of the entity            | String  | Required        |
    +---------+-------------------------------+---------+-----------------+
    | `nam    | Namespace of the entity       | String  | Required        |
    | espace` |                               |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `name`  | Name related to the entity    | String  | Required        |
    +---------+-------------------------------+---------+-----------------+
    | `perm   | Permission from a specific    | String  | Required        |
    | ission` | plugin, resource type, or     |         |                 |
    |         | name                          |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `       | Policy action for the         | String  | Required        |
    | policy` | permission, such as `create`, |         |                 |
    |         | `read`, `update`, `delete`,   |         |                 |
    |         | or `use`                      |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `       | Indication of allowing or not | String  | Required        |
    | effect` | allowing the policy           |         |                 |
    +---------+-------------------------------+---------+-----------------+

    : Request parameters

    :::: formalpara
    ::: title
    Example response
    :::

        204 No Content
    ::::

\[DELETE\] /api/permission/policies/*\<kind\>*/*\<namespace\>*/*\<name\>*

:   Deletes all permission policies added to the specified entity.

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `kind`  | Kind of the entity            | String  | Required        |
    +---------+-------------------------------+---------+-----------------+
    | `nam    | Namespace of the entity       | String  | Required        |
    | espace` |                               |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `name`  | Name related to the entity    | String  | Required        |
    +---------+-------------------------------+---------+-----------------+

    : Request parameters

    :::: formalpara
    ::: title
    Example response
    :::

        204 No Content
    ::::

\[GET\] /api/permission/plugins/policies

:   Returns permission policies for all static plugins.

    :::: formalpara
    ::: title
    Example response (JSON)
    :::

    ``` json
    [
      {
        "pluginId": "catalog",
        "policies": [
          {
            "isResourced": true,
            "permission": "catalog-entity",
            "policy": "read"
          },
          {
            "isResourced": false,
            "permission": "catalog.entity.create",
            "policy": "create"
          },
          {
            "isResourced": true,
            "permission": "catalog-entity",
            "policy": "delete"
          },
          {
            "isResourced": true,
            "permission": "catalog-entity",
            "policy": "update"
          },
          {
            "isResourced": false,
            "permission": "catalog.location.read",
            "policy": "read"
          },
          {
            "isResourced": false,
            "permission": "catalog.location.create",
            "policy": "create"
          },
          {
            "isResourced": false,
            "permission": "catalog.location.delete",
            "policy": "delete"
          }
        ]
      },
      ...
    ]
    ```
    ::::

#### Conditional policies {#_conditional-policies}

The RBAC REST API supports the following endpoints for managing
conditional policies in the Red Hat Developer Hub.

\[GET\] /api/permission/plugins/condition-rules

:   Returns available conditional rule parameter schemas for the
    available plugins that are enabled in Developer Hub.

    :::: formalpara
    ::: title
    Example response (JSON)
    :::

    ``` json
    [
       {
          "pluginId": "catalog",
          "rules": [
             {
                "name": "HAS_ANNOTATION",
                "description": "Allow entities with the specified annotation",
                "resourceType": "catalog-entity",
                "paramsSchema": {
                   "type": "object",
                   "properties": {
                      "annotation": {
                         "type": "string",
                         "description": "Name of the annotation to match on"
                      },
                      "value": {
                         "type": "string",
                         "description": "Value of the annotation to match on"
                      }
                   },
                   "required": [
                      "annotation"
                   ],
                   "additionalProperties": false,
                   "$schema": "http://json-schema.org/draft-07/schema#"
                }
             },
             {
                "name": "HAS_LABEL",
                "description": "Allow entities with the specified label",
                "resourceType": "catalog-entity",
                "paramsSchema": {
                   "type": "object",
                   "properties": {
                      "label": {
                         "type": "string",
                         "description": "Name of the label to match on"
                      }
                   },
                   "required": [
                      "label"
                   ],
                   "additionalProperties": false,
                   "$schema": "http://json-schema.org/draft-07/schema#"
                }
             },
             {
                "name": "HAS_METADATA",
                "description": "Allow entities with the specified metadata subfield",
                "resourceType": "catalog-entity",
                "paramsSchema": {
                   "type": "object",
                   "properties": {
                      "key": {
                         "type": "string",
                         "description": "Property within the entities metadata to match on"
                      },
                      "value": {
                         "type": "string",
                         "description": "Value of the given property to match on"
                      }
                   },
                   "required": [
                      "key"
                   ],
                   "additionalProperties": false,
                   "$schema": "http://json-schema.org/draft-07/schema#"
                }
             },
             {
                "name": "HAS_SPEC",
                "description": "Allow entities with the specified spec subfield",
                "resourceType": "catalog-entity",
                "paramsSchema": {
                   "type": "object",
                   "properties": {
                      "key": {
                         "type": "string",
                         "description": "Property within the entities spec to match on"
                      },
                      "value": {
                         "type": "string",
                         "description": "Value of the given property to match on"
                      }
                   },
                   "required": [
                      "key"
                   ],
                   "additionalProperties": false,
                   "$schema": "http://json-schema.org/draft-07/schema#"
                }
             },
             {
                "name": "IS_ENTITY_KIND",
                "description": "Allow entities matching a specified kind",
                "resourceType": "catalog-entity",
                "paramsSchema": {
                   "type": "object",
                   "properties": {
                      "kinds": {
                         "type": "array",
                         "items": {
                            "type": "string"
                         },
                         "description": "List of kinds to match at least one of"
                      }
                   },
                   "required": [
                      "kinds"
                   ],
                   "additionalProperties": false,
                   "$schema": "http://json-schema.org/draft-07/schema#"
                }
             },
             {
                "name": "IS_ENTITY_OWNER",
                "description": "Allow entities owned by a specified claim",
                "resourceType": "catalog-entity",
                "paramsSchema": {
                   "type": "object",
                   "properties": {
                      "claims": {
                         "type": "array",
                         "items": {
                            "type": "string"
                         },
                         "description": "List of claims to match at least one on within ownedBy"
                      }
                   },
                   "required": [
                      "claims"
                   ],
                   "additionalProperties": false,
                   "$schema": "http://json-schema.org/draft-07/schema#"
                }
             }
          ]
       }
       ... <another plugin condition parameter schemas>
    ]
    ```
    ::::

\[GET\] /api/permission/roles/conditions/:id

:   Returns conditions for the specified ID.

    :::: formalpara
    ::: title
    Example response (JSON)
    :::

    ``` json
    {
      "id": 1,
      "result": "CONDITIONAL",
      "roleEntityRef": "role:default/test",
      "pluginId": "catalog",
      "resourceType": "catalog-entity",
      "permissionMapping": ["read"],
      "conditions": {
        "anyOf": [
          {
            "rule": "IS_ENTITY_OWNER",
            "resourceType": "catalog-entity",
            "params": {
              "claims": ["group:default/team-a"]
            }
          },
          {
            "rule": "IS_ENTITY_KIND",
            "resourceType": "catalog-entity",
            "params": {
              "kinds": ["Group"]
            }
          }
        ]
      }
    }
    ```
    ::::

\[GET\] /api/permission/roles/conditions

:   Returns list of all conditions for all roles.

    :::: formalpara
    ::: title
    Example response (JSON)
    :::

    ``` json
    [
      {
        "id": 1,
        "result": "CONDITIONAL",
        "roleEntityRef": "role:default/test",
        "pluginId": "catalog",
        "resourceType": "catalog-entity",
        "permissionMapping": ["read"],
        "conditions": {
          "anyOf": [
            {
              "rule": "IS_ENTITY_OWNER",
              "resourceType": "catalog-entity",
              "params": {
                "claims": ["group:default/team-a"]
              }
            },
            {
              "rule": "IS_ENTITY_KIND",
              "resourceType": "catalog-entity",
              "params": {
                "kinds": ["Group"]
              }
            }
          ]
        }
      }
    ]
    ```
    ::::

\[POST\] /api/permission/roles/conditions

:   Creates a conditional policy for the specified role.

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `       | Always has the value          | String  | Required        |
    | result` | `CONDITIONAL`                 |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `       | String entity reference to    | String  | Required        |
    | roleEnt | the RBAC role, such as        |         |                 |
    | ityRef` | `role:default/dev`            |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `pl     | Corresponding plugin ID, such | String  | Required        |
    | uginId` | as `catalog`                  |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `perm   | Array permission action, such | String  | Required        |
    | issionM | as                            | array   |                 |
    | apping` | `                             |         |                 |
    |         | ['read', 'update', 'delete']` |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `resour | Resource type provided by the | String  | Required        |
    | ceType` | plugin, such as               |         |                 |
    |         | `catalog-entity`              |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `cond   | Condition JSON with           | JSON    | Required        |
    | itions` | parameters or array           |         |                 |
    |         | parameters joined by criteria |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `name`  | Name of the role              | String  | Required        |
    +---------+-------------------------------+---------+-----------------+
    | `       | The description of the role   | String  | Optional        |
    | metadat |                               |         |                 |
    | a.descr |                               |         |                 |
    | iption` |                               |         |                 |
    +---------+-------------------------------+---------+-----------------+

    : Request parameters

    :::: formalpara
    ::: title
    Example request body (JSON)
    :::

    ``` json
    {
      "result": "CONDITIONAL",
      "roleEntityRef": "role:default/test",
      "pluginId": "catalog",
      "resourceType": "catalog-entity",
      "permissionMapping": ["read"],
      "conditions": {
        "rule": "IS_ENTITY_OWNER",
        "resourceType": "catalog-entity",
        "params": {
          "claims": ["group:default/team-a"]
        }
      }
    }
    ```
    ::::

    :::: formalpara
    ::: title
    Example response (JSON)
    :::

    ``` json
    {
      "id": 1
    }
    ```
    ::::

\[PUT\] /permission/roles/conditions/:id

:   Updates a condition policy for a specified ID.

    +---------+-------------------------------+---------+-----------------+
    | Name    | Description                   | Type    | Presence        |
    +=========+===============================+=========+=================+
    | `       | Always has the value          | String  | Required        |
    | result` | `CONDITIONAL`                 |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `       | String entity reference to    | String  | Required        |
    | roleEnt | the RBAC role, such as        |         |                 |
    | ityRef` | `role:default/dev`            |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `pl     | Corresponding plugin ID, such | String  | Required        |
    | uginId` | as `catalog`                  |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `perm   | Array permission action, such | String  | Required        |
    | issionM | as                            | array   |                 |
    | apping` | `                             |         |                 |
    |         | ['read', 'update', 'delete']` |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `resour | Resource type provided by the | String  | Required        |
    | ceType` | plugin, such as               |         |                 |
    |         | `catalog-entity`              |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `cond   | Condition JSON with           | JSON    | Required        |
    | itions` | parameters or array           |         |                 |
    |         | parameters joined by criteria |         |                 |
    +---------+-------------------------------+---------+-----------------+
    | `name`  | Name of the role              | String  | Required        |
    +---------+-------------------------------+---------+-----------------+
    | `       | The description of the role   | String  | Optional        |
    | metadat |                               |         |                 |
    | a.descr |                               |         |                 |
    | iption` |                               |         |                 |
    +---------+-------------------------------+---------+-----------------+

    : Request parameters

    :::: formalpara
    ::: title
    Example request body (JSON)
    :::

    ``` json
    {
      "result": "CONDITIONAL",
      "roleEntityRef": "role:default/test",
      "pluginId": "catalog",
      "resourceType": "catalog-entity",
      "permissionMapping": ["read"],
      "conditions": {
        "anyOf": [
          {
            "rule": "IS_ENTITY_OWNER",
            "resourceType": "catalog-entity",
            "params": {
              "claims": ["group:default/team-a"]
            }
          },
          {
            "rule": "IS_ENTITY_KIND",
            "resourceType": "catalog-entity",
            "params": {
              "kinds": ["Group"]
            }
          }
        ]
      }
    }
    ```
    ::::

    :::: formalpara
    ::: title
    Example response
    :::

        200
    ::::

\[DELETE\] /api/permission/roles/conditions/:id

:   Deletes a conditional policy for the specified ID.

    :::: formalpara
    ::: title
    Example response
    :::

        204
    ::::

#### User statistics {#_user-statistics}

The `licensed-users-info-backend` plugin exposes various REST API
endpoints to retrieve data related to logged-in users.

No additional configuration is required for the
`licensed-users-info-backend` plugin. If the RBAC backend plugin is
enabled, then an administrator role must be assigned to access the
endpoints, as the endpoints are protected by the `policy.entity.read`
permission.

The base URL for user statistics endpoints is
`http://SERVER:PORT/api/licensed-users-info`, such as
`http://localhost:7007/api/licensed-users-info`.

\[GET\] /users/quantity

:   Returns the total number of logged-in users.

    :::: formalpara
    ::: title
    Example request
    :::

    ``` bash
    curl -X GET "http://localhost:7007/api/licensed-users-info/users/quantity" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token"
    ```
    ::::

    :::: formalpara
    ::: title
    Example response
    :::

    ``` json
    { "quantity": "2" }
    ```
    ::::

\[GET\] /users

:   Returns a list of logged-in users with their details.

    :::: formalpara
    ::: title
    Example request
    :::

    ``` bash
    curl -X GET "http://localhost:7007/api/licensed-users-info/users" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token"
    ```
    ::::

    :::: formalpara
    ::: title
    Example response
    :::

    ``` json
    [
      {
        "userEntityRef": "user:default/dev",
        "lastTimeLogin": "Thu, 22 Aug 2024 16:27:41 GMT",
        "displayName": "John Leavy",
        "email": "dev@redhat.com"
      }
    ]
    ```
    ::::

\[GET\] /users

:   Returns a list of logged-in users in CSV format.

    :::: formalpara
    ::: title
    Example request
    :::

    ``` bash
    curl -X GET "http://localhost:7007/api/licensed-users-info/users" \
    -H "Content-Type: text/csv" \
    -H "Authorization: Bearer $token"
    ```
    ::::

    :::: formalpara
    ::: title
    Example response
    :::

    ``` csv
    userEntityRef,displayName,email,lastTimeLogin
    user:default/dev,John Leavy,dev@redhat.com,"Thu, 22 Aug 2024 16:27:41 GMT"
    ```
    ::::

## Managing authorizations by using external files

To automate Red Hat Developer Hub maintenance, you can configure
permissions and roles in external files, before starting Developer Hub.

### Defining authorizations in external files by using the operator

To automate Red Hat Developer Hub maintenance, you can define
permissions and roles in external files, before starting Developer Hub.
You need to prepare your files, upload them to your OpenShift Container
Platform project, and configure Developer Hub to use the external files.

<div>

::: title
Prerequisites
:::

- [You enabled the RBAC feature](#enabling-and-giving-access-to-rbac).

</div>

<div>

::: title
Procedure
:::

1.  Define your policies in a `rbac-policies.csv` CSV file by using the
    following format:

    a.  Define role permissions:

        ``` csv
        p, <role_entity_reference>, <permission>, <action>, <allow_or_deny>
        ```

        *\<role_entity_reference\>*

        :   Role entity reference, such as: `role:default/guest`.

        *\<permission\>*

        :   Permission, such as: `bulk.import`, `catalog.entity.read`,
            or `catalog.entity.refresh`, or permission resource type,
            such as: `bulk-import` or `catalog-entity`.

            See: [Permission policies
            reference](#ref-rbac-permission-policies_title-authorization).

        *\<action\>*

        :   Action type, such as: `use`, `read`, `create`, `update`,
            `delete`.

        *\<allow_or_deny\>*

        :   Access granted: `allow` or `deny`.

    b.  Assign the role to a group or a user:

        ``` csv
        g, <group_or_user>, <role_entity_reference>
        ```

        *\<group_or_user\>*

        :   Group, such as: `user:default/mygroup`, or user, such as:
            `user:default/myuser`.

            :::: formalpara
            ::: title
            Sample `rbac-policies.csv`
            :::

            ``` csv
            p, role:default/guests, catalog-entity, read, allow
            p, role:default/guests, catalog.entity.create, create, allow
            g, user:default/my-user, role:default/guests
            g, group:default/my-group, role:default/guests
            ```
            ::::

2.  Define your conditional policies in a
    `rbac-conditional-policies.yaml` YAML file by using the following
    format:

    ``` yaml
    result: CONDITIONAL
    roleEntityRef: <role_entity_reference>
    pluginId: <plugin_id>
    permissionMapping:
      - read
      - update
      - delete
    conditions: <conditions>
    ```

    See: [Conditional policies
    reference](#ref-rbac-conditional-policy-definition_title-authorization).

3.  Upload your `rbac-policies.csv` and `rbac-conditional-policies.yaml`
    files to a `rbac-policies` config map in your OpenShift Container
    Platform project containing Developer Hub.

    ``` terminal
    $ oc create configmap rbac-policies \
         --from-file=rbac-policies.csv \
         --from-file=rbac-conditional-policies.yaml
    ```

4.  Update [your `Backstage` custom
    resource](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index)
    to mount in the Developer Hub filesystem your files from the
    `rbac-policies` config map:

    :::: formalpara
    ::: title
    `Backstage` custom resource fragment
    :::

    ``` yaml
    apiVersion: rhdh.redhat.com/v1alpha3
    kind: Backstage
    spec:
      application:
        extraFiles:
          mountPath: /opt/app-root/src
          configMaps:
            - name: rbac-policies
    ```
    ::::

5.  Update your Developer Hub `app-config.yaml` configuration file to
    use the `rbac-policies.csv` and `rbac-conditional-policies.yaml`
    external files:

    :::: formalpara
    ::: title
    `app-config.yaml` file fragment
    :::

    ``` yaml
    permission:
      enabled: true
      rbac:
        conditionalPoliciesFile: /opt/app-root/src/rbac-conditional-policies.yaml
        policies-csv-file: /opt/app-root/src/rbac-policies.csv
        policyFileReload: true
    ```
    ::::

</div>

### Defining authorizations in external files by using Helm

To automate Red Hat Developer Hub maintenance, you can define
permissions and roles in external files, before starting Developer Hub.
You need to prepare your files, upload them to your OpenShift Container
Platform project, and configure Developer Hub to use the external files.

<div>

::: title
Prerequisites
:::

- [You enabled the RBAC feature](#enabling-and-giving-access-to-rbac).

</div>

<div>

::: title
Procedure
:::

1.  Define your policies in a `rbac-policies.csv` CSV file by using the
    following format:

    a.  Define role permissions:

        ``` csv
        p, <role_entity_reference>, <permission>, <action>, <allow_or_deny>
        ```

        *\<role_entity_reference\>*

        :   Role entity reference, such as: `role:default/guest`.

        *\<permission\>*

        :   Permission, such as: `bulk.import`, `catalog.entity.read`,
            or `catalog.entity.refresh`, or permission resource type,
            such as: `bulk-import` or `catalog-entity`.

            See: [Permission policies
            reference](#ref-rbac-permission-policies_title-authorization).

        *\<action\>*

        :   Action type, such as: `use`, `read`, `create`, `update`,
            `delete`.

        *\<allow_or_deny\>*

        :   Access granted: `allow` or `deny`.

    b.  Assign the role to a group or a user:

        ``` csv
        g, <group_or_user>, <role_entity_reference>
        ```

        *\<group_or_user\>*

        :   Group, such as: `user:default/mygroup`, or user, such as:
            `user:default/myuser`.

            :::: formalpara
            ::: title
            Sample `rbac-policies.csv`
            :::

            ``` csv
            p, role:default/guests, catalog-entity, read, allow
            p, role:default/guests, catalog.entity.create, create, allow
            g, user:default/my-user, role:default/guests
            g, group:default/my-group, role:default/guests
            ```
            ::::

2.  Define your conditional policies in a
    `rbac-conditional-policies.yaml` YAML file by using the following
    format:

    ``` yaml
    result: CONDITIONAL
    roleEntityRef: <role_entity_reference>
    pluginId: <plugin_id>
    permissionMapping:
      - read
      - update
      - delete
    conditions: <conditions>
    ```

    See: [Conditional policies
    reference](#ref-rbac-conditional-policy-definition_title-authorization).

3.  Upload your `rbac-policies.csv` and `rbac-conditional-policies.yaml`
    files to a `rbac-policies` config map in your OpenShift Container
    Platform project containing Developer Hub.

    ``` terminal
    $ oc create configmap rbac-policies \
         --from-file=rbac-policies.csv \
         --from-file=rbac-conditional-policies.yaml
    ```

4.  Update your Developer Hub `Backstage` Helm chart to mount in the
    Developer Hub filesystem your files from the `rbac-policies` config
    map:

    a.  In the Developer Hub Helm Chart, go to **Root Schema → Backstage
        chart schema → Backstage parameters → Backstage container
        additional volume mounts**.

    b.  Select **Add Backstage container additional volume mounts** and
        add the following values:

        mountPath

        :   `/opt/app-root/src/rbac`

        Name

        :   `rbac-policies`

    c.  Add the RBAC policy to the **Backstage container additional
        volumes** in the Developer Hub Helm Chart:

        name

        :   `rbac-policies`

        configMap

        :

            defaultMode

            :   `420`

            name

            :   `rbac-policies`

5.  Update your Developer Hub `app-config.yaml` configuration file to
    use the `rbac-policies.csv` and `rbac-conditional-policies.yaml`
    external files:

    :::: formalpara
    ::: title
    `app-config.yaml` file fragment
    :::

    ``` yaml
    permission:
      enabled: true
      rbac:
        conditionalPoliciesFile: /opt/app-root/src/rbac-conditional-policies.yaml
        policies-csv-file: /opt/app-root/src/rbac-policies.csv
        policyFileReload: true
    ```
    ::::

</div>

## Configuring guest access with RBAC UI {#configuring-guest-access-with-rbac-ui_title-authorization}

Use guest access with the role-based access control (RBAC) front-end
plugin to allow a user to test role and policy creation without the need
to set up and configure an authentication provider.

:::: note
::: title
:::

Guest access is not recommended for production.
::::

### Configuring the RBAC backend plugin {#configuring-the-rbac-backend-plugin_title-authorization}

You can configure the RBAC backend plugin by updating the
`app-config.yaml` file to enable the permission framework.

<div>

::: title
Prerequisites
:::

- You have installed the `@janus-idp/backstage-plugin-rbac` plugin in
  Developer Hub. For more information, see
  [{plugins-configure-book-title}]({plugins-configure-book-url}).

</div>

<div>

::: title
Procedure
:::

- Update the `app-config.yaml` file to enable the permission framework
  as shown:

</div>

``` yaml
permission
  enabled: true
  rbac:
    admin:
      users:
        - name: user:default/guest
    pluginsWithPermission:
      - catalog
      - permission
      - scaffolder
```

:::: note
::: title
:::

The `pluginsWithPermission` section of the `app-config.yaml` file
includes only three plugins by default. Update the section as needed to
include any additional plugins that also incorporate permissions.
::::

### Setting up the guest authentication provider {#setting-up-the-guest-authentication-provider_title-authorization}

You can enable guest authentication and use it alongside the RBAC
frontend plugin.

<div>

::: title
Prerequisites
:::

- You have installed the `@janus-idp/backstage-plugin-rbac` plugin in
  Developer Hub. For more information, see
  [{plugins-configure-book-title}]({plugins-configure-book-url}).

</div>

<div>

::: title
Procedure
:::

- In the `app-config.yaml` file, add the user entity reference to
  resolve and enable the `dangerouslyAllowOutsideDevelopment` option, as
  shown in the following example:

</div>

``` yaml
auth:
  environment: development
  providers:
    guest:
      userEntityRef: user:default/guest
      dangerouslyAllowOutsideDevelopment: true
```

:::: note
::: title
:::

You can use `user:default/guest` as the user entity reference to match
the added user under the `permission.rbac.admin.users` section of the
`app-config.yaml` file.
::::

## Delegating role-based access controls (RBAC) access in Red Hat Developer Hub {#proc-delegating-rbac-access_title-authorization}

An enterprise customer requires the ability to delegate role-based
access control (RBAC) responsibilities to other individuals in the
organization. In this scenario, you, as the administrator, can provide
access to the RBAC plugin specifically to designated users, such as team
leads. Each team lead is then able to manage permissions exclusively for
users within their respective team or department, without visibility
into or control over permissions outside their assigned scope. This
approach allows team leads to manage access and permissions for their
own teams independently, while administrators maintain global oversight.

In RHDH, you can delegate RBAC access using the multitenancy feature of
RBAC plugin, specifically the `IS_OWNER` conditional rule.

By delegating the RBAC access, you can expect the following outcomes:

- Team leads can manage RBAC settings for their teams independently.

- Visibility of other users\' or teams\' permissions is restricted.

- Administrators retain overarching control while delegating
  team-specific access.

<div>

::: title
Prerequisites
:::

- Your RHDH instance is up and running with RBAC plugin installed and
  configured.

- You have administrative access to RHDH.

- You have API access using `curl` or another tool.

</div>

<div>

::: title
Procedure
:::

1.  In your RHDH instance, navigate to the **Administration → RBAC**
    page.

2.  Create a new role designated for team leads using the Web UI or API:

    :::: formalpara
    ::: title
    Example of creating a new role for the team lead using the RBAC
    backend API
    :::

    ``` bash
    curl -X POST 'http://localhost:7007/api/permission/roles' \
    --header "Authorization: Bearer $ADMIN_TOKEN" \
    --header "Content-Type: application/json" \
    --data '{
      "memberReferences": ["user:default/team_lead"],
      "name": "role:default/team_lead",
      "metadata": {
        "description": "This is an example team lead role"
      }
    }'
    ```
    ::::

    For more information about creating a role using the Web UI, see
    [Creating a role in the Red Hat Developer Hub Web
    UI](#proc-rbac-ui-create-role_title-authorization).

3.  Allow team leads to read catalog entities and create permissions in
    the RBAC plugin using the Web UI or the following API request:

    :::: formalpara
    ::: title
    Example of granting the team lead role permission to create RBAC
    policies and read catalog entities
    :::

    ``` bash
    curl -X POST 'http://localhost:7007/api/permission/policies' \
    --header "Authorization: Bearer $ADMIN_TOKEN" \
    --header "Content-Type: application/json" \
    --data '[
      {
        "entityReference": "role:default/team_lead",
        "permission": "policy.entity.create",
        "policy": "create",
        "effect": "allow"
      },
      {
        "entityReference": "role:default/team_lead",
        "permission": "catalog-entity",
        "policy": "read",
        "effect": "allow"
      }
    ]'
    ```
    ::::

4.  To ensure team leads can only manage what they own, use the
    `IS_OWNER` conditional rule as follows:

    :::: formalpara
    ::: title
    Example `curl` of applying a conditional access policy using the
    `IS_OWNER` rule for the team lead role
    :::

    ``` bash
    curl -X POST 'http://localhost:7007/api/permission/roles/conditions' \
    --header "Authorization: Bearer $ADMIN_TOKEN" \
    --header "Content-Type: application/json" \
    --data '{
     "result": "CONDITIONAL",
     "pluginId": "permission",
     "resourceType": "policy-entity",
     "conditions": {
       "rule": "IS_OWNER",
       "resourceType": "policy-entity",
       "params": {
         "owners": [
           "user:default/team_lead"
         ]
       }
     },
     "roleEntityRef": "role:default/team_lead",
     "permissionMapping": [
       "read",
       "update",
       "delete"
     ]
    }'
    ```
    ::::

    The previous example of conditional policy limits visibility and
    control to only owned roles and policies.

5.  Log in to RHDH as team lead and verify the following:

    a.  Use the following request and verify that you do not see any
        roles:

        :::: formalpara
        ::: title
        Example `curl` to retrieve roles visible to the team lead
        :::

        ``` bash
        curl -X GET 'http://localhost:7007/api/permission/roles' \
        --header "Authorization: Bearer $TEAM_LEAD_TOKEN"
        ```
        ::::

    b.  Use the following request to create a new role for their team:

        :::: formalpara
        ::: title
        Example `curl` of team lead creating a new role for their team
        with ownership assigned
        :::

        ``` bash
        curl -X POST 'http://localhost:7007/api/permission/roles' \
        --header "Authorization: Bearer $TEAM_LEAD_TOKEN" \
        --header "Content-Type: application/json" \
        --data '{
          "memberReferences": ["user:default/team_member"],
          "name": "role:default/team_a",
          "metadata": {
            "description": "This is an example team_a role",
            "owner": "user:default/team_lead"
          }
        }'
        ```
        ::::

        :::: note
        ::: title
        :::

        You can set the ownership during creation, but you can also
        update the ownership at any time.
        ::::

    c.  Use the following request to assign a permission policy to the
        new role:

        :::: formalpara
        ::: title
        Example `curl` for granting read access to catalog entities for
        the new role
        :::

        ``` bash
        curl -X POST 'http://localhost:7007/api/permission/policies' \
        --header "Authorization: Bearer $ADMIN_TOKEN" \
        --header "Content-Type: application/json" \
        --data '[
          {
            "entityReference": "role:default/team_a",
            "permission": "catalog-entity",
            "policy": "read",
            "effect": "allow"
          }
        ]'
        ```
        ::::

    d.  Use the following request to verify that only team-owned roles
        and policies are visible:

        :::: formalpara
        ::: title
        Example `curl` to retrieve roles and permission policies visible
        to the team lead
        :::

        ``` bash
        curl -X GET 'http://localhost:7007/api/permission/roles' \
        --header "Authorization: Bearer $TEAM_LEAD_TOKEN"

        curl -X GET 'http://localhost:7007/api/permission/policies' \
        --header "Authorization: Bearer $TEAM_LEAD_TOKEN"
        ```
        ::::

</div>

<div>

::: title
Verification
:::

- Log in as a team lead and verify the following:

  - The RBAC UI is accessible.

  - Only the assigned users or group is visible.

  - Permissions outside the scoped team are not viewable or editable.

- Log in as an administrator and verify that you retain full visibility
  and control.

</div>

## Permission policies reference {#ref-rbac-permission-policies_title-authorization}

Permission policies in Red Hat Developer Hub are a set of rules to
govern access to resources or functionalities. These policies state the
authorization level that is granted to users based on their roles. The
permission policies are implemented to maintain security and
confidentiality within a given environment.

You can define the following types of permissions in Developer Hub:

- resource type

- basic

The distinction between the two permission types depends on whether a
permission includes a defined resource type.

You can define the resource type permission using either the associated
resource type or the permission name as shown in the following example:

:::: formalpara
::: title
Example resource type permission definition
:::

``` csv
p, role:default/myrole, catalog.entity.read, read, allow
g, user:default/myuser, role:default/myrole

p, role:default/another-role, catalog-entity, read, allow
g, user:default/another-user, role:default/another-role
```
::::

You can define the basic permission in Developer Hub using the
permission name as shown in the following example:

:::: formalpara
::: title
Example basic permission definition
:::

``` csv
p, role:default/myrole, catalog.entity.create, create, allow
g, user:default/myuser, role:default/myrole
```
::::

Developer Hub supports following permission policies:

Catalog permissions

:   .Catalog permissions

+---------+-----------------+---------+-------------------------------+
| Name    | Resource type   | Policy  | Description                   |
+=========+=================+=========+===============================+
| `catalo | `               | `read`  | Allows a user or role to read |
| g.entit | catalog-entity` |         | from the catalog              |
| y.read` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `c      |                 | `       | Allows a user or role to      |
| atalog. |                 | create` | create catalog entities,      |
| entity. |                 |         | including registering an      |
| create` |                 |         | existing component in the     |
|         |                 |         | catalog                       |
+---------+-----------------+---------+-------------------------------+
| `ca     | `               | `       | Allows a user or role to      |
| talog.e | catalog-entity` | update` | refresh a single or multiple  |
| ntity.r |                 |         | entities from the catalog     |
| efresh` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `c      | `               | `       | Allows a user or role to      |
| atalog. | catalog-entity` | delete` | delete a single or multiple   |
| entity. |                 |         | entities from the catalog     |
| delete` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `c      |                 | `read`  | Allows a user or role to read |
| atalog. |                 |         | a single or multiple          |
| locatio |                 |         | locations from the catalog    |
| n.read` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `cat    |                 | `       | Allows a user or role to      |
| alog.lo |                 | create` | create locations within the   |
| cation. |                 |         | catalog                       |
| create` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `cat    |                 | `       | Allows a user or role to      |
| alog.lo |                 | delete` | delete locations from the     |
| cation. |                 |         | catalog                       |
| delete` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+

Bulk import permission

:   .Bulk import permission

+---------+-----------------+---------+-------------------------------+
| Name    | Resource type   | Policy  | Description                   |
+=========+=================+=========+===============================+
| `bulk.  | `bulk-import`   | `use`   | Allows the user to access the |
| import` |                 |         | bulk import endpoints, such   |
|         |                 |         | as listing all repositories   |
|         |                 |         | and organizations accessible  |
|         |                 |         | by all GitHub integrations    |
|         |                 |         | and managing the import       |
|         |                 |         | requests                      |
+---------+-----------------+---------+-------------------------------+

Scaffolder permissions

:   .Scaffolder permissions

+---------+-----------------+---------+-------------------------------+
| Name    | Resource type   | Policy  | Description                   |
+=========+=================+=========+===============================+
| `scaff  | `sca            | `use`   | Allows the execution of an    |
| older.a | ffolder-action` |         | action from a template        |
| ction.e |                 |         |                               |
| xecute` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `       | `scaff          | `read`  | Allows a user or role to read |
| scaffol | older-template` |         | a single or multiple one      |
| der.tem |                 |         | parameters from a template    |
| plate.p |                 |         |                               |
| aramete |                 |         |                               |
| r.read` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `sc     | `scaff          | `read`  | Allows a user or role to read |
| affolde | older-template` |         | a single or multiple steps    |
| r.templ |                 |         | from a template               |
| ate.ste |                 |         |                               |
| p.read` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `sc     |                 | `       | Allows a user or role to      |
| affolde |                 | create` | trigger software templates    |
| r.task. |                 |         | which create new scaffolder   |
| create` |                 |         | tasks                         |
+---------+-----------------+---------+-------------------------------+
| `sc     |                 | `use`   | Allows a user or role to      |
| affolde |                 |         | cancel currently running      |
| r.task. |                 |         | scaffolder tasks              |
| cancel` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `       |                 | `read`  | Allows a user or role to read |
| scaffol |                 |         | all scaffolder tasks and      |
| der.tas |                 |         | their associated events and   |
| k.read` |                 |         | logs                          |
+---------+-----------------+---------+-------------------------------+
| `sca    |                 | `use`   | Allows a user or role to      |
| ffolder |                 |         | access frontend template      |
| .templa |                 |         | management features,          |
| te.mana |                 |         | including editing,            |
| gement` |                 |         | previewing, and trying        |
|         |                 |         | templates, forms, and custom  |
|         |                 |         | fields.                       |
+---------+-----------------+---------+-------------------------------+

RBAC permissions

:   .RBAC permissions

+---------+-----------------+---------+-------------------------------+
| Name    | Resource type   | Policy  | Description                   |
+=========+=================+=========+===============================+
| `polic  | `policy-entity` | `read`  | Allows a user or role to read |
| y.entit |                 |         | permission policies and roles |
| y.read` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `       |                 | `       | Allows a user or role to      |
| policy. |                 | create` | create a single or multiple   |
| entity. |                 |         | permission policies and roles |
| create` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `       | `policy-entity` | `       | Allows a user or role to      |
| policy. |                 | update` | update a single or multiple   |
| entity. |                 |         | permission policies and roles |
| update` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `       | `policy-entity` | `       | Allows a user or role to      |
| policy. |                 | delete` | delete a single or multiple   |
| entity. |                 |         | permission policies and roles |
| delete` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+

Kubernetes permissions

:   .Kubernetes permissions

+---------+-----------------+---------+-------------------------------+
| Name    | Resource type   | Policy  | Description                   |
+=========+=================+=========+===============================+
| `kube   |                 | `read`  | Allows a user to read         |
| rnetes. |                 |         | Kubernetes cluster details    |
| cluster |                 |         | under the `/clusters` path    |
| s.read` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `kuber  |                 | `read`  | Allows a user to read         |
| netes.r |                 |         | information about Kubernetes  |
| esource |                 |         | resources located at          |
| s.read` |                 |         | `/services/:serviceId` and    |
|         |                 |         | `/resources`                  |
+---------+-----------------+---------+-------------------------------+
| `kub    |                 | `use`   | Allows a user or role to      |
| ernetes |                 |         | access the proxy endpoint     |
| .proxy` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+

OCM permissions

:   Basic OCM permissions only restrict access to the cluster view, but
    they do not prevent access to the Kubernetes clusters in the
    resource view. For more effective permissions, consider applying a
    conditional policy to restrict access to catalog entities that are
    of type `kubernetes-cluster`. Access restriction is dependent on the
    set of permissions granted to a role. For example, if the role had
    full permissions (`read`, `update`, and `delete`), then you must
    specify all its permissions in the `permissionMapping` field.

:::: formalpara
::: title
Example permissionMapping definition
:::

``` csv
result: CONDITIONAL
roleEntityRef: 'role:default/<YOUR_ROLE>'
pluginId: catalog
resourceType: catalog-entity
permissionMapping:
  - read
  - update
  - delete
conditions:
  not:
    rule: HAS_SPEC
    resourceType: catalog-entity
    params:
      key: type
      value: kubernetes-cluster
```
::::

+---------+-----------------+---------+-------------------------------+
| Name    | Resource type   | Policy  | Description                   |
+=========+=================+=========+===============================+
| `oc     |                 | `read`  | Allows a user or role to read |
| m.entit |                 |         | from the OCM plugin           |
| y.read` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `ocm    |                 | `read`  | Allows a user or role to read |
| .cluste |                 |         | the cluster information in    |
| r.read` |                 |         | the OCM plugin                |
+---------+-----------------+---------+-------------------------------+

Topology permissions

:   .Topology permissions

+---------+-----------------+---------+-------------------------------+
| Name    | Resource type   | Policy  | Description                   |
+=========+=================+=========+===============================+
| `kube   |                 | `read`  | Allows a user to read         |
| rnetes. |                 |         | Kubernetes cluster details    |
| cluster |                 |         | under the `/clusters` path    |
| s.read` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `kuber  |                 | `read`  | Allows a user to read         |
| netes.r |                 |         | information about Kubernetes  |
| esource |                 |         | resources located at          |
| s.read` |                 |         | `/services/:serviceId` and    |
|         |                 |         | `/resources`                  |
+---------+-----------------+---------+-------------------------------+
| `kub    |                 | `use`   | Allows a user or role to      |
| ernetes |                 |         | access the proxy endpoint,    |
| .proxy` |                 |         | allowing the user or role to  |
|         |                 |         | read pod logs and events      |
|         |                 |         | within RHDH                   |
+---------+-----------------+---------+-------------------------------+

Tekton permissions

:   .Tekton permissions

+---------+-----------------+---------+-------------------------------+
| Name    | Resource type   | Policy  | Description                   |
+=========+=================+=========+===============================+
| `kube   |                 | `read`  | Allows a user to read         |
| rnetes. |                 |         | Kubernetes cluster details    |
| cluster |                 |         | under the `/clusters` path    |
| s.read` |                 |         |                               |
+---------+-----------------+---------+-------------------------------+
| `kuber  |                 | `read`  | Allows a user to read         |
| netes.r |                 |         | information about Kubernetes  |
| esource |                 |         | resources located at          |
| s.read` |                 |         | `/services/:serviceId` and    |
|         |                 |         | `/resources`                  |
+---------+-----------------+---------+-------------------------------+
| `kub    |                 | `use`   | Allows a user or role to      |
| ernetes |                 |         | access the proxy endpoint,    |
| .proxy` |                 |         | allowing the user or role to  |
|         |                 |         | read pod logs and events      |
|         |                 |         | within RHDH                   |
+---------+-----------------+---------+-------------------------------+

## Conditional policies in Red Hat Developer Hub {#con-rbac-conditional-policies-rhdh_title-authorization}

The permission framework in Red Hat Developer Hub provides conditions,
supported by the RBAC backend plugin (`backstage-plugin-rbac-backend`).
The conditions work as content filters for the Developer Hub resources
that are provided by the RBAC backend plugin.

The RBAC backend API stores conditions assigned to roles in the
database. When you request to access the frontend resources, the RBAC
backend API searches for the corresponding conditions and delegates them
to the appropriate plugin using its plugin ID. If you are assigned to
multiple roles with different conditions, then the RBAC backend merges
the conditions using the `anyOf` criteria.

Conditional criteria

:   A condition in Developer Hub is a simple condition with a rule and
    parameters. However, a condition can also contain a parameter or an
    array of parameters combined by conditional criteria. The supported
    conditional criteria includes:

    - `allOf`: Ensures that all conditions within the array must be true
      for the combined condition to be satisfied.

    - `anyOf`: Ensures that at least one of the conditions within the
      array must be true for the combined condition to be satisfied.

    - `not`: Ensures that the condition within it must not be true for
      the combined condition to be satisfied.

Conditional object

:   The plugin specifies the parameters supported for conditions. You
    can access the conditional object schema from the RBAC API endpoint
    to understand how to construct a conditional JSON object, which is
    then used by the RBAC backend plugin API.

    A conditional object contains the following parameters:

    +--------------------+-------------------------------+-----------------+
    | Parameter          | Type                          | Description     |
    +====================+===============================+=================+
    | `result`           | String                        | Always has the  |
    |                    |                               | value           |
    |                    |                               | `CONDITIONAL`   |
    +--------------------+-------------------------------+-----------------+
    | `roleEntityRef`    | String                        | String entity   |
    |                    |                               | reference to    |
    |                    |                               | the RBAC role,  |
    |                    |                               | such as         |
    |                    |                               | `ro             |
    |                    |                               | le:default/dev` |
    +--------------------+-------------------------------+-----------------+
    | `pluginId`         | String                        | Corresponding   |
    |                    |                               | plugin ID, such |
    |                    |                               | as `catalog`    |
    +--------------------+-------------------------------+-----------------+
    | `                  | String array                  | Array           |
    | permissionMapping` |                               | permission      |
    |                    |                               | actions, such   |
    |                    |                               | as              |
    |                    |                               | `['read', 'upda |
    |                    |                               | te', 'delete']` |
    +--------------------+-------------------------------+-----------------+
    | `resourceType`     | String                        | Resource type   |
    |                    |                               | provided by the |
    |                    |                               | plugin, such as |
    |                    |                               | `               |
    |                    |                               | catalog-entity` |
    +--------------------+-------------------------------+-----------------+
    | `conditions`       | JSON                          | Condition JSON  |
    |                    |                               | with parameters |
    |                    |                               | or array        |
    |                    |                               | parameters      |
    |                    |                               | joined by       |
    |                    |                               | criteria        |
    +--------------------+-------------------------------+-----------------+

    : Conditional object parameters

Conditional policy aliases

:   The RBAC backend plugin (`backstage-plugin-rbac-backend`) supports
    the use of aliases in conditional policy rule parameters. The
    conditional policy aliases are dynamically replaced with the
    corresponding values during policy evaluation. Each alias in
    conditional policy is prefixed with a `$` sign indicating its
    special function.

    The supported conditional aliases include:

    - `$currentUser`: This alias is replaced with the user entity
      reference for the user who requests access to the resource. For
      example, if user Tom from the default namespace requests access,
      `$currentUser` becomes `user:default/tom`.

:::: formalpara
::: title
Example conditional policy object with `$currentUser` alias
:::

``` json
{
  "result": "CONDITIONAL",
  "roleEntityRef": "role:default/developer",
  "pluginId": "catalog",
  "resourceType": "catalog-entity",
  "permissionMapping": ["delete"],
  "conditions": {
    "rule": "IS_ENTITY_OWNER",
    "resourceType": "catalog-entity",
    "params": {
      "claims": ["$currentUser"]
    }
  }
}
```
::::

- `$ownerRefs`: This alias is replaced with ownership references,
  usually as an array that includes the user entity reference and the
  user's parent group entity reference. For example, for user Tom from
  team-a, `$ownerRefs` becomes
  `['user:default/tom', 'group:default/team-a']`.

:::: formalpara
::: title
Example conditional policy object with `$ownerRefs` alias
:::

``` json
{
  "result": "CONDITIONAL",
  "roleEntityRef": "role:default/developer",
  "pluginId": "catalog",
  "resourceType": "catalog-entity",
  "permissionMapping": ["delete"],
  "conditions": {
    "rule": "IS_ENTITY_OWNER",
    "resourceType": "catalog-entity",
    "params": {
      "claims": ["$ownerRefs"]
    }
  }
}
```
::::

### Enabling transitive parent groups {#_enabling-transitive-parent-groups}

By default, Red Hat Developer Hub does not resolve indirect parent
groups during authentication. In this case, with the following group
hierarchy, the `user_alice` user is only a member of the
`group_developers` group:

    group_admin
      └── group_developers
        └── user_alice

To support multi-level group hierarchies when using the \$ownerRefs
alias, you can configure Developer Hub to include indirect parent groups
in the user's ownership entities. In that case the `user_alice` user is
a member of both `group_developers` and `group_admin` groups.

<div>

::: title
Procedure
:::

- Enable the `includeTransitiveGroupOwnership` option in your
  `app-config.yaml` file.

  ``` yaml
  includeTransitiveGroupOwnership: true
  ```

</div>

### Conditional policies reference {#ref-rbac-conditional-policy-definition_title-authorization}

You can access API endpoints for conditional policies in Red Hat
Developer Hub. For example, to retrieve the available conditional rules,
which can help you define these policies, you can access the
`GET [api/plugins/condition-rules]` endpoint.

The `api/plugins/condition-rules` returns the condition parameters
schemas, for example:

``` json
[
   {
      "pluginId": "catalog",
      "rules": [
         {
            "name": "HAS_ANNOTATION",
            "description": "Allow entities with the specified annotation",
            "resourceType": "catalog-entity",
            "paramsSchema": {
               "type": "object",
               "properties": {
                  "annotation": {
                     "type": "string",
                     "description": "Name of the annotation to match on"
                  },
                  "value": {
                     "type": "string",
                     "description": "Value of the annotation to match on"
                  }
               },
               "required": [
                  "annotation"
               ],
               "additionalProperties": false,
               "$schema": "http://json-schema.org/draft-07/schema#"
            }
         },
         {
            "name": "HAS_LABEL",
            "description": "Allow entities with the specified label",
            "resourceType": "catalog-entity",
            "paramsSchema": {
               "type": "object",
               "properties": {
                  "label": {
                     "type": "string",
                     "description": "Name of the label to match on"
                  }
               },
               "required": [
                  "label"
               ],
               "additionalProperties": false,
               "$schema": "http://json-schema.org/draft-07/schema#"
            }
         },
         {
            "name": "HAS_METADATA",
            "description": "Allow entities with the specified metadata subfield",
            "resourceType": "catalog-entity",
            "paramsSchema": {
               "type": "object",
               "properties": {
                  "key": {
                     "type": "string",
                     "description": "Property within the entities metadata to match on"
                  },
                  "value": {
                     "type": "string",
                     "description": "Value of the given property to match on"
                  }
               },
               "required": [
                  "key"
               ],
               "additionalProperties": false,
               "$schema": "http://json-schema.org/draft-07/schema#"
            }
         },
         {
            "name": "HAS_SPEC",
            "description": "Allow entities with the specified spec subfield",
            "resourceType": "catalog-entity",
            "paramsSchema": {
               "type": "object",
               "properties": {
                  "key": {
                     "type": "string",
                     "description": "Property within the entities spec to match on"
                  },
                  "value": {
                     "type": "string",
                     "description": "Value of the given property to match on"
                  }
               },
               "required": [
                  "key"
               ],
               "additionalProperties": false,
               "$schema": "http://json-schema.org/draft-07/schema#"
            }
         },
         {
            "name": "IS_ENTITY_KIND",
            "description": "Allow entities matching a specified kind",
            "resourceType": "catalog-entity",
            "paramsSchema": {
               "type": "object",
               "properties": {
                  "kinds": {
                     "type": "array",
                     "items": {
                        "type": "string"
                     },
                     "description": "List of kinds to match at least one of"
                  }
               },
               "required": [
                  "kinds"
               ],
               "additionalProperties": false,
               "$schema": "http://json-schema.org/draft-07/schema#"
            }
         },
         {
            "name": "IS_ENTITY_OWNER",
            "description": "Allow entities owned by a specified claim",
            "resourceType": "catalog-entity",
            "paramsSchema": {
               "type": "object",
               "properties": {
                  "claims": {
                     "type": "array",
                     "items": {
                        "type": "string"
                     },
                     "description": "List of claims to match at least one on within ownedBy"
                  }
               },
               "required": [
                  "claims"
               ],
               "additionalProperties": false,
               "$schema": "http://json-schema.org/draft-07/schema#"
            }
         }
      ]
   }
   ... <another plugin condition parameter schemas>
]
```

The RBAC backend API constructs a condition JSON object based on the
previous condition schema.

#### Examples of conditional policies {#_examples-of-conditional-policies}

In Red Hat Developer Hub, you can define conditional policies with or
without criteria. You can use the following examples to define the
conditions based on your use case:

A condition without criteria

:   Consider a condition without criteria displaying catalogs only if
    user is a member of the owner group. To add this condition, you can
    use the catalog plugin schema `IS_ENTITY_OWNER` as follows:

    :::: formalpara
    ::: title
    Example condition without criteria
    :::

    ``` json
    {
      "rule": "IS_ENTITY_OWNER",
      "resourceType": "catalog-entity",
      "params": {
        "claims": ["group:default/team-a"]
      }
    }
    ```
    ::::

    In the previous example, the only conditional parameter used is
    `claims`, which contains a list of user or group entity references.

    You can apply the previous example condition to the RBAC REST API by
    adding additional parameters as follows:

    ``` json
    {
      "result": "CONDITIONAL",
      "roleEntityRef": "role:default/test",
      "pluginId": "catalog",
      "resourceType": "catalog-entity",
      "permissionMapping": ["read"],
      "conditions": {
        "rule": "IS_ENTITY_OWNER",
        "resourceType": "catalog-entity",
        "params": {
          "claims": ["group:default/team-a"]
        }
      }
    }
    ```

A condition with criteria

:   Consider a condition with criteria, which displays catalogs only if
    user is a member of owner group OR displays list of all catalog user
    groups.

    To add the criteria, you can add another rule as `IS_ENTITY_KIND` in
    the condition as follows:

    :::: formalpara
    ::: title
    Example condition with criteria
    :::

    ``` json
    {
      "anyOf": [
        {
          "rule": "IS_ENTITY_OWNER",
          "resourceType": "catalog-entity",
          "params": {
            "claims": ["group:default/team-a"]
          }
        },
        {
          "rule": "IS_ENTITY_KIND",
          "resourceType": "catalog-entity",
          "params": {
            "kinds": ["Group"]
          }
        }
      ]
    }
    ```
    ::::

    :::: note
    ::: title
    :::

    Running conditions in parallel during creation is not supported.
    Therefore, consider defining nested conditional policies based on
    the available criteria.
    ::::

    :::: formalpara
    ::: title
    Example of nested conditions
    :::

    ``` json
    {
      "anyOf": [
        {
          "rule": "IS_ENTITY_OWNER",
          "resourceType": "catalog-entity",
          "params": {
            "claims": ["group:default/team-a"]
          }
        },
        {
          "rule": "IS_ENTITY_KIND",
          "resourceType": "catalog-entity",
          "params": {
            "kinds": ["Group"]
          }
        }
      ],
      "not": {
        "rule": "IS_ENTITY_KIND",
        "resourceType": "catalog-entity",
        "params": { "kinds": ["Api"] }
      }
    }
    ```
    ::::

    You can apply the previous example condition to the RBAC REST API by
    adding additional parameters as follows:

    ``` json
    {
      "result": "CONDITIONAL",
      "roleEntityRef": "role:default/test",
      "pluginId": "catalog",
      "resourceType": "catalog-entity",
      "permissionMapping": ["read"],
      "conditions": {
        "anyOf": [
          {
            "rule": "IS_ENTITY_OWNER",
            "resourceType": "catalog-entity",
            "params": {
              "claims": ["group:default/team-a"]
            }
          },
          {
            "rule": "IS_ENTITY_KIND",
            "resourceType": "catalog-entity",
            "params": {
              "kinds": ["Group"]
            }
          }
        ]
      }
    }
    ```

The following examples can be used with Developer Hub plugins. These
examples can help you determine how to define conditional policies:

:::: formalpara
::: title
Conditional policy defined for Keycloak plugin
:::

``` json
{
  "result": "CONDITIONAL",
  "roleEntityRef": "role:default/developer",
  "pluginId": "catalog",
  "resourceType": "catalog-entity",
  "permissionMapping": ["update", "delete"],
  "conditions": {
    "not": {
      "rule": "HAS_ANNOTATION",
      "resourceType": "catalog-entity",
      "params": { "annotation": "keycloak.org/realm", "value": "<YOUR_REALM>" }
    }
  }
}
```
::::

The previous example of Keycloak plugin prevents users in the
`role:default/developer` from updating or deleting users that are
ingested into the catalog from the Keycloak plugin.

:::: note
::: title
:::

In the previous example, the annotation `keycloak.org/realm` requires
the value of `<YOUR_REALM>`.
::::

:::: formalpara
::: title
Conditional policy defined for Quay plugin
:::

``` json
{
  "result": "CONDITIONAL",
  "roleEntityRef": "role:default/developer",
  "pluginId": "scaffolder",
  "resourceType": "scaffolder-action",
  "permissionMapping": ["use"],
  "conditions": {
    "not": {
      "rule": "HAS_ACTION_ID",
      "resourceType": "scaffolder-action",
      "params": { "actionId": "quay:create-repository" }
    }
  }
}
```
::::

The previous example of Quay plugin prevents the role
`role:default/developer` from using the Quay scaffolder action. Note
that `permissionMapping` contains `use`, signifying that
`scaffolder-action` resource type permission does not have a permission
policy.

For more information about permissions in Red Hat Developer Hub, see
[Permission policies
reference](#ref-rbac-permission-policies_title-authorization).

## User statistics in Red Hat Developer Hub {#con-user-stats-rhdh_title-authorization}

In Red Hat Developer Hub, the `licensed-users-info-backend` plugin
provides statistical information about the logged-in users using the Web
UI or REST API endpoints.

The `licensed-users-info-backend` plugin enables administrators to
monitor the number of active users on Developer Hub. Using this feature,
organizations can compare their actual usage with the number of licenses
they have purchased. Additionally, you can share the user metrics with
Red Hat for transparency and accurate licensing.

The `licensed-users-info-backend` plugin is enabled by default. This
plugin enables a **Download User List** link at the bottom of the
**Administration → RBAC** tab.

### Downloading active users list in Red Hat Developer Hub {#proc-download-user-stats-rhdh_title-authorization}

You can download the list of users in CSV format using the Developer Hub
web interface.

<div>

::: title
Prerequisites
:::

- RBAC plugins (`@backstage-community/plugin-rbac` and
  `@backstage-community/plugin-rbac-backend`) must be enabled in Red Hat
  Developer Hub.

- An administrator role must be assigned.

</div>

<div>

::: title
Procedure
:::

1.  In Red Hat Developer Hub, navigate to **Administration** and select
    the **RBAC** tab.

2.  At the bottom of the **RBAC** page, click **Download User List**.

3.  Optional: Modify the file name in the **Save as** field and click
    **Save**.

4.  To access the downloaded users list, go to the **Downloads** folder
    on your local machine and open the CSV file.

</div>
