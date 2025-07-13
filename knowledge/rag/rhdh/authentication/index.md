Depending on your organization's security policies, you might require to
identify and authorize users before giving them access to resources,
such as Red Hat Developer Hub.

In Developer Hub, authentication and authorization are two separate
processes:

1.  Authentication defines the user identity, and passes on this
    information to Developer Hub. Read the following chapters to
    configure authentication in Developer Hub.

2.  Authorization defines what the authenticated identity can access or
    do in Developer Hub. See [Authorization in Red Hat Developer
    Hub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/authorization_in_red_hat_developer_hub/index).

:::: tip
::: title
Not recommended for production
:::

To explore Developer Hub features, you can enable the guest user to skip
configuring authentication and authorization, log in as the guest user,
and access all the features.
::::

The authentication system in Developer Hub is handled by external
authentication providers.

Developer Hub supports following authentication providers:

- Red Hat Single-Sign On (RHSSO)

- GitHub

- Microsoft Azure

To identify users in Developer Hub, configure:

- One (and only one) authentication provider for sign-in and
  identification.

- Optionally, additional authentication providers for identification, to
  add more information to the user identity, or enable access to
  additional external resources.

For each authentication provider, set up the shared secret that the
authentication provider and Developer Hub require to communicate, first
in the authentication provider, then in Developer Hub.

Developer Hub stores user identity information in the Developer Hub
software catalog.

:::: tip
::: title
Not recommended for production
:::

To explore the authentication system and use Developer Hub without
authorization policies, you can bypass the Developer Hub software
catalog and start using Developer Hub without provisioning the Developer
Hub software catalog.
::::

To get, store, and update additional user information, such as group or
team ownership, with the intention to use this data to define
authorization policies, provision users and groups in the Developer Hub
software catalog.

:::: important
::: title
:::

Developer Hub uses a one-way synchronization system to provision users
and groups from your authentication system to the Developer Hub software
catalog. Therefore, deleting users and groups by using Developer Hub Web
UI or REST API might have unintended consequences.
::::

## Authenticating with the Guest user {#authenticating-with-the-guest-user_title-authentication}

To explore Developer Hub features, you can skip configuring
authentication and authorization. You can configure Developer Hub to log
in as a Guest user and access Developer Hub features.

### Authenticating with the Guest user on an Operator-based installation {#authenticating-with-the-guest-user-on-an-operator-based-installation_title-authentication}

After an Operator-based installation, you can configure Developer Hub to
log in as a Guest user and access Developer Hub features.

<div>

::: title
Prerequisites
:::

- You [installed Developer Hub by using the Operator]().

- You [added a custom Developer Hub application
  configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index),
  and have sufficient permissions to modify it.

</div>

<div>

::: title
Procedure
:::

- To enable the guest user in your Developer Hub custom configuration,
  [edit your Developer Hub application
  configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index#provisioning-your-custom-configuration)
  with following content:

  :::: formalpara
  ::: title
  `app-config.yaml` fragment
  :::

  ``` yaml
  auth:
    environment: development
    providers:
      guest:
        dangerouslyAllowOutsideDevelopment: true
  ```
  ::::

</div>

<div>

::: title
Verification
:::

1.  Go to the Developer Hub login page.

2.  To log in with the Guest user account, click **Enter** in the
    **Guest** tile.

3.  In the Developer Hub **Settings** page, your profile name is
    **Guest**.

4.  You can use Developer Hub features.

</div>

### Authenticating with the Guest user on a Helm-based installation {#authenticating-with-the-guest-user-on-a-helm-based-installation_title-authentication}

On a Helm-based installation, you can configure Developer Hub to log in
as a Guest user and access Developer Hub features.

<div>

::: title
Prerequisites
:::

- You [added a custom Developer Hub application
  configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index),
  and have sufficient permissions to modify it.

- You [use the Red Hat Developer Hub Helm chart to run Developer
  Hub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index#using-the-helm-chart-to-run-rhdh-with-your-custom-configuration).

</div>

<div>

::: title
Procedure
:::

- To enable the guest user in your Developer Hub custom configuration,
  [configure your Red Hat Developer Hub Helm
  Chart](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index#using-the-helm-chart-to-run-rhdh-with-your-custom-configuration)
  with following content:

  :::: formalpara
  ::: title
  Red Hat Developer Hub Helm Chart configuration fragment
  :::

  ``` yaml
  upstream:
    backstage:
      appConfig:
        app:
          baseUrl: 'https://{{- include "janus-idp.hostname" . }}'
        auth:
          environment: development
          providers:
            guest:
              dangerouslyAllowOutsideDevelopment: true
  ```
  ::::

</div>

<div>

::: title
Verification
:::

1.  Go to the Developer Hub login page.

2.  To log in with the Guest user account, click **Enter** in the
    **Guest** tile.

3.  In the Developer Hub **Settings** page, your profile name is
    **Guest**.

4.  You can use Developer Hub features.

</div>

## Authenticating with Red Hat Build of Keycloak (RHBK) {#assembly-authenticating-with-rhbk}

To authenticate users with Red Hat Build of Keycloak (RHBK):

1.  [Enable the OpenID Connect (OIDC) authentication provider in
    RHDH](#enabling-authentication-with-rhbk).

2.  [Provision users from Red Hat Build of Keycloak (RHBK) to the
    software
    catalog](#provisioning-users-from-rhbk-to-the-software-catalog).

### Enabling authentication with Red Hat Build of Keycloak (RHBK) {#enabling-authentication-with-rhbk}

To authenticate users with Red Hat Build of Keycloak (RHBK), enable the
OpenID Connect (OIDC) authentication provider in Red Hat Developer Hub.

<div>

::: title
Prerequisites
:::

- You [added a custom Developer Hub application
  configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index),
  and have sufficient permissions to modify it.

- You have sufficient permissions in RHSSO to create and manage a realm.

</div>

<div>

::: title
Procedure
:::

1.  To allow Developer Hub to authenticate with RHBK, complete the steps
    in RHBK, to [create a realm and a
    user](https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.0/html/getting_started_guide/getting-started-zip-#getting-started-zip-create-a-realm)
    and [secure the first
    application](https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.0/html/getting_started_guide/getting-started-zip-#getting-started-zip-secure-the-first-application):

    a.  Use an existing realm, or [create a
        realm](https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.0/html/getting_started_guide/getting-started-zip-#getting-started-zip-create-a-realm),
        with a distinctive **Name** such as *\<my_realm\>*. Save the
        value for the next step:

        - **RHBK realm base URL**, such as:
          *\<your_rhbk_URL\>*/realms/*\<your_realm\>*.

    b.  To register your Developer Hub in RHBK, in the created realm,
        [secure the first
        application](https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.0/html-single/getting_started_guide/index#getting-started-zip-secure-the-first-application),
        with:

        i.  **Client ID**: A distinctive client ID, such as *\<RHDH\>*.

        ii. **Valid redirect URIs**: Set to the OIDC handler URL:
            `https://<RHDH_URL>/api/auth/oidc/handler/frame`.

        iii. Navigate to the **Credentials** tab and copy the **Client
             secret**.

        iv. Save the values for the next step:

            - **Client ID**

            - **Client Secret**

    c.  To prepare for the verification steps, in the same realm, get
        the credential information for an existing user or [create a
        user](https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.0/html-single/getting_started_guide/index#getting-started-zip-create-a-user).
        Save the user credential information for the verification steps.

2.  To add your RHSSO credentials to your Developer Hub, add the
    following key/value pairs to [your Developer Hub
    secrets](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/introduction_to_plugins/index#provisioning-your-custom-configuration):

    `AUTH_OIDC_CLIENT_ID`

    :   Enter the saved **Client ID**.

    `AUTH_OIDC_CLIENT_SECRET`

    :   Enter the saved **Client Secret**.

    `AUTH_OIDC_METADATA_URL`

    :   Enter the saved **RHBK realm base URL**.

3.  To set up the RHBK authentication provider in your Developer Hub
    custom configuration, edit your custom Developer Hub ConfigMap such
    as `app-config-rhdh`, and add the following lines to the
    `app-config.yaml` content:

    a.  Configure mandatory fields:

        :::: formalpara
        ::: title
        `app-config.yaml` fragment with mandatory fields to enable
        authentication with RHBK
        :::

        ``` yaml
        auth:
          environment: production
          providers:
            oidc:
              production:
                metadataUrl: ${AUTH_OIDC_METADATA_URL}
                clientId: ${AUTH_OIDC_CLIENT_ID}
                clientSecret: ${AUTH_OIDC_CLIENT_SECRET}
                prompt: auto
        signInPage: oidc
        ```
        ::::

        `environment: production`

        :   Mark the environment as `production` to hide the Guest login
            in the Developer Hub home page.

        `metadataUrl`, `clientId`, `clientSecret`

        :   To configure the OIDC provider with your secrets.

        `sigInPage: oidc`

        :   To enable the OIDC provider as default sign-in provider.

        `prompt: auto`

        :   To allow the identity provider to automatically determine
            whether to prompt for credentials or bypass the login
            redirect if an active RHSSO session exists.

</div>

:::: note
::: title
:::

If `prompt: auto` is not set, the identity provider defaults to
`prompt: none`, which assumes that you are already logged in and rejects
sign-in requests without an active session.
::::

`callbackUrl`

:   RHBK callback URL.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `callbackURL` field
    :::

    ``` yaml
    auth:
      providers:
        oidc:
          production:
            callbackUrl: ${AUTH_OIDC_CALLBACK_URL}
    ```
    ::::

`tokenEndpointAuthMethod`

:   Token endpoint authentication method.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `tokenEndpointAuthMethod`
    field
    :::

    ``` yaml
    auth:
      providers:
        oidc:
          production:
            tokenEndpointAuthMethod: ${AUTH_OIDC_TOKEN_ENDPOINT_METHOD}
    ```
    ::::

`tokenSignedResponseAlg`

:   Token signed response algorithm.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `tokenSignedResponseAlg`
    field
    :::

    ``` yaml
    auth:
      providers:
        oidc:
          production:
            tokenSignedResponseAlg: ${AUTH_OIDC_SIGNED_RESPONSE_ALG}
    ```
    ::::

`scope`

:   RHBK scope.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `scope` field
    :::

    ``` yaml
    auth:
      providers:
        oidc:
          production:
            scope: ${AUTH_OIDC_SCOPE}
    ```
    ::::

`signIn`

:

    `resolvers`

    :   After successful authentication, the user signing in must be
        resolved to an existing user in the Developer Hub catalog. To
        best match users securely for your use case, consider
        configuring a specific resolver. Enter the resolver list to
        override the default resolver:
        `oidcSubClaimMatchingKeycloakUserId`.

        The authentication provider tries each sign-in resolver in order
        until it succeeds, and fails if none succeed.

        :::: warning
        ::: title
        :::

        In production mode, only configure one resolver to ensure users
        are securely matched.
        ::::

        `resolver`

        :   Enter the sign-in resolver name. Available values:

            - `oidcSubClaimMatchingKeycloakUserId`

            - `emailLocalPartMatchingUserEntityName`

            - `emailMatchingUserEntityProfileEmail`

            - `preferredUsernameMatchingUserEntityName`

              :::: formalpara
              ::: title
              `app-config.yaml` fragment with optional `resolvers` list
              :::

              ``` yaml
              auth:
                providers:
                  oidc:
                    production:
                      signIn:
                        resolvers:
                          - resolver: oidcSubClaimMatchingKeycloakUserId
                          - resolver: preferredUsernameMatchingUserEntityName
                          - resolver: emailMatchingUserEntityProfileEmail
                          - resolver: emailLocalPartMatchingUserEntityName
              ```
              ::::

        `dangerouslyAllowSignInWithoutUserInCatalog: true`

        :   Configure the sign-in resolver to bypass the user
            provisioning requirement in the Developer Hub software
            catalog.

            :::: warning
            ::: title
            :::

            Use this option to explore Developer Hub features, but do
            not use it in production.
            ::::

            :::: formalpara
            ::: title
            `app-config-rhdh.yaml` fragment with optional field to allow
            signing in users absent from the software catalog
            :::

            ``` yaml
            auth:
              environment: production
              providers:
                oidc:
                  production:
                    metadataUrl: ${AUTH_OIDC_METADATA_URL}
                    clientId: ${AUTH_OIDC_CLIENT_ID}
                    clientSecret: ${AUTH_OIDC_CLIENT_SECRET}
                    signIn:
                      resolvers:
                        - resolver: oidcSubClaimMatchingKeycloakUserID
                          dangerouslyAllowSignInWithoutUserInCatalog: true
            signInPage: oidc
            ```
            ::::

`sessionDuration`

:   Lifespan of the user session. Enter a duration in `ms` library
    format (such as \'24h\', \'2 days\'), ISO duration, or \"human
    duration\" as used in code.

    :::: formalpara
    ::: title
    `app-config-rhdh.yaml` fragment with optional `sessionDuration`
    field
    :::

    ``` yaml
    auth:
      providers:
        github:
          production:
            sessionDuration: { hours: 24 }
    ```
    ::::

`auth`

:

    `backstageTokenExpiration`

    :   To modify the Developer Hub token expiration from its default
        value of one hour, note that this refers to the validity of
        short-term cryptographic tokens, not the session duration. The
        expiration value must be set between 10 minutes and 24 hours.

        :::: formalpara
        ::: title
        `app-config.yaml` fragment with optional
        `auth.backstageTokenExpiration` field
        :::

        ``` yaml
        auth:
          backstageTokenExpiration: { minutes: <user_defined_value> }
        ```
        ::::

        :::: warning
        ::: title
        Security consideration
        :::

        If multiple valid refresh tokens are issued due to frequent
        refresh token requests, older tokens will remain valid until
        they expire. To enhance security and prevent potential misuse of
        older tokens, enable a refresh token rotation strategy in your
        RHBK realm.

        1.  From the **Configure** section of the navigation menu, click
            **Realm Settings**.

        2.  From the **Realm Settings** page, click the **Tokens** tab.

        3.  From the **Refresh tokens** section of the **Tokens** tab,
            toggle the **Revoke Refresh Token** to the **Enabled**
            position.
        ::::

<div>

::: title
Verification
:::

1.  Go to the Developer Hub login page.

2.  Your Developer Hub sign-in page displays **Sign in using OIDC** and
    the Guest user sign-in is disabled.

3.  Log in with OIDC by using the saved **Username** and **Password**
    values.

</div>

### Provisioning users from Red Hat Build of Keycloak (RHBK) to the software catalog {#provisioning-users-from-rhbk-to-the-software-catalog}

<div>

::: title
Prerequisites
:::

- You [enabled authentication with
  RHBK](#enabling-authentication-with-rhbk).

</div>

<div>

::: title
Procedure
:::

- To enable RHBK member discovery, edit your custom Developer Hub
  ConfigMap, such as `app-config-rhdh`, and add the following lines to
  the `app-config.yaml` content:

  :::: {#keycloakOrgProviderId .formalpara}
  ::: title
  `app-config.yaml` fragment with mandatory `keycloakOrg` fields
  :::

  ``` yaml
  catalog:
    providers:
      keycloakOrg:
        default:
          baseUrl: ${AUTH_OIDC_METADATA_URL}
          clientId: ${AUTH_OIDC_CLIENT_ID}
          clientSecret: ${AUTH_OIDC_CLIENT_SECRET}
  ```
  ::::

  `baseUrl`

  :   Your RHBK server URL, defined when [enabling authentication with
      RHBK](#enabling-authentication-with-rhbk).

  `clientId`

  :   Your Developer Hub application client ID in RHBK, defined when
      [enabling authentication with
      RHBK](#enabling-authentication-with-rhbk).

  `clientSecret`

  :   Your Developer Hub application client secret in RHBK, defined when
      [enabling authentication with
      RHBK](#enabling-authentication-with-rhbk).

  Optional: Consider adding the following optional fields:

  `realm`

  :   Realm to synchronize. Default value: `master`.

      :::: formalpara
      ::: title
      `app-config.yaml` fragment with optional `realm` field
      :::

      ``` yaml
      catalog:
        providers:
          keycloakOrg:
            default:
              realm: master
      ```
      ::::

  `loginRealm`

  :   Realm used to authenticate. Default value: `master`.

      :::: formalpara
      ::: title
      `app-config.yaml` fragment with optional `loginRealm` field
      :::

      ``` yaml
      catalog:
        providers:
          keycloakOrg:
            default:
              loginRealm: master
      ```
      ::::

  `userQuerySize`

  :   User number to query simultaneously. Default value: `100`.

      :::: formalpara
      ::: title
      `app-config.yaml` fragment with optional `userQuerySize` field
      :::

      ``` yaml
      catalog:
        providers:
          keycloakOrg:
            default:
              userQuerySize: 100
      ```
      ::::

  `groupQuerySize`

  :   Group number to query simultaneously. Default value: `100`.

      :::: formalpara
      ::: title
      `app-config.yaml` fragment with optional `groupQuerySize` field
      :::

      ``` yaml
      catalog:
        providers:
          keycloakOrg:
            default:
              groupQuerySize: 100
      ```
      ::::

  `schedule.frequency`

  :   To specify custom schedule frequency. Supports cron, ISO duration,
      and \"human duration\" as used in code.

      :::: formalpara
      ::: title
      `app-config.yaml` fragment with optional `schedule.frequency`
      field
      :::

      ``` yaml
      catalog:
        providers:
          keycloakOrg:
            default:
              schedule:
                frequency: { hours: 1 }
      ```
      ::::

  `schedule.timeout`

  :   To specify custom timeout. Supports ISO duration and \"human
      duration\" as used in code.

      :::: formalpara
      ::: title
      `app-config.yaml` fragment with optional `schedule.timeout` field
      :::

      ``` yaml
      catalog:
        providers:
          keycloakOrg:
            default:
              schedule:
                timeout: { minutes: 50 }
      ```
      ::::

  `schedule.initialDelay`

  :   To specify custom initial delay. Supports ISO duration and \"human
      duration\" as used in code.

      :::: formalpara
      ::: title
      `app-config.yaml` fragment with optional `schedule.initialDelay`
      field
      :::

      ``` yaml
      catalog:
        providers:
          keycloakOrg:
            default:
              schedule:
                initialDelay: { seconds: 15}
      ```
      ::::

</div>

<div>

::: title
Verification
:::

1.  Check the console logs to verify that the synchronization is
    completed.

    :::: formalpara
    ::: title
    Successful synchronization example:
    :::

    ``` json
    {"class":"KeycloakOrgEntityProvider","level":"info","message":"Read 3 Keycloak users and 2 Keycloak groups in 1.5 seconds. Committing...","plugin":"catalog","service":"backstage","taskId":"KeycloakOrgEntityProvider:default:refresh","taskInstanceId":"bf0467ff-8ac4-4702-911c-380270e44dea","timestamp":"2024-09-25 13:58:04"}
    {"class":"KeycloakOrgEntityProvider","level":"info","message":"Committed 3 Keycloak users and 2 Keycloak groups in 0.0 seconds.","plugin":"catalog","service":"backstage","taskId":"KeycloakOrgEntityProvider:default:refresh","taskInstanceId":"bf0467ff-8ac4-4702-911c-380270e44dea","timestamp":"2024-09-25 13:58:04"}
    ```
    ::::

2.  Log in with an RHBK account.

</div>

### Creating a custom transformer to provision users from Red Hat Build of Keycloak (RHBK) to the software catalog {#creating-a-custom-transformer-to-provision-users-from-rhbk-to-the-software-catalog}

To customize how RHBK users and groups are mapped to Red Hat Developer
Hub entities, you can create a backend module that uses the
`keycloakTransformerExtensionPoint` to provide custom user and group
transformers for the Keycloak backend.

<div>

::: title
Prerequisites
:::

- You have [enabled provisioning users from Red Hat Build of Keycloak
  (RHBK) to the software
  catalog](#provisioning-users-from-rhbk-to-the-software-catalog).

</div>

<div>

::: title
Procedure
:::

1.  Create a new backend module with the `yarn new` command.

2.  Add your custom user and group transformers to the
    `keycloakTransformerExtensionPoint`.

    The following is an example of how the backend module can be
    defined:

    :::: formalpara
    ::: title
    `plugins/<module-name>/src/module.ts`
    :::

    ``` javascript
    import {
      GroupTransformer,
      keycloakTransformerExtensionPoint,
      UserTransformer,
    } from '@backstage-community/plugin-catalog-backend-module-keycloak';

    const customGroupTransformer: GroupTransformer = async (
      entity, // entity output from default parser
      realm, // Keycloak realm name
      groups, // Keycloak group representation
    ) => {
      /* apply transformations */
      return entity;
    };
    const customUserTransformer: UserTransformer = async (
      entity, // entity output from default parser
      user, // Keycloak user representation
      realm, // Keycloak realm name
      groups, // Keycloak group representation
    ) => {
      /* apply transformations */
      return entity;
    };

    export const keycloakBackendModuleTransformer = createBackendModule({
      pluginId: 'catalog',
      moduleId: 'keycloak-transformer',
      register(reg) {
        reg.registerInit({
          deps: {
            keycloak: keycloakTransformerExtensionPoint,
          },
          async init({ keycloak }) {
            keycloak.setUserTransformer(customUserTransformer);
            keycloak.setGroupTransformer(customGroupTransformer);
            /* highlight-add-end */
          },
        });
      },
    });
    ```
    ::::

    :::: important
    ::: title
    :::

    The module's `pluginId` must be set to `catalog` to match the
    `pluginId` of the `keycloak-backend`; otherwise, the module fails to
    initialize.
    ::::

3.  Install this new backend module into your Developer Hub backend.

    ``` javascript
    backend.add(import(backstage-plugin-catalog-backend-module-keycloak-transformer))
    ```

</div>

<div>

::: title
Verification
:::

- Developer Hub imports the users and groups each time when started.
  Check the console logs to verify that the synchronization is
  completed.

  :::: formalpara
  ::: title
  Successful synchronization example:
  :::

  ``` json
  {"class":"KeycloakOrgEntityProvider","level":"info","message":"Read 3 Keycloak users and 2 Keycloak groups in 1.5 seconds. Committing...","plugin":"catalog","service":"backstage","taskId":"KeycloakOrgEntityProvider:default:refresh","taskInstanceId":"bf0467ff-8ac4-4702-911c-380270e44dea","timestamp":"2024-09-25 13:58:04"}
  {"class":"KeycloakOrgEntityProvider","level":"info","message":"Committed 3 Keycloak users and 2 Keycloak groups in 0.0 seconds.","plugin":"catalog","service":"backstage","taskId":"KeycloakOrgEntityProvider:default:refresh","taskInstanceId":"bf0467ff-8ac4-4702-911c-380270e44dea","timestamp":"2024-09-25 13:58:04"}
  ```
  ::::

- After the first import is complete, navigate to the **Catalog** page
  and select **User** to view the list of users.

- When you select a user, you see the information imported from RHBK.

- You can select a group, view the list, and access or review the
  information imported from RHBK.

- You can log in with an RHBK account.

</div>

## Authenticating with GitHub

To authenticate users with GitHub or GitHub Enterprise:

1.  [Enable the GitHub authentication provider in Developer
    Hub](#enabling-authentication-with-github).

2.  [Provision users from GitHub to the software
    catalog](#provisioning-users-from-github-to-the-software-catalog).

### Enabling authentication with GitHub

To authenticate users with GitHub, enable the GitHub authentication
provider in Red Hat Developer Hub.

<div>

::: title
Prerequisites
:::

- You [added a custom Developer Hub application
  configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index),
  and have sufficient permissions to modify it.

- You have sufficient permissions in GitHub to create and manage a
  [GitHub App](https://docs.github.com/en/apps/overview).

</div>

<div>

::: title
Procedure
:::

1.  To allow Developer Hub to authenticate with GitHub, create a GitHub
    App. Opt for a GitHub App instead of an OAuth app to use
    fine-grained permissions, gain more control over which repositories
    the application can access, and use short-lived tokens.

    a.  [Register a GitHub
        App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app)
        with the following configuration:

        - **GitHub App name**: Enter a unique name identifying your
          GitHub App, such as *\<Red Hat Developer Hub\>*-*\<GUID\>*.

        - **Homepage URL**: Your Developer Hub URL:
          `https://<my_developer_hub_url>`.

        - **Authorization callback URL**: Your Developer Hub
          authentication backend URL:
          `https://<my_developer_hub_url>/api/auth/github/handler/frame`.

        - **Webhook URL**: Your Developer Hub URL:
          `https://<my_developer_hub_url>`.

        - **Webhook secret**: Provide a strong secret.

        - **Repository permissions**:

          - Enable `Read-only` access to:

            - **Administration**

            - **Commit statuses**

            - **Contents**

            - **Dependabot alerts**

            - **Deployments**

            - **Pull Requests**

            - **Webhooks**

              :::: tip
              ::: title
              :::

              If you plan to make changes using the GitHub API, ensure
              that `Read and write` permissions are enabled instead of
              `Read-only`.
              ::::

          - Toggle other permissions as per your needs.

        - **Organization permissions**:

          - Enable `Read-only` access to **Members**.

        - For **Where can this GitHub App be installed?**, select
          `Only on this account`.

    b.  In the **General** → **Clients secrets** section, click
        **Generate a new client secret**.

    c.  In the **General** → **Private keys** section, click **Generate
        a private key**.

    d.  In the **Install App** tab, choose an account to install your
        GitHub App on.

    e.  Save the following values for the next step:

        - **App ID**

        - **Client ID**

        - **Client secret**

        - **Private key**

        - **Webhook secret**

2.  To add your GitHub credentials to Developer Hub, add the following
    key/value pairs to [your Developer Hub
    secrets](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/introduction_to_plugins/index#provisioning-your-custom-configuration):

    `AUTH_GITHUB_APP_ID`

    :   Enter the saved **App ID**.

    `AUTH_GITHUB_CLIENT_ID`

    :   Enter the saved **Client ID**.

    `GITHUB_ORGANIZATION`

    :   Enter your GitHub organization name, such as
        \`*\<your_github_organization_name\>*\'.

    `GITHUB_ORG_URL`

    :   Enter `$GITHUB_HOST_DOMAIN/$GITHUB_ORGANIZATION`.

    `GITHUB_CLIENT_SECRET`

    :   Enter the saved **Client Secret**.

    `GITHUB_PRIVATE_KEY_FILE`

    :   Enter the saved **Private key**.

    `GITHUB_WEBHOOK_URL`

    :   Enter your Developer Hub URL: `https://<my_developer_hub_url>`.

    `GITHUB_WEBHOOK_SECRET`

    :   Enter the saved **Webhook secret**.

3.  . To set up the GitHub authentication provider and enable
    integration with the GitHub API in your Developer Hub custom
    configuration, edit your custom Developer Hub config map such as
    `my-rhdh-app-config`, and add the following lines to the
    `app-config.yaml` file content:

    :::: formalpara
    ::: title
    `app-config.yaml` file fragment with mandatory fields to enable
    authentication with GitHub
    :::

    ``` yaml
    auth:
      environment: production
      providers:
        github:
          production:
            clientId: ${AUTH_GITHUB_CLIENT_ID}
            clientSecret: ${AUTH_GITHUB_CLIENT_SECRET}
    integrations:
      github:
        - host: ${GITHUB_HOST_DOMAIN}
          apps:
            - appId: ${AUTH_GITHUB_APP_ID}
              clientId: ${AUTH_GITHUB_CLIENT_ID}
              clientSecret: ${GITHUB_CLIENT_SECRET}
              webhookUrl: ${GITHUB_WEBHOOK_URL}
              webhookSecret: ${GITHUB_WEBHOOK_SECRET}
              privateKey: |
                ${GITHUB_PRIVATE_KEY_FILE}
    signInPage: github
    ```
    ::::

    - Mark the environment as `production` and disable the Guest login
      option in the Developer Hub login page.

    - Apply the GitHub credentials configured in your Developer Hub
      secrets.

    - To enable the GitHub provider as your Developer Hub sign-in
      provider.

      a.  Optional: Consider adding the following optional fields:

          `callbackUrl`

          :   The callback URL that GitHub uses when initiating an OAuth
              flow, such as:
              *\<your_intermediate_service_url/handler\>*. Define it
              when Developer Hub is not the immediate receiver, such as
              in cases when you use one OAuth app for many Developer Hub
              instances.

              :::: formalpara
              ::: title
              `app-config.yaml` file fragment with optional
              `enterpriseInstanceUrl` field
              :::

              ``` yaml
              auth:
                providers:
                  github:
                    production:
                      callbackUrl: <your_intermediate_service_url/handler>
              ```
              ::::

</div>

`sessionDuration`

:   Lifespan of the user session. Enter a duration in `ms` library
    format (such as \'24h\', \'2 days\'), ISO duration, or \"human
    duration\" as used in code.

    :::: formalpara
    ::: title
    `app-config-rhdh.yaml` fragment with optional `sessionDuration`
    field
    :::

    ``` yaml
    auth:
      providers:
        github:
          production:
            sessionDuration: { hours: 24 }
    ```
    ::::

`signIn`

:

    `resolvers`

    :   After successful authentication, the user signing in must be
        resolved to an existing user in the Developer Hub catalog. To
        best match users securely for your use case, consider
        configuring a specific resolver. Enter the resolver list to
        override the default resolver: `usernameMatchingUserEntityName`.

        The authentication provider tries each sign-in resolver in order
        until it succeeds, and fails if none succeed.

        :::: warning
        ::: title
        :::

        In production mode, only configure one resolver to ensure users
        are securely matched.
        ::::

        `resolver`

        :   Enter the sign-in resolver name. Available resolvers:

            - `usernameMatchingUserEntityName`

            - `preferredUsernameMatchingUserEntityName`

            - `emailMatchingUserEntityProfileEmail`

        `dangerouslyAllowSignInWithoutUserInCatalog: true`

        :   Configure the sign-in resolver to bypass the user
            provisioning requirement in the Developer Hub software
            catalog.

            :::: warning
            ::: title
            :::

            Use `dangerouslyAllowSignInWithoutUserInCatalog` to explore
            Developer Hub features, but do not use it in production.
            ::::

            :::: formalpara
            ::: title
            `app-config.yaml` file fragment with optional field to allow
            signing in users absent from the software catalog
            :::

            ``` yaml
            auth:
              environment: production
              providers:
                github:
                  production:
                    clientId: ${AUTH_GITHUB_CLIENT_ID}
                    clientSecret: ${AUTH_GITHUB_CLIENT_SECRET}
                    signIn:
                      resolvers:
                        - resolver: usernameMatchingUserEntityName
                          dangerouslyAllowSignInWithoutUserInCatalog: true
            integrations:
              github:
                - host: ${GITHUB_HOST_DOMAIN}
                  apps:
                    - appId: ${AUTH_GITHUB_APP_ID}
                      clientId: ${AUTH_GITHUB_CLIENT_ID}
                      clientSecret: ${GITHUB_CLIENT_SECRET}
                      webhookUrl: ${GITHUB_WEBHOOK_URL}
                      webhookSecret: ${GITHUB_WEBHOOK_SECRET}
                      privateKey: |
                        ${GITHUB_PRIVATE_KEY_FILE}
            signInPage: github
            ```
            ::::

:::::: tip
::: title
:::

To enable GitHub integration with a different authentication provider,
complete the following configurations:

- Add the GitHub provider to the existing `auth` section.

- Keep the `signInPage` section from your authentication provider
  configuration.

:::: formalpara
::: title
`app-config.yaml` file fragment with mandatory fields to enable GitHub
integration and use a different authentication provider
:::

``` yaml
auth:
  environment: production
  providers:
    github:
      production:
        clientId: ${AUTH_GITHUB_CLIENT_ID}
        clientSecret: ${AUTH_GITHUB_CLIENT_SECRET}
    <your_other_authentication_providers_configuration>
integrations:
  github:
    - host: ${GITHUB_HOST_DOMAIN}
      apps:
        - appId: ${AUTH_GITHUB_APP_ID}
          clientId: ${AUTH_GITHUB_CLIENT_ID}
          clientSecret: ${GITHUB_CLIENT_SECRET}
          webhookUrl: ${GITHUB_WEBHOOK_URL}
          webhookSecret: ${GITHUB_WEBHOOK_SECRET}
          privateKey: |
            ${GITHUB_PRIVATE_KEY_FILE}
signInPage: <your_main_authentication_provider>
```
::::
::::::

<div>

::: title
Verification
:::

1.  Go to the Developer Hub login page.

2.  Your Developer Hub sign-in page displays **Sign in using GitHub**
    and the Guest user sign-in is disabled.

3.  Log in with GitHub.

</div>

### Provisioning users from GitHub to the software catalog

To authenticate users, Red Hat Developer Hub requires their presence in
the software catalog. Consider configuring Developer Hub to provision
users from GitHub to the software catalog on schedule, rather than
provisioning the users manually.

<div>

::: title
Prerequisites
:::

- You have [enabled authentication with
  GitHub](#enabling-authentication-with-github), including the following
  secrets:

  - `GITHUB_HOST_DOMAIN`

  - `GITHUB_ORGANIZATION`

</div>

<div>

::: title
Procedure
:::

- To enable GitHub member discovery, edit your custom Developer Hub
  ConfigMap, such as `app-config-rhdh`, and add the following lines to
  the `app-config.yaml` content:

  :::: {#githubProviderId .formalpara}
  ::: title
  `app-config.yaml` fragment with mandatory `github` fields
  :::

  ``` yaml
  catalog:
    providers:
      github:
        providerId:
          organization: "${GITHUB_ORGANIZATION}"
          schedule:
            frequency:
              minutes: 30
            initialDelay:
              seconds: 15
            timeout:
              minutes: 15
      githubOrg:
        githubUrl: "${GITHUB_HOST_DOMAIN}"
        orgs: [ "${GITHUB_ORGANIZATION}" ]
        schedule:
          frequency:
            minutes: 30
          initialDelay:
            seconds: 15
          timeout:
            minutes: 15
  ```
  ::::

  `organization`, `githubUrl`, and `orgs`

  :   Use the Developer Hub application information that you have
      created in GitHub and configured in OpenShift as secrets.

  `schedule.frequency`

  :   To specify custom schedule frequency. Supports cron, ISO duration,
      and \"human duration\" as used in code.

  `schedule.timeout`

  :   To specify custom timeout. Supports ISO duration and \"human
      duration\" as used in code.

  `schedule.initialDelay`

  :   To specify custom initial delay. Supports ISO duration and \"human
      duration\" as used in code.

</div>

<div>

::: title
Verification
:::

1.  Check the console logs to verify that the synchronization is
    completed.

    :::: formalpara
    ::: title
    Successful synchronization example:
    :::

    ``` json
    {"class":"GithubMultiOrgEntityProvider","level":"info","message":"Reading GitHub users and teams for org: rhdh-dast","plugin":"catalog","service":"backstage","target":"https://github.com","taskId":"GithubMultiOrgEntityProvider:production:refresh","taskInstanceId":"801b3c6c-167f-473b-b43e-e0b4b780c384","timestamp":"2024-09-09 23:55:58"}
    {"class":"GithubMultiOrgEntityProvider","level":"info","message":"Read 7 GitHub users and 2 GitHub groups in 0.4 seconds. Committing...","plugin":"catalog","service":"backstage","target":"https://github.com","taskId":"GithubMultiOrgEntityProvider:production:refresh","taskInstanceId":"801b3c6c-167f-473b-b43e-e0b4b780c384","timestamp":"2024-09-09 23:55:59"}
    ```
    ::::

2.  Log in with a GitHub account.

</div>

## Authentication with Microsoft Azure {#assembly-authenticating-with-microsoft-azure}

To authenticate users with Microsoft Azure:

1.  [Enable authentication with Microsoft
    Azure](#enabling-authentication-with-microsoft-azure).

2.  [Provision users from Microsoft Azure to the software
    catalog](#provisioning-users-from-microsoft-azure-to-the-software-catalog).

### Enabling authentication with Microsoft Azure

Red Hat Developer Hub includes a Microsoft Azure authentication provider
that can authenticate users by using OAuth.

<div>

::: title
Prerequisites
:::

1.  You have the permission to register an application in Microsoft
    Azure.

    - You [added a custom Developer Hub application
      configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index),
      and have sufficient permissions to modify it.

</div>

<div>

::: title
Procedure
:::

1.  To allow Developer Hub to authenticate with Microsoft Azure, [create
    an OAuth application in Microsoft
    Azure](https://learn.microsoft.com/en-us/entra/identity-platform/scenario-web-app-sign-user-app-registration?tabs=aspnetcore#register-an-app-by-using-the-azure-portal).

    a.  In the Azure portal go to [**App
        registrations**](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade),
        create a **New registration** with the configuration:

        **Name**

        :   The application name in Azure, such as *\<My Developer
            Hub\>*.

    b.  On the **Home \> App registrations \> *\<My Developer Hub\>* \>
        Manage \> Authentication** page, **Add a platform**, with the
        following configuration:

        **Redirect URI**

        :   Enter the backend authentication URI set in Developer Hub:
            `https://<my_developer_hub_url>/api/auth/microsoft/handler/frame`

        **Front-channel logout URL**

        :   Leave blank.

        **Implicit grant and hybrid flows**

        :   Leave all checkboxes cleared.

    c.  On the **Home \> App registrations \> *\<My Developer Hub\>* \>
        Manage \> API permissions** page, **Add a Permission**, then add
        the following **Delegated permission** for the **Microsoft Graph
        API**:

        - `email`

        - `offline_access`

        - `openid`

        - `profile`

        - `User.Read`

        - Optional custom scopes for the Microsoft Graph API that you
          define both in this section and in the `app-config.yaml`
          Developer Hub configuration file.

</div>

::: informalexample
Your company might require you to grant admin consent for these
permissions. Even if your company does not require admin consent, you
might do so as it means users do not need to individually consent the
first time they access backstage. To grant administrator consent, a
directory administrator must go to the [admin
consent](https://learn.microsoft.com/en-us/azure/active-directory/manage-apps/user-admin-consent-overview)
page and click **Grant admin consent for COMPANY NAME**.
:::

a.  On the **Home \> App registrations \> *\<My Developer Hub\>* \>
    Manage \> Certificates & Secrets** page, in the **Client secrets**
    tab, create a **New client secret**.

b.  Save for the next step:

    - **Directory (tenant) ID**

    - **Application (client) ID**

    - **Application (client) secret**

      1.  To add your Microsoft Azure credentials to Developer Hub, add
          the following key/value pairs to [your Developer Hub
          secrets](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/introduction_to_plugins/index#provisioning-your-custom-configuration):

          `AUTH_AZURE_TENANT_ID`

          :   Enter your saved **Directory (tenant) ID**.

          `AUTH_AZURE_CLIENT_ID`

          :   Enter your saved **Application (client) ID**.

          `AUTH_AZURE_CLIENT_SECRET`

          :   Enter your saved **Application (client) secret**.

      2.  Set up the Microsoft Azure authentication provider in your
          `app-config.yaml` file:

          :::: formalpara
          ::: title
          `app-config.yaml` file fragment
          :::

          ``` yaml
          auth:
            environment: production
            providers:
              microsoft:
                production:
                  clientId: ${AUTH_AZURE_CLIENT_ID}
                  clientSecret: ${AUTH_AZURE_CLIENT_SECRET}
                  tenantId: ${AUTH_AZURE_TENANT_ID}
          signInPage: microsoft
          ```
          ::::

          - Mark the environment as production and disable the **Guest**
            login option in the Developer Hub login page.

          - Apply the Microsoft Azure credentials configured in your
            Developer Hub secrets.

          - Set the Microsoft Azure provider as your Developer Hub
            sign-in provider.

c.  Optional: Consider adding following optional fields:

    `domainHint`

    :   Optional for single-tenant applications. You can reduce login
        friction for users with accounts in multiple tenants by
        automatically filtering out accounts from other tenants. If you
        want to use this parameter for a single-tenant application,
        uncomment and enter the tenant ID. If your application
        registration is multi-tenant, leave this parameter blank. For
        more information, see [Home Realm
        Discovery](https://learn.microsoft.com/en-us/azure/active-directory/manage-apps/home-realm-discovery-policy).

        :::: formalpara
        ::: title
        `app-config.yaml` file fragment with optional `domainHint` field
        :::

        ``` yaml
        auth:
          environment: production
          providers:
            microsoft:
              production:
                domainHint: ${AUTH_AZURE_TENANT_ID}
        ```
        ::::

    `additionalScopes`

    :   Optional for additional scopes. To add scopes for the
        application registration, uncomment and enter the list of scopes
        that you want to add. The default and mandatory value lists:
        `'openid', 'offline_access', 'profile', 'email', 'User.Read'`.

        :::: formalpara
        ::: title
        `app-config.yaml` file fragment with optional `additionalScopes`
        field
        :::

        ``` yaml
        auth:
          environment: production
          providers:
            microsoft:
              production:
                additionalScopes:
                   - Mail.Send
        ```
        ::::

    `sessionDuration`

    :   Lifespan of the user session. Enter a duration in `ms` library
        format (such as \'24h\', \'2 days\'), ISO duration, or \"human
        duration\" as used in code.

        :::: formalpara
        ::: title
        `app-config-rhdh.yaml` fragment with optional `sessionDuration`
        field
        :::

        ``` yaml
        auth:
          providers:
            microsoft:
              production:
                sessionDuration: { hours: 24 }
        ```
        ::::

    `signIn`

    :

        `resolvers`

        :   After successful authentication, the user signing in must be
            resolved to an existing user in the Developer Hub catalog.
            To best match users securely for your use case, consider
            configuring a specific resolver. Enter the resolver list to
            override the default resolver:
            `emailLocalPartMatchingUserEntityName`.

            The authentication provider tries each sign-in resolver in
            order until it succeeds, and fails if none succeed.

            :::: warning
            ::: title
            :::

            In production mode, only configure one resolver to ensure
            users are securely matched.
            ::::

            `resolver`

            :   Enter the sign-in resolver name. Available resolvers:

                - `userIdMatchingUserEntityAnnotation`

                - `emailLocalPartMatchingUserEntityName`

                - `emailMatchingUserEntityProfileEmail`

            `dangerouslyAllowSignInWithoutUserInCatalog: true`

            :   Configure the sign-in resolver to bypass the user
                provisioning requirement in the Developer Hub software
                catalog.

                :::: warning
                ::: title
                :::

                Use `dangerouslyAllowSignInWithoutUserInCatalog` to
                explore Developer Hub features, but do not use it in
                production.
                ::::

                :::: formalpara
                ::: title
                `app-config-rhdh.yaml` fragment with optional field to
                allow signing in users absent from the software catalog
                :::

                ``` yaml
                auth:
                  environment: production
                  providers:
                    microsoft:
                      production:
                        clientId: ${AUTH_AZURE_CLIENT_ID}
                        clientSecret: ${AUTH_AZURE_CLIENT_SECRET}
                        tenantId: ${AUTH_AZURE_TENANT_ID}
                        signIn:
                          resolvers:
                            - resolver: usernameMatchingUserEntityName
                              dangerouslyAllowSignInWithoutUserInCatalog: true
                signInPage: microsoft
                ```
                ::::

:::: note
::: title
:::

This step is optional for environments with outgoing access
restrictions, such as firewall rules. If your environment has such
restrictions, ensure that your RHDH backend can access the following
hosts:

- `login.microsoftonline.com`: For obtaining and exchanging
  authorization codes and access tokens.

- `graph.microsoft.com`: For retrieving user profile information (as
  referenced in the source code). If this host is unreachable, you might
  see an *Authentication failed, failed to fetch user profile* error
  when attempting to log in.
::::

### Provisioning users from Microsoft Azure to the software catalog

To authenticate users with Microsoft Azure, after [Enabling
authentication with Microsoft
Azure](#enabling-authentication-with-microsoft-azure), provision users
from Microsoft Azure to the Developer Hub software catalog.

<div>

::: title
Prerequisites
:::

- You have [enabled authentication with Microsoft
  Azure](#enabling-authentication-with-microsoft-azure).

</div>

<div>

::: title
Procedure
:::

- To enable Microsoft Azure member discovery, edit your custom Developer
  Hub ConfigMap, such as `app-config-rhdh`, and add following lines to
  the `app-config.yaml` content:

  :::: {#microsoftGraphOrgProviderId .formalpara}
  ::: title
  `app-config.yaml` fragment with mandatory `microsoftGraphOrg` fields
  :::

  ``` yaml
  catalog:
    providers:
      microsoftGraphOrg:
        providerId:
          target: https://graph.microsoft.com/v1.0
          tenantId: ${AUTH_AZURE_TENANT_ID}
          clientId: ${AUTH_AZURE_CLIENT_ID}
          clientSecret: ${AUTH_AZURE_CLIENT_SECRET}
  ```
  ::::

  `target: https://graph.microsoft.com/v1.0`

  :   Defines the MSGraph API endpoint the provider is connecting to.
      You might change this parameter to use a different version, such
      as the [beta
      endpoint](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-beta#call-the-beta-endpoint).

  `tenandId`, `clientId` and `clientSecret`

  :   Use the Developer Hub application information you created in
      Microsoft Azure and configured in OpenShift as secrets.

</div>

Optional: Consider adding the following optional
`microsoftGraphOrg.providerId` fields:

`authority: https://login.microsoftonline.com`

:   Defines the authority used. Change the value to use a different
    [authority](https://learn.microsoft.com/en-us/graph/deployments#app-registration-and-token-service-root-endpoints),
    such as Azure US government. Default value:
    `https://login.microsoftonline.com`.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `queryMode` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            authority: https://login.microsoftonline.com/
    ```
    ::::

<!-- -->

`queryMode: basic | advanced`

:   By default, the Microsoft Graph API only provides the `basic`
    feature set for querying. Certain features require `advanced`
    querying capabilities. See [Microsoft Azure Advanced
    queries](https://docs.microsoft.com/en-us/graph/aad-advanced-queries).

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `queryMode` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            queryMode: advanced
    ```
    ::::

<!-- -->

`user.expand`

:   To include the expanded resource or collection referenced by a
    single relationship (navigation property) in your results. Only one
    relationship can be expanded in a single request. See [Microsoft
    Graph query expand
    parameter](https://docs.microsoft.com/en-us/graph/query-parameters#expand-parameter).
    This parameter can be combined with
    [variablelist_title](#userGroupMemberFilter) or
    [variablelist_title](#userFilter).

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `user.expand` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            user:
              expand: manager
    ```
    ::::

<!-- -->

`user.filter`

:   To filter users. See [Microsoft Graph
    API](https://docs.microsoft.com/en-us/graph/api/resources/user?view=graph-rest-1.0#properties)
    and [Microsoft Graph API query filter parameters
    syntax](https://docs.microsoft.com/en-us/graph/query-parameters#filter-parameter).
    This parameter and [variablelist_title](#userGroupMemberFilter) are
    mutually exclusive, only one can be specified.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `user.filter` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            user:
              filter: accountEnabled eq true and userType eq 'member'
    ```
    ::::

<!-- -->

`user.loadPhotos: true | false`

:   Load photos by default. Set to `false` to not load user photos.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `user.loadPhotos` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            user:
              loadPhotos: true
    ```
    ::::

<!-- -->

`user.select`

:   Define the [Microsoft Graph resource
    types](https://docs.microsoft.com/en-us/graph/api/resources/schemaextension?view=graph-rest-1.0)
    to retrieve.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `user.select` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            user:
              select: ['id', 'displayName', 'description']
    ```
    ::::

    `userGroupMember.filter`

    :   To use group membership to get users. To filter groups and fetch
        their members. This parameter and
        [variablelist_title](#userFilter) are mutually exclusive, only
        one can be specified.

        :::: formalpara
        ::: title
        `app-config.yaml` fragment with optional
        `userGroupMember.filter` field
        :::

        ``` yaml
        catalog:
          providers:
            microsoftGraphOrg:
              providerId:
                userGroupMember:
                  filter: "displayName eq 'Backstage Users'"
        ```
        ::::

<!-- -->

`userGroupMember.search`

:   To use group membership to get users. To search for groups and fetch
    their members. This parameter and [variablelist_title](#userFilter)
    are mutually exclusive, only one can be specified.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `userGroupMember.search`
    field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            userGroupMember:
              search: '"description:One" AND ("displayName:Video" OR "displayName:Drive")'
    ```
    ::::

<!-- -->

`group.expand`

:   Optional parameter to include the expanded resource or collection
    referenced by a single relationship (navigation property) in your
    results. Only one relationship can be expanded in a single request.
    See
    <https://docs.microsoft.com/en-us/graph/query-parameters#expand-parameter>
    This parameter can be combined with
    [variablelist_title](#userGroupMemberFilter) instead of
    [variablelist_title](#userFilter).

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `group.expand` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            group:
              expand: member
    ```
    ::::

<!-- -->

`group.filter`

:   To filter groups. See [Microsoft Graph API query group
    syntax](https://docs.microsoft.com/en-us/graph/api/resources/group?view=graph-rest-1.0#properties).

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `group.filter` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            group:
              filter: securityEnabled eq false and mailEnabled eq true and groupTypes/any(c:c+eq+'Unified')
    ```
    ::::

<!-- -->

`group.search`

:   To search for groups. See [Microsoft Graph API query search
    parameter](https://docs.microsoft.com/en-us/graph/search-query-parameter).

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `group.search` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            group:
              search: '"description:One" AND ("displayName:Video" OR "displayName:Drive")'
    ```
    ::::

<!-- -->

`group.select`

:   To define the [Microsoft Graph resource
    types](https://docs.microsoft.com/en-us/graph/api/resources/schemaextension?view=graph-rest-1.0)
    to retrieve.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `group.select` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            group:
              select: ['id', 'displayName', 'description']
    ```
    ::::

`schedule.frequency`

:   To specify custom schedule frequency. Supports cron, ISO duration,
    and \"human duration\" as used in code.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `schedule.frequency` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            schedule:
              frequency: { hours: 1 }
    ```
    ::::

`schedule.timeout`

:   To specify custom timeout. Supports ISO duration and \"human
    duration\" as used in code.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `schedule.timeout` field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            schedule:
              timeout: { minutes: 50 }
    ```
    ::::

`schedule.initialDelay`

:   To specify custom initial delay. Supports ISO duration and \"human
    duration\" as used in code.

    :::: formalpara
    ::: title
    `app-config.yaml` fragment with optional `schedule.initialDelay`
    field
    :::

    ``` yaml
    catalog:
      providers:
        microsoftGraphOrg:
          providerId:
            schedule:
              initialDelay: { seconds: 15}
    ```
    ::::

<div>

::: title
Verification
:::

1.  Check the console logs to verify that the synchronization is
    completed.

    :::: formalpara
    ::: title
    Successful synchronization example:
    :::

    ``` json
    backend:start: {"class":"MicrosoftGraphOrgEntityProvider$1","level":"info","message":"Read 1 msgraph users and 1 msgraph groups in 2.2 seconds. Committing...","plugin":"catalog","service":"backstage","taskId":"MicrosoftGraphOrgEntityProvider:default:refresh","taskInstanceId":"88a67ce1-c466-41a4-9760-825e16b946be","timestamp":"2024-06-26 12:23:42"}
    backend:start: {"class":"MicrosoftGraphOrgEntityProvider$1","level":"info","message":"Committed 1 msgraph users and 1 msgraph groups in 0.0 seconds.","plugin":"catalog","service":"backstage","taskId":"MicrosoftGraphOrgEntityProvider:default:refresh","taskInstanceId":"88a67ce1-c466-41a4-9760-825e16b946be","timestamp":"2024-06-26 12:23:42"}
    ```
    ::::

2.  Log in with a Microsoft Azure account.

</div>
