Authorized users can customize Red Hat Developer Hub appearance and
features, such as templates, Learning Paths, Tech Radar, Home page, and
quick access cards.

## Customizing your Red Hat Developer Hub title {#customizing-your-product-title}

You can change the default Red Hat Developer Hub display name.

<div>

::: title
Prerequisites
:::

- [Custom Developer Hub
  configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index).

</div>

<div>

::: title
Procedure
:::

- In your custom `app-config.yaml` file, enter your Developer Hub
  instance display name, such as *\<Red Hat Developer Hub\>*.

  :::: formalpara
  ::: title
  `app-config.yaml` excerpt
  :::

  ``` yaml
  app:
    title: My custom Red Hat Developer Hub title
  ```
  ::::

</div>

## Customizing your Red Hat Developer Hub base URL {#customizing-your-product-se-url}

You can change the default Red Hat Developer Hub base URL.

<div>

::: title
Prerequisites
:::

- You know your desired Developer Hub external URL:
  https://*\<my_developer_hub_url\>*, and have configured DNS to point
  to your Red Hat OpenShift Container Platform cluster.

- [Custom Developer Hub
  configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index).

</div>

<div>

::: title
Procedure
:::

- In your custom `app-config.yaml` file, enter your Developer Hub
  external URL, such as https://*\<my_developer_hub_url\>*.

  :::: formalpara
  ::: title
  `app-config.yaml` excerpt
  :::

  ``` yaml
  app:
    baseUrl: https://<my_developer_hub_url>
  backend:
    baseUrl: https://<my_developer_hub_url>
    cors:
      origin: https://<my_developer_hub_url>
  ```
  ::::

</div>

## Customizing Red Hat Developer Hub backend secret {#customizing-the-backend-secret}

The default Red Hat Developer Hub configuration defines the Developer
Hub backend secret for service to service authentication.

You can define your custom Developer Hub backend secret.

<div>

::: title
Prerequisites
:::

- You [added a custom Developer Hub application
  configuration](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index),
  and have sufficient permissions to modify it.

</div>

<div>

::: title
Procedure
:::

1.  To define the Developer Hub backend secret, add to your custom
    `<my_product_secrets>.txt` file the `BACKEND_SECRET` environment
    variable with a base64 encoded string. Use a unique value for each
    Developer Hub instance.

    ``` yaml
    $ echo > <my_product_secrets>.txt "BACKEND_SECRET=$(node -p 'require("crypto").randomBytes(24).toString("base64")')"
    ```

    :::: formalpara
    ::: title
    `<my_product_secrets>.txt` example
    :::

        BACKEND_SECRET=3E2/rIPuZNFCtYHoxVP8wjriffnN1q/z
    ::::

2.  Add your backend secret to your custom `app-config.yaml` file.

    :::: formalpara
    ::: title
    `app-config.yaml` excerpt defining the backend secret
    :::

    ``` yaml
    backend:
      auth:
        externalAccess:
          - type: legacy
            options:
              subject: legacy-default-config
              secret: "${BACKEND_SECRET}"
    ```
    ::::

</div>

## Configuring templates

Configure templates to create software components, and publish these
components to different locations, such as the Red Hat Developer Hub
software catalog, or Git repositories.

A template is a form composed of different UI fields that is defined in
a YAML file. Templates include *actions*, which are steps that are
executed in sequential order and can be executed conditionally.

### Creating a template by using the Template Editor {#proc-creating-templates_configuring-templates}

You can create a template by using the Template Editor.

<div>

::: title
Procedure
:::

1.  Access the Template Editor by using one of the following options:

    ![Template Editor](images/rhdh/template-editor.png)

    - Open the URL `https://<rhdh_url>/create/edit` for your Red Hat
      Developer Hub instance.

    - Click **Self-service** in the navigation menu of the Red Hat
      Developer Hub console, then click the overflow menu button and
      select **Template editor**.

2.  Click **Edit Template Form**.

3.  Optional: Modify the YAML definition for the parameters of your
    template. For more information about these parameters, see [Creating
    a template as a YAML
    file](#ref-creating-templates_configuring-templates).

4.  In the **Name** field, enter a unique name for your template.

5.  From the **Owner** drop-down menu, choose an owner for the template.

6.  Click **Next**.

7.  In the **Repository Location** view, enter the following information
    about the hosted repository that you want to publish the template
    to:

    a.  Select an available **Host** from the drop-down menu.

        :::::: note
        ::: title
        :::

        Available hosts are defined in the YAML parameters by the
        `allowedHosts` field:

        :::: formalpara
        ::: title
        Example YAML
        :::

        ``` yaml
        # ...
                ui:options:
                  allowedHosts:
                    - github.com
        # ...
        ```
        ::::
        ::::::

    b.  In the **Owner \*** field, enter an organization, user or
        project that the hosted repository belongs to.

    c.  In the **Repository \*** field, enter the name of the hosted
        repository.

    d.  Click **Review**.

8.  Review the information for accuracy, then click **Create**.

</div>

<div>

::: title
Verification
:::

1.  Click the **Catalog** tab in the navigation panel.

2.  In the **Kind** drop-down menu, select **Template**.

3.  Confirm that your template is shown in the list of existing
    templates.

</div>

### Creating a template as a YAML file {#ref-creating-templates_configuring-templates}

You can create a template by defining a `Template` object as a YAML
file.

The `Template` object describes the template and its metadata. It also
contains required input variables and a list of actions that are
executed by the scaffolding service.

:::: formalpara
::: title
`Template` object example
:::

``` yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: template-name
  title: Example template
  description: An example template for v1beta3 scaffolder.
spec:
  owner: backstage/techdocs-core
  type: service
  parameters:
    - title: Fill in some steps
      required:
        - name
      properties:
        name:
          title: Name
          type: string
          description: Unique name of the component
        owner:
          title: Owner
          type: string
          description: Owner of the component
    - title: Choose a location
      required:
        - repoUrl
      properties:
        repoUrl:
          title: Repository Location
          type: string
  steps:
    - id: fetch-base
      name: Fetch Base
      action: fetch:template
      # ...
  output:
    links:
      - title: Repository
        url: ${{ steps['publish'].output.remoteUrl }}
      - title: Open in catalog
        icon: catalog
        entityRef: ${{ steps['register'].output.entityRef }}
# ...
```
::::

- Specify a name for the template.

- Specify a title for the template. This is the title that is visible on
  the template tile in the **Self-service** view.

- Specify a description for the template. This is the description that
  is visible on the template tile in the **Self-service** view.

- Specify the ownership of the template. The `owner` field provides
  information about who is responsible for maintaining or overseeing the
  template within the system or organization. In the provided example,
  the `owner` field is set to `backstage/techdocs-core`. This means that
  this template belongs to the `techdocs-core` project in the
  `backstage` namespace.

- Specify the component type. Any string value is accepted for this
  required field, but your organization should establish a proper
  taxonomy for these. Red Hat Developer Hub instances may read this
  field and behave differently depending on its value. For example, a
  `website` type component may present tooling in the Red Hat Developer
  Hub interface that is specific to just websites.

  The following values are common for this field:

  `service`

  :   A backend service, typically exposing an API.

  `website`

  :   A website.

  `library`

  :   A software library, such as an npm module or a Java library.

- Use the `parameters` section to specify parameters for user input that
  are shown in a form view when a user creates a component by using the
  template in the Red Hat Developer Hub console. Each `parameters`
  subsection, defined by a title and properties, creates a new form page
  with that definition.

- Use the `steps` section to specify steps that are executed in the
  backend. These steps must be defined by using a unique step ID, a
  name, and an action. You can view actions that are available on your
  Red Hat Developer Hub instance by visiting the URL
  `https://<rhdh_url>/create/actions`.

- Use the `output` section to specify the structure of output data that
  is created when the template is used. The `output` section,
  particularly the `links` subsection, provides valuable references and
  URLs that users can utilize to access and interact with components
  that are created from the template.

- Provides a reference or URL to the repository associated with the
  generated component.

- Provides a reference or URL that allows users to open the generated
  component in a catalog or directory where various components are
  listed.

<div>

::: title
Additional resources
:::

- [Backstage documentation - Writing
  Templates](https://backstage.io/docs/features/software-templates/writing-templates)

- [Backstage documentation - Builtin
  actions](https://backstage.io/docs/features/software-templates/builtin-actions)

- [Backstage documentation - Writing Custom
  Actions](https://backstage.io/docs/features/software-templates/writing-custom-actions)

</div>

### Importing an existing template to Red Hat Developer Hub {#proc-adding-templates_configuring-templates}

You can add an existing template to your Red Hat Developer Hub instance
by using the Catalog Processor.

<div>

::: title
Prerequisites
:::

- You have created a directory or repository that contains at least one
  template YAML file.

- If you want to use a template that is stored in a repository such as
  GitHub or GitLab, you must configure a Red Hat Developer Hub
  integration for your provider.

</div>

<div>

::: title
Procedure
:::

- In the `app-config.yaml` configuration file, modify the
  `catalog.rules` section to include a rule for templates, and configure
  the `catalog.locations` section to point to the template that you want
  to add, as shown in the following example:

  ``` yaml
  # ...
  catalog:
    rules:
      - allow: [Template]
    locations:
      - type: url
        target: https://<repository_url>/example-template.yaml
  # ...
  ```

  - To allow new templates to be added to the catalog, you must add a
    `Template` rule.

  - If you are importing templates from a repository, such as GitHub or
    GitLab, use the `url` type.

  - Specify the URL for the template.

</div>

<div>

::: title
Verification
:::

1.  Click the **Catalog** tab in the navigation panel.

2.  In the **Kind** drop-down menu, select **Template**.

3.  Confirm that your template is shown in the list of existing
    templates.

</div>

<div>

::: title
Additional resources
:::

- [Enabling the GitHub authentication
  provider](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/authentication_in_red_hat_developer_hub/index#assembly-auth-provider-github)

</div>

## Customizing the Learning Paths in Red Hat Developer Hub {#proc-customize-rhdh-learning-paths_configuring-templates}

In Red Hat Developer Hub, you can configure Learning Paths by hosting
the required data externally, and using the built-in proxy to deliver
this data rather than the default.

You can provide Learning Paths data from the following sources:

- A JSON file hosted on a web server, such as GitHub or GitLab.

- A dedicated service that provides the Learning Paths data in JSON
  format using an API.

### Customizing the Learning Paths by using a hosted JSON file {#proc-customizing-the-learning-paths-by-using-a-hosted-json-file_configuring-templates}

For ease of use and simplicity, you can configure the Learning Paths by
using a hosted JSON file.

<div>

::: title
Procedure
:::

1.  Publish the JSON file containing your Learning Paths data to a web
    server, such as GitHub or Gitlab. You can find an example at
    <https://raw.githubusercontent.com/redhat-developer/rhdh/release-1.6/packages/app/public/learning-paths/data.json>.

2.  Configure the Developer Hub proxy to access the Learning Paths data
    from the hosted JSON file, by adding the following to the
    `app-config.yaml` file:

    ``` yaml
    proxy:
      endpoints:
        '/developer-hub':
          target: <target>
          pathRewrite:
            '^/api/proxy/developer-hub/learning-paths': '<learning_path.json>'
          changeOrigin: true
          secure: true
    ```

    `<target>`

    :   Enter the hosted JSON file base URL, such as
        `https://raw.githubusercontent.com`.

    `<learning_path.json>`

    :   Enter the hosted JSON file path without the base URL, such as
        `'/redhat-developer/rhdh/main/packages/app/public/learning-paths/data.json'`

        :::: tip
        ::: title
        :::

        When also configuring the home page, due to the use of
        overlapping `pathRewrites` for both the `learning-path` and
        `homepage` quick access proxies, create the `learning-paths`
        configuration (`^api/proxy/developer-hub/learning-paths`) before
        you create the `homepage` configuration
        (`^/api/proxy/developer-hub`). For example:

        ``` yaml
        proxy:
          endpoints:
            '/developer-hub':
              target: https://raw.githubusercontent.com/
              pathRewrite:
                '^/api/proxy/developer-hub/learning-paths': '/redhat-developer/rhdh/main/packages/app/public/learning-paths/data.json'
                '^/api/proxy/developer-hub/tech-radar': '/redhat-developer/rhdh/main/packages/app/public/tech-radar/data-default.json'
                '^/api/proxy/developer-hub': '/redhat-developer/rhdh/main/packages/app/public/homepage/data.json'
              changeOrigin: true
              secure: true
        ```
        ::::

</div>

<div>

::: title
Additional resources
:::

- [Customizing the Home page in Red Hat Developer
  Hub](#customizing-the-home-page).

</div>

### Customizing the Learning Paths by using a customization service {#proc-customizing-the-learning-paths-by-using-a-customization-service_configuring-templates}

For advanced scenarios, you can host your Red Hat Developer Hub
customization service to provide data to all configurable Developer Hub
pages, such as the Learning Paths. You can even use a different service
for each page.

<div>

::: title
Procedure
:::

1.  Deploy your Developer Hub customization service on the same
    OpenShift Container Platform cluster as your Developer Hub instance.
    You can find an example at
    [`red-hat-developer-hub-customization-provider`](https://github.com/redhat-developer/red-hat-developer-hub-customization-provider),
    that provides the same data as default Developer Hub data. The
    customization service provides a Learning Paths data URL such as:
    `http://<rhdh-customization-provider>/learning-paths`.

2.  Configure the Developer Hub proxy to use your dedicated service to
    provide the Learning Path data, add the following to the
    [`app-config.yaml`
    file](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index):

    ``` yaml
    proxy:
      endpoints:
        '/developer-hub/learning-paths':
          target: <learning_path_data_url>
          changeOrigin: true
          qsecure: true
    ```

    - Change to \"false\" in case of using self hosted cluster with a
      self-signed certificate

</div>

## Configuring the global header in Red Hat Developer Hub {#configuring-the-global-header-in-rhdh}

As an administrator, you can configure the Red Hat Developer Hub global
header to create a consistent and flexible navigation bar across your
Developer Hub instance. By default, the Developer Hub global header
includes the following components:

- **Self-service** button provides quick access to a variety of
  templates, enabling users to efficiently set up services, backend and
  front-end plugins within Developer Hub

- **Support** button that can link an internal or external support page

- **Notifications** button displays alerts and updates from plugins and
  external services

- **Search** input field allows users to find services, components,
  documentation, and other resources within Developer Hub

- **Plugin extension capabilities** provide a preinstalled and enabled
  catalog of available plugins in Developer Hub

- **User profile** drop-down menu provides access to profile settings,
  appearance customization, Developer Hub metadata, and a logout button

### Customizing your Red Hat Developer Hub global header {#customizing-your-product-global-header_configuring-the-global-header-in-rhdh}

You can use the `red-hat-developer-hub.backstage-plugin-global-header`
dynamic plugin to extend the global header with additional buttons and
customize the order and position of icons and features. Additionally,
you can create and integrate your custom dynamic header plugins using
the mount points provided by this new header feature, allowing you to
further tailor to suit your needs. For more information about enabling
dynamic plugins, see [Installing and viewing plugins in Red Hat
Developer
Hub](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_and_viewing_plugins_in_red_hat_developer_hub/index).

:::: formalpara
::: title
Default global header configuration
:::

``` yaml
  - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-global-header
    disabled: false
    pluginConfig:
      app:
        sidebar:
          search: false
          settings: false
      dynamicPlugins:
        frontend:
          default.main-menu-items:
            menuItems:
              default.create:
                title: ''
          red-hat-developer-hub.backstage-plugin-global-header: # the default enabled dynamic header plugin
            mountPoints:
              - mountPoint: application/header
                importName: GlobalHeader
                config:
                  position: above-main-content
              - mountPoint: global.header/component
                importName: SearchComponent
                config:
                  priority: 100
              - mountPoint: global.header/component
                importName: Spacer
                config:
                  priority: 99
                  props:
                    growFactor: 0
              - mountPoint: global.header/component
                importName: HeaderIconButton
                config:
                  priority: 90
                  props:
                    title: Self-service
                    icon: add
                    to: create
              - mountPoint: global.header/component
                importName: SupportButton
                config:
                  priority: 80
              - mountPoint: global.header/component
                importName: NotificationButton
                config:
                  priority: 70
              - mountPoint: global.header/component
                importName: Divider
                config:
                  priority: 50
              - mountPoint: global.header/component
                importName: ProfileDropdown
                config:
                  priority: 10
              - mountPoint: global.header/profile
                importName: MenuItemLink
                config:
                  priority: 100
                  props:
                    title: Settings
                    link: /settings
                    icon: manageAccounts
              - mountPoint: global.header/profile
                importName: LogoutButton
                config:
                  priority: 10
```
::::

- **search**: Hides the **Search** modal in the sidebar menu. Change it
  to `true` to display the **Search** modal in the sidebar.

- **settings**: Hides the **Settings** button in the sidebar menu.
  Change it to `true` to display the **Settings** button in the sidebar.

- `default.main-menu-items`: Hides the **Self-service** button from the
  sidebar menu. Remove this field to display the **Self-service** button
  in the sidebar.

- **position**: Defines the position of the header. Options:
  `above-main-content` or `above-sidebar`.

To extend the functionality of the default global header, include any
the following attributes in your global header entry:

`mountPoint`

:   Specifies the location of the header. Use `application/header` to
    specify it as a global header. You can configure several global
    headers at different positions by adding entries to the
    `mountPoints` field.

`importName`

:   Specifies the component exported by the global header plugin.

    The `red-hat-developer-hub.backstage-plugin-global-header` package
    (enabled by default) offers the following header components as
    possible mount point values:

    - **`SearchComponent`**: Adds a search bar (enabled by default).

    - **`Spacer`**: Adds spacing in the header to position buttons at
      the end. Useful when you disable `SearchComponent`.

    - **`HeaderIconButton`**: Adds an icon button. By default, the
      **Self-service** icon button remains enabled.

    - **`SupportButton`**: Adds a **Support** icon button, allowing
      users to configure a link to an internal or external page. Enabled
      by default but requires additional configuration to display.

    - **`NotificationButton`**: Adds a **Notifications** icon button to
      display unread notifications in real time and navigate to the
      **Notifications** page. Enabled by default (requires the
      notifications plugin).

    - **`Divider`**: Adds a vertical divider. By default, a divider
      appears between the profile dropdown and other header components.

    - **`ProfileDropdown`**: Adds a profile dropdown showing the
      logged-in user's name. By default, it contains two menu items.

    - **`MenuItemLink`**: Adds a link item in a dropdown menu. By
      default, the profile dropdown includes a link to the **Settings**
      page.

    - **`LogoutButton`**: Adds a logout button in the profile dropdown
      (enabled by default).

    - **`CreateDropdown`**: Adds a **Self-service** dropdown button
      (disabled by default). The menu items are configurable.

    - **`SoftwareTemplatesSection`**: Adds a list of software template
      links to the **Self-service** dropdown menu (disabled by default).
      You must enable `CreateDropdown`.

    - **`RegisterAComponentSection`**: Adds a link to the **Register a
      Component** page in the **Self-service** dropdown menu (disabled
      by default). You must enable `CreateDropdown`.

`config.position`

:   Specifies the position of the header. Supported values are
    `above-main-content` and `above-sidebar`.

<div>

::: title
Prerequisites
:::

- You must configure the support URL in the `app-config.yaml` file to
  display the **Support** button in the header.

- You must install the notifications plugin to display the
  **Notifications** button in the header.

</div>

<div>

::: title
Procedure
:::

1.  Copy the default configuration and modify the field values to suit
    your needs. You can adjust the `priority` value of each header
    component to control its position. Additionally, you can enable or
    disable components by adding or removing them from the
    configuration. To ensure that the remaining header buttons align
    with the end of the header before the profile dropdown button, set
    `config.props.growFactor` to `1` in the `Spacer` mount point to
    enable the `Spacer` component. For example:

    ``` yaml
    - mountPoint: global.header/component
      importName: Spacer
      config:
        priority: 100
        props:
          growFactor: 1
    ```

2.  To use your custom header, you must install it as a dynamic plugin
    by adding your plugin configuration to your
    `app-config-dynamic.yaml` file. For example:

    ``` yaml
    - package: <npm_or_oci_package-reference>
      disabled: false
      pluginConfig:
        dynamicPlugins:
          frontend:
            <package_name>:
              mountPoints:
                - mountPoint: application/header
                  importName: <application_header_name>
                  config:
                    position: above-main-content
                - mountPoint: global.header/component
                  importName: <header_component_name>
                  config:
                    priority: 100
                - mountPoint: global.header/component
                  importName: <header_component_name>
                  config:
                    priority: 90
    ```

    where:

    \<npm_or_oci_package-reference\>

    :   Specifies the package name.

    \<application_header_name\>

    :   Specifies the name of the application header. For example:
        `MyHeader`

    \<header_component_name\>

    :   Specifies the name of the header component. For example:
        `MyHeaderComponent`

        :::: note
        ::: title
        :::

        `importName` is an optional name referencing the value returned
        by the scaffolder field extension API.
        ::::

3.  Optional: To disable the global header, set the value of the
    `disabled` field to `true` in your `dynamic-plugins.yaml` file. For
    example:

    ``` yaml
    - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-global-header
      disabled: true
    ```

</div>

### Mount points for dynamic plugin integration {#mount-points-for-dynamic-plugin-intergration_configuring-the-global-header-in-rhdh}

You can customize the application header in Developer Hub using mount
points for dynamic plugins. These mount points give flexibility in
configuring the position of the header, its components and dropdown
menus. You can create a customized experience with the following
enhancements:

application/header

:   Controls the header position. Use `config.position` to set placement
    as either `above-main-content` or `above-sidebar`.

global.header/component

:   Configures header components. Use `config.priority` to set the order
    of components, and pass properties (including CSS styles) via
    `config.props`.

    :::: formalpara
    ::: title
    Example adding a **Self-service** button
    :::

    ``` yaml
    - mountPoint: global.header/component
      importName: HeaderIconButton
      config:
        priority: 80
        props:
          title: Self-service
          icon: add
          to: create
    ```
    ::::

    :::: formalpara
    ::: title
    Example adding a spacer element
    :::

    ``` yaml
    - mountPoint: global.header/component
      importName: Spacer
      config:
        priority: 99
        props:
          growFactor: 0
    ```
    ::::

    :::: formalpara
    ::: title
    Example adding a divider element
    :::

    ``` yaml
    mountPoints:
      - mountPoint: global.header/component
        importName: Divider
        config:
          priority: 150
    ```
    ::::

global.header/profile

:   Configures the profile dropdown list when the `ProfileDropdown`
    component is enabled.

    :::: formalpara
    ::: title
    Example adding a settings link to the profile dropdown
    :::

    ``` yaml
    - mountPoint: global.header/profile
      importName: MenuItemLink
      config:
        priority: 100
        props:
          title: Settings
          link: /settings
          icon: manageAccounts
    ```
    ::::

global.header/create

:   Configures the create dropdown list when the `CreateDropdown`
    component is enabled.

    :::: formalpara
    ::: title
    Example adding a section for registering a component
    :::

    ``` yaml
    - mountPoint: global.header/create
      importName: RegisterAComponentSection
      config:
        props:
          growFactor: 0
    ```
    ::::

## Configuring a floating action button in Red Hat Developer Hub {#configuring-a-floating-action-button}

You can use the floating action button plugin to configure any action as
a floating button in the Developer Hub instance. The floating action
button plugin is enabled by default. You can also configure floating
action buttons to display as submenu options within the main floating
action button by assigning the floating action buttons to the same
`slot` field of your `dynamic-plugins.yaml` file.

### Configuring a floating action button as a dynamic plugin {#proc-configuring-floating-action-button-as-a-dynamic-plugin_configuring-a-floating-action-button}

You can configure the floating action button as a dynamic plugin to
perform actions or open an internal or external link.

:::: formalpara
::: title
Prerequisties
:::

You must have sufficient permissions as a platform engineer.
::::

:::: formalpara
::: title
Procedure
:::

To configure a floating action button as a dynamic plugin, complete any
of the following tasks:
::::

- Specify the `global.floatingactionbutton/config` mount point in your
  `app-config-dynamic.yaml` file. For example:

  :::: formalpara
  ::: title
  Example of a bulk-import plugin as a floating action button
  :::

  ``` yaml
  - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-bulk-import
    disabled: false
    pluginConfig:
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-bulk-import:
            # Start of the floating action button configuration
            mountPoints:
              - mountPoint: global.floatingactionbutton/config
                importName: BulkImportPage
                config:
                  slot: 'page-end'
                  icon: <svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24px" viewBox="0 0 24 24" width="24px" fill="#e8eaed"><g><rect fill="none" height="24" width="24"/></g><g><path d="M11,7L9.6,8.4l2.6,2.6H2v2h10.2l-2.6,2.6L11,17l5-5L11,7z M20,19h-8v2h8c1.1,0,2-0.9,2-2V5c0-1.1-0.9-2-2-2h-8v2h8V19z"/></g></svg>
                  label: 'Bulk import'
                  toolTip: 'Register multiple repositories in bulk'
                  to: /bulk-import/repositories
            # End of the floating action button configuration
            appIcons:
              - name: bulkImportIcon
                importName: BulkImportIcon
            dynamicRoutes:
              - path: /bulk-import/repositories
                importName: BulkImportPage
                menuItem:
                  icon: bulkImportIcon
                  text: Bulk import
  ```
  ::::

  - (Required) The import name with an associated component to the mount
    point.

  - Use the `svg` value to display a black BulkImportPage icon.

- To configure an action as a floating action button that opens an
  external link, specify the `global.floatingactionbutton/config` mount
  point in your `dynamic-plugins.yaml` file within the
  `backstage-plugin-global-floating-action-button` plugin. For example:

  :::: formalpara
  ::: title
  Example of a floating action button that opens GitHub
  :::

  ``` yaml
  - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-global-floating-action-button
    disabled: false
    pluginConfig:
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-global-floating-action-button:
            mountPoints:
                - mountPoint: application/listener
                  importName: DynamicGlobalFloatingActionButton
                - mountPoint: global.floatingactionbutton/config
                  importName: NullComponent
                  config:
                    icon: '<svg viewBox="0 0 250 300" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid"><path d="M200.134 0l55.555 117.514-55.555 117.518h-47.295l55.555-117.518L152.84 0h47.295zM110.08 99.836l20.056-38.092-2.29-8.868L102.847 0H55.552l48.647 102.898 5.881-3.062zm17.766 74.433l-17.333-39.034-6.314-3.101-48.647 102.898h47.295l25-52.88v-7.883z" fill="#40B4E5"/><path d="M152.842 235.032L97.287 117.514 152.842 0h47.295l-55.555 117.514 55.555 117.518h-47.295zm-97.287 0L0 117.514 55.555 0h47.296L47.295 117.514l55.556 117.518H55.555z" fill="#003764"/></svg>'
                    label: 'Quay'
                    showLabel: true
                    toolTip: 'Quay'
                    to: 'https://quay.io'
                - mountPoint: global.floatingactionbutton/config
                  importName: NullComponent
                  config:
                    icon: github
                    label: 'Git'
                    toolTip: 'Github'
                    to: https://github.com/redhat-developer/rhdh-plugins
  ```
  ::::

  - (Required) The import name with an associated component to the mount
    point.

  - Use the `svg` value to display the `Quay` icon.

- To configure a floating action button that contains a submenu, define
  the `global.floatingactionbutton/config` mount point in the same
  `slot` field in your `dynamic-plugins.yaml` file for multiple actions.
  The default slot is `page-end` when not specified. For example:

  :::: formalpara
  ::: title
  Example of a floating action button with submenu actions
  :::

  ``` yaml
  - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-bulk-import
    disabled: false
    pluginConfig:
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-bulk-import:
            # Start of fab config
            mountPoints:
              - mountPoint: global.floatingactionbutton/config
                importName: BulkImportPage
                config:
                  slot: 'page-end'
                  icon: <svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24px" viewBox="0 0 24 24" width="24px" fill="#e8eaed"><g><rect fill="none" height="24" width="24"/></g><g><path d="M11,7L9.6,8.4l2.6,2.6H2v2h10.2l-2.6,2.6L11,17l5-5L11,7z M20,19h-8v2h8c1.1,0,2-0.9,2-2V5c0-1.1-0.9-2-2-2h-8v2h8V19z"/></g></svg>
                  label: 'Bulk import'
                  toolTip: 'Register multiple repositories in bulk'
                  to: /bulk-import/repositories
            # end of fab config
            appIcons:
              - name: bulkImportIcon
                importName: BulkImportIcon
            dynamicRoutes:
              - path: /bulk-import/repositories
                importName: BulkImportPage
                menuItem:
                  icon: bulkImportIcon
                  text: Bulk import

  - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-global-floating-action-button
    disabled: false
    pluginConfig:
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-global-floating-action-button:
            mountPoints:
              - mountPoint: application/listener
                importName: DynamicGlobalFloatingActionButton
              - mountPoint: global.floatingactionbutton/config
                importName: NullComponent
                config:
                  icon: github
                  label: 'Git'
                  toolTip: 'Github'
                  to: https://github.com/redhat-developer/rhdh-plugins
              - mountPoint: global.floatingactionbutton/config
                importName: NullComponent
                config:
                  icon: '<svg viewBox="0 0 250 300" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid"><path d="M200.134 0l55.555 117.514-55.555 117.518h-47.295l55.555-117.518L152.84 0h47.295zM110.08 99.836l20.056-38.092-2.29-8.868L102.847 0H55.552l48.647 102.898 5.881-3.062zm17.766 74.433l-17.333-39.034-6.314-3.101-48.647 102.898h47.295l25-52.88v-7.883z" fill="#40B4E5"/><path d="M152.842 235.032L97.287 117.514 152.842 0h47.295l-55.555 117.514 55.555 117.518h-47.295zm-97.287 0L0 117.514 55.555 0h47.296L47.295 117.514l55.556 117.518H55.555z" fill="#003764"/></svg>'
                  label: 'Quay'
                  showLabel: true
                  toolTip: 'Quay'
                  to: 'https://quay.io'
  ```
  ::::

  - (Required) The import name with an associated component to the mount
    point.

- To configure a floating action button to display only on specific
  pages, configure the `global.floatingactionbutton/config` mount point
  in the `backstage-plugin-global-floating-action-button` plugin and set
  the `visibleOnPaths` property as shown in the following example:

  :::: formalpara
  ::: title
  Example of a floating action button to display specific pages
  :::

  ``` yaml
  - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-bulk-import
    disabled: false
    pluginConfig:
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-bulk-import:
            # start of fab config
            mountPoints:
              - mountPoint: global.floatingactionbutton/config
                importName: BulkImportPage
                config:
                  slot: 'page-end'
                  icon: <svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24px" viewBox="0 0 24 24" width="24px" fill="#e8eaed"><g><rect fill="none" height="24" width="24"/></g><g><path d="M11,7L9.6,8.4l2.6,2.6H2v2h10.2l-2.6,2.6L11,17l5-5L11,7z M20,19h-8v2h8c1.1,0,2-0.9,2-2V5c0-1.1-0.9-2-2-2h-8v2h8V19z"/></g></svg>
                  label: 'Bulk import'
                  toolTip: 'Register multiple repositories in bulk'
                  to: /bulk-import/repositories
                  visibleOnPaths: ['/catalog', '/settings']
            # end of fab config
            appIcons:
              - name: bulkImportIcon
                importName: BulkImportIcon
            dynamicRoutes:
              - path: /bulk-import/repositories
                importName: BulkImportPage
                menuItem:
                  icon: bulkImportIcon
                  text: Bulk import
  ```
  ::::

  - (Required) The import name with an associated component to the mount
    point.

- To hide a floating action button on specific pages, configure the
  `global.floatingactionbutton/config` mount point in the
  `backstage-plugin-global-floating-action-button` plugin and set the
  `excludeOnPaths` property as shown in the following example:

  :::: formalpara
  ::: title
  Example of a floating action button to hide specific pages
  :::

  ``` yaml
  - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-bulk-import
    disabled: false
    pluginConfig:
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-bulk-import:
            # start of fab config
            mountPoints:
              - mountPoint: global.floatingactionbutton/config
                importName: BulkImportPage
                config:
                  slot: 'page-end'
                  icon: <svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24px" viewBox="0 0 24 24" width="24px" fill="#e8eaed"><g><rect fill="none" height="24" width="24"/></g><g><path d="M11,7L9.6,8.4l2.6,2.6H2v2h10.2l-2.6,2.6L11,17l5-5L11,7z M20,19h-8v2h8c1.1,0,2-0.9,2-2V5c0-1.1-0.9-2-2-2h-8v2h8V19z"/></g></svg>
                  label: 'Bulk import'
                  toolTip: 'Register multiple repositories in bulk'
                  to: /bulk-import/repositories
                  excludeOnPaths: ['/bulk-import']
            # end of fab config
            appIcons:
              - name: bulkImportIcon
                importName: BulkImportIcon
            dynamicRoutes:
              - path: /bulk-import/repositories
                importName: BulkImportPage
                menuItem:
                  icon: bulkImportIcon
                  text: Bulk import
  ```
  ::::

  - (Required) The import name with an associated component to the mount
    point.

#### Floating action button parameters {#_floating-action-button-parameters}

Use the parameters as shown in the following table to configure your
floating action button plugin.

+-------------+-------------+-------------+-------------+-------------+
| Name        | Description | Type        | Default     | Required    |
|             |             |             | value       |             |
+=============+=============+=============+=============+=============+
| `slot`      | Position of | `enum`      | `PAGE_END`  | No          |
|             | the         |             |             |             |
|             | floating    |             |             |             |
|             | action      |             |             |             |
|             | button.     |             |             |             |
|             | Valid       |             |             |             |
|             | values:     |             |             |             |
|             | `PAGE_END`, |             |             |             |
|             | `B          |             |             |             |
|             | OTTOM_LEFT` |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `label`     | Name of the | `String`    | Not         | Yes         |
|             | floating    |             | applicable  |             |
|             | action      |             |             |             |
|             | button      |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `icon`      | Icon of the | `String`,   | Not         | No          |
|             | floating    | `React.Rea  | applicable  |             |
|             | action      | ctElement`, |             |             |
|             | button.     | `SVG i      |             |             |
|             | Recommended | mage icon`, |             |             |
|             | to use      | `HTML       |             |             |
|             | filled      | image icon` |             |             |
|             | icons from  |             |             |             |
|             | the         |             |             |             |
|             | [Material   |             |             |             |
|             | Design      |             |             |             |
|             | library]    |             |             |             |
|             | (https://fo |             |             |             |
|             | nts.google. |             |             |             |
|             | com/icons). |             |             |             |
|             | You can     |             |             |             |
|             | also use an |             |             |             |
|             | svg icon.   |             |             |             |
|             | For         |             |             |             |
|             | example:    |             |             |             |
|             | `<svg x     |             |             |             |
|             | mlns="http: |             |             |             |
|             | //www.w3.or |             |             |             |
|             | g/2000/svg" |             |             |             |
|             |  enable-bac |             |             |             |
|             | kground="ne |             |             |             |
|             | w 0 0 24 24 |             |             |             |
|             | " height="2 |             |             |             |
|             | 4px" viewBo |             |             |             |
|             | x="0 0 24 2 |             |             |             |
|             | 4" width="2 |             |             |             |
|             | 4px" fill=" |             |             |             |
|             | #e8eaed"><g |             |             |             |
|             | ><rect fill |             |             |             |
|             | ="none" hei |             |             |             |
|             | ght="24" wi |             |             |             |
|             | dth="24"/>< |             |             |             |
|             | /g><g><path |             |             |             |
|             |  d="M11,7L9 |             |             |             |
|             | .6,8.4l2.6, |             |             |             |
|             | 2.6H2v2h10. |             |             |             |
|             | 2l-2.6,2.6L |             |             |             |
|             | 11,17l5-5L1 |             |             |             |
|             | 1,7z M20,19 |             |             |             |
|             | h-8v2h8c1.1 |             |             |             |
|             | ,0,2-0.9,2- |             |             |             |
|             | 2V5c0-1.1-0 |             |             |             |
|             | .9-2-2-2h-8 |             |             |             |
|             | v2h8V19z"/> |             |             |             |
|             | </g></svg>` |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `showLabel` | Display of  | `Boolean`   | Not         | No          |
|             | the label   |             | applicable  |             |
|             | next to     |             |             |             |
|             | your icon   |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `size`      | Size of the | `small`,    | `medium`    | No          |
|             | floating    | `medium`,   |             |             |
|             | action      | `large`     |             |             |
|             | button      |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `color`     | Color of    | `default`,  | `default`   | No          |
|             | the         | `error`,    |             |             |
|             | component.  | `info`,     |             |             |
|             | It supports | `inherit`,  |             |             |
|             | both        | `primary`,  |             |             |
|             | default and | `           |             |             |
|             | custom      | secondary`, |             |             |
|             | theme       | `success`,  |             |             |
|             | colors,     | `warning`   |             |             |
|             | that are    |             |             |             |
|             | added from  |             |             |             |
|             | the         |             |             |             |
|             | [Palette    |             |             |             |
|             | Getting     |             |             |             |
|             | started     |             |             |             |
|             | guide](     |             |             |             |
|             | https://mui |             |             |             |
|             | .com/materi |             |             |             |
|             | al-ui/custo |             |             |             |
|             | mization/pa |             |             |             |
|             | lette/#cust |             |             |             |
|             | om-colors). |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `onClick`   | Performed   | `Re         | Not         | No          |
|             | action when | act.MouseEv | applicable  |             |
|             | selecting a | entHandler` |             |             |
|             | floating    |             |             |             |
|             | action      |             |             |             |
|             | button      |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `to`        | Link that   | `String`    | Not         | No          |
|             | opens when  |             | applicable  |             |
|             | selecting a |             |             |             |
|             | floating    |             |             |             |
|             | action      |             |             |             |
|             | button      |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `toolTip`   | Text that   | `String`    | Not         | No          |
|             | appears     |             | applicable  |             |
|             | when        |             |             |             |
|             | hovering    |             |             |             |
|             | over a      |             |             |             |
|             | floating    |             |             |             |
|             | action      |             |             |             |
|             | button      |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `priority`  | Order of    | `number`    | Not         | No          |
|             | the         |             | applicable  |             |
|             | floating    |             |             |             |
|             | action      |             |             |             |
|             | buttons     |             |             |             |
|             | displayed   |             |             |             |
|             | in the      |             |             |             |
|             | submenu. A  |             |             |             |
|             | larger      |             |             |             |
|             | value means |             |             |             |
|             | higher      |             |             |             |
|             | priority.   |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `visi       | Display     | `string[]`  | Display     | No          |
| bleOnPaths` | floating    |             | floating    |             |
|             | action      |             | action      |             |
|             | button on   |             | button on   |             |
|             | the         |             | all paths   |             |
|             | specified   |             |             |             |
|             | paths       |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| `excl       | Hide        | `string[]`  | Display     | No          |
| udeOnPaths` | floating    |             | floating    |             |
|             | action      |             | action      |             |
|             | button on   |             | button on   |             |
|             | the         |             | all paths   |             |
|             | specified   |             |             |             |
|             | paths       |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

: Floating action button parameters

:::: note
::: title
:::

If multiple floating button actions are assigned to the same `slot`
value, the floating buttons are displayed as submenu options within the
main floating action button.
::::

## Customizing the Tech Radar page in Red Hat Developer Hub {#proc-customizing-the-tech-radar-page_configuring-a-floating-action-button}

In Red Hat Developer Hub, the Tech Radar page is provided by the
`tech-radar` dynamic plugin, which is disabled by default. For
information about enabling dynamic plugins in Red Hat Developer Hub see
[Configuring dynamic
plugins](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/introduction_to_plugins/index).

In Red Hat Developer Hub, you can configure Learning Paths by passing
the data into the `app-config.yaml` file as a proxy. The base Tech Radar
URL must include the `/developer-hub/tech-radar` proxy.

:::: note
::: title
:::

Due to the use of overlapping `pathRewrites` for both the `tech-radar`
and `homepage` quick access proxies, you must create the `tech-radar`
configuration (`^api/proxy/developer-hub/tech-radar`) before you create
the `homepage` configuration (`^/api/proxy/developer-hub`).

For more information about customizing the Home page in Red Hat
Developer Hub, see [Customizing the Home page in Red Hat Developer
Hub](#customizing-the-home-page).
::::

You can provide data to the Tech Radar page from the following sources:

- JSON files hosted on GitHub or GitLab.

- A dedicated service that provides the Tech Radar data in JSON format
  using an API.

### Customizing the Tech Radar page by using a JSON file {#proc-customizing-the-tech-radar-page-by-using-a-json-file_configuring-a-floating-action-button}

For ease of use and simplicity, you can configure the Tech Radar page by
using a hosted JSON file.

<div>

::: title
Prerequisites
:::

- You have specified the data sources for the Tech Radar plugin in the
  `integrations` section of the `app-config.yaml` file. For example, to
  configure GitHub as an integration, see [Authenticating with
  GitHub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/authentication_in_red_hat_developer_hub/index#authenticating-with-github).

- You have enabled the
  `./dynamic-plugins/dist/backstage-community-plugin-tech-radar` and
  `/dynamic-plugins/dist/backstage-community-plugin-tech-radar-backend-dynamic`
  plugins.

</div>

<div>

::: title
Procedure
:::

1.  Publish the JSON file containing your Tech Radar data to a web
    server, such as GitHub or Gitlab. You can find an example at
    <https://raw.githubusercontent.com/redhat-developer/rhdh/release-1.6/packages/app/public/tech-radar/data-default.json>.

2.  Configure Developer Hub to access the Tech Radar data from the
    hosted JSON files, by adding the following to the `app-config.yaml`
    file:

    ``` yaml
    techRadar:
      url: <tech_radar_data_url>
    ```

    `<tech_radar_data_url>`

    :   Enter the Tech Radar data hosted JSON URL.

</div>

### Customizing the Tech Radar page by using a customization service {#proc-customizing-rhdh-tech-radar-page-by-using-a-customization-service_configuring-a-floating-action-button}

For advanced scenarios, you can host your Red Hat Developer Hub
customization service to provide data to all configurable Developer Hub
pages, such as the Tech Radar page. You can even use a different service
for each page.

<div>

::: title
Prerequisites
:::

- You have specified the data sources for the Tech Radar plugin in the
  `integrations` section of the `app-config.yaml` file. For example, to
  configure GitHub as an integration, see [Authenticating with
  GitHub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/authentication_in_red_hat_developer_hub/index#authenticating-with-github).

- You have enabled the
  `./dynamic-plugins/dist/backstage-community-plugin-tech-radar` and
  `/dynamic-plugins/dist/backstage-community-plugin-tech-radar-backend-dynamic`
  plugins.

</div>

<div>

::: title
Procedure
:::

1.  Deploy your Developer Hub customization service on the same
    OpenShift Container Platform cluster as your Developer Hub instance.
    You can find an example at
    [`red-hat-developer-hub-customization-provider`](https://github.com/redhat-developer/red-hat-developer-hub-customization-provider),
    that provides the same data as default Developer Hub data. The
    customization service provides a Tech Radar data URL such as:
    `http://<rhdh-customization-provider>/tech-radar`.

2.  Add the dedicated service as an allowed host by adding the following
    code to the `app-config.yaml` file:

    ``` yaml
    backend:
       reading:
            allow:
              - host: '<rhdh_customization_provider_base_url>'
    ```

    `<rhdh_customization_provider_base_url>`

    :   Enter the base URL of your Tech Radar data URL, such as:
        `<rhdh-customization-provider>`.

3.  Add the following to the `app-config.yaml` file:

    ``` yaml
    techRadar:
        url: <tech_radar_data_url>
    ```

    `<tech_radar_data_url>`

    :   Enter your Tech Radar data URL, such as:
        `http://<rhdh-customization-provider>/tech-radar`.

</div>

## Customizing Red Hat Developer Hub appearance {#customizing-appearance}

The following default theme configurations are available for Red Hat
Developer Hub:

The Red Hat Developer Hub theme

:   Default theme configurations to make your developer portal look like
    a standard Red Hat Developer Hub instance. For more information, see
    [Default Red Hat Developer Hub
    theme](#ref-customize-rhdh-default-rhdh_customizing-appearance)

The Backstage theme

:   Default theme configurations to make your developer portal look like
    a standard Backstage instance. For more information, see [Default
    Backstage
    theme](#ref-customize-rhdh-default-backstage_customizing-appearance)

You can change or disable particular parameters in a default theme or
create a fully customized theme by modifying the `app-config-rhdh.yaml`
file. From the `app-config-rhdh.yaml` file, you can customize common
theme components, including the following:

- Company name and logo

- Font color, size, and style of text in paragraphs, headings, headers,
  and buttons

- Header color, gradient, and shape

- Button color

- Navigation indicator color

You can also customize some components from the Developer Hub GUI, such
as the theme mode (**Light Theme**, **Dark Theme**, or **Auto**).

### Customizing the theme mode for your Developer Hub instance {#proc-customizing-rhdh-theme-mode_customizing-appearance}

:::: note
::: title
:::

In Developer Hub, theme configurations are used to change the look and
feel of different UI components. So, you might notice changes in
different UI components, such as buttons, tabs, sidebars, cards, and
tables along with some changes in background color and font used on the
RHDH pages.
::::

You can choose one of the following theme modes for your Developer Hub
instance:

- Light theme

- Dark theme

- Auto

The default theme mode is Auto, which automatically sets the light or
dark theme based on your system preferences.

<div>

::: title
Prerequisites
:::

- You are logged in to the Developer Hub web console.

</div>

<div>

::: title
Procedure
:::

1.  From the Developer Hub web console, click **Settings**.

2.  From the **Appearance** panel, click **LIGHT THEME**, **DARK
    THEME**, or **AUTO** to change the theme mode.

    ![custom theme mode 1](images/user-guide/custom-theme-mode-1.png)

</div>

### Customizing the branding logo of your Developer Hub instance {#proc-customize-rhdh-branding-logo_customizing-appearance}

You can customize the branding logo of your Developer Hub instance by
configuring the `branding` section in the `app-config.yaml` file, as
shown in the following example:

``` yaml
app:
  branding:
    fullLogo: ${BASE64_EMBEDDED_FULL_LOGO}
    iconLogo: ${BASE64_EMBEDDED_ICON_LOGO}
```

where:

- `fullLogo` is the logo on the expanded (pinned) sidebar and expects a
  base64 encoded image.

- `iconLogo` is the logo on the collapsed (unpinned) sidebar and expects
  a base64 encoded image.

  You can format the `BASE64_EMBEDDED_FULL_LOGO` environment variable as
  follows:

  ``` yaml
  BASE64_EMBEDDED_FULL_LOGO: "data:_<media_type>_;base64,<base64_data>"
  ```

  The following example demonstrates how to customize the
  `BASE64_EMBEDDED_FULL_LOGO` using the
  `data:_<media_type>_;base64,<base64_data>` format:

  ``` yaml
  SVGLOGOBASE64=$(base64 -i logo.svg)
  BASE64_EMBEDDED_FULL_LOGO="data:image/svg+xml;base64,$SVGLOGOBASE64"
  ```

  Replace `image/svg+xml` with the correct media type for your image
  (for example, `image/png` and `image/jpeg`), and adjust the file
  extension accordingly. As a result, you can embed the logo directly
  without referencing an external file.

You can also customize the width of the branding logo by setting a value
for the `fullLogoWidth` field in the `branding` section, as shown in the
following example:

``` yaml
app:
  branding:
    fullLogoWidth: 110px
# ...
```

- The default value for the logo width is `110px`. The following units
  are supported: `integer`, `px`, `em`, `rem`, percentage.

### Customizing the sidebar menu items for your Developer Hub instance {#con-customize-rhdh-sidebar-menuitems_customizing-appearance}

The sidebar menu in Red Hat Developer Hub consists of two main parts
that you can configure:

Dynamic plugin menu items

:   Your preferences and your active plugins define dynamically one part
    of the sidebar menu.

Main menu items

:   The core navigation structure of sidebar is static.

    - **Dynamic plugin menu items**: These items are displayed beneath
      the main menu and can be customized based on the plugins
      installed. The main menu items section is dynamic and can change
      based on your preferences and installed plugins.

#### Customizing the sidebar menu items for your Developer Hub instance {#proc-customize-rhdh-sidebar-menuitems_customizing-appearance}

Customize the main menu items using the following steps:

<div>

::: title
Procedure
:::

1.  Open the `app-config.yaml` file.

    a.  To customize the order and parent-child relationships for the
        main menu items, use the
        `dynamicPlugins.frontend.default.main-menu-items.menuItems`
        field.

    b.  For dynamic plugin menu items, use the
        `dynamicPlugins.frontend.<package_name>.menuItems` field.

</div>

:::: formalpara
::: title
Example `app-config.yaml` file
:::

``` yaml
dynamicPlugins:
  frontend:
    default.main-menu-items:
        menuItems:
          default.home:
            title: Home
            icon: home
            priority: 100
          default.my-group:
            title: My Group
            icon: group
            priority: 90
          default.catalog:
            title: Catalog
            icon: category
            to: catalog
            priority: 80
          default.apis:
            title: APIs
            icon: extension
            to: api-docs
            priority: 70
          default.learning-path:
            title: Learning Paths
            icon: school,
            to: learning-paths
            priority: 60
          default.create:
            title: Self-service
            icon: add
            to: create
            priority: 50
```
::::

#### Configuring a dynamic plugin menu item for your Developer Hub instance {#proc-configuring-dynamic-plugin-menuitem_customizing-appearance}

Configure a dynamic plugin menu item using the following step:

<div>

::: title
Procedure
:::

- In the `app-config.yaml` file, update the `menuItems` section of your
  *\<plugin_name\>* plugin. For example:

  ``` yaml
  dynamicPlugins:
    frontend:
      _<plugin_name>_:
        menuItems:
          <menu_item_name>:
            icon: # home | group | category | extension | school | _<my_icon>_
            title: _<plugin_page_title>_
            priority: 10
            parent: favorites
  ```

  - `<plugin_name>`: Enter the plugin name. This name is the same as the
    `scalprum.name` key in the `package.json` file.

  - `<menu_item_name>`: Enter a unique name in the main sidebar
    navigation for either a standalone menu item or a parent menu item.
    If this field specifies a plugin menu item, the name of the menu
    item must match the name using in the corresponding path in
    `dynamicRoutes`. For example, if `dynamicRoutes` defines
    `path: /my-plugin`, then `menu_item_name` must be defined as
    `my-plugin`.

  - `icon`: (Optional) Enter the icon name. You can use any of the
    following icons:

    - Default icons, such as `home`, `group`, `category`, `extension`,
      and `school`. To use default icons, set the icon as an (`" "`)
      empty string.

    - A custom icon, where *\<my_icon\>* specifies the name of your
      custom icon

    - An SVG icon, such as:
      `icon: <svg width="20px" height="20px" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" fill="#ffffff">…​</svg>`

    - An HTML image, such as:
      `icon: https://img.icons8.com/ios-glyphs/20/FFFFFF/shop.png`

  - `title`: (Optional) Enter the menu item title. Omit it when the
    title is already specified in the `dynamicRoutes` configuration
    under `menuItem.text`. To hide the title from the sidebar, set the
    title as an (`" "`) empty string.

  - `priority`: (Optional) Sets the order in which menu items appear in
    the sidebar. The default priority is 0, which places the item at the
    bottom of the list. A higher priority value places the item higher
    in the sidebar. You can define this field for each section.

  - `parent`: (Optional) Enter the parent menu item under which the
    current item is nested. If this field is used, the parent menu item
    must be defined elsewhere in the `menuItems` configuration of any
    enabled plugin. You can define this field for each section.

  :::: formalpara
  ::: title
  Example `menuItems` configuration
  :::

  ``` yaml
  dynamicPlugins:
    frontend:
      _<package_name>_:
        dynamicRoutes:
          - path: /my-plugin
            module: CustomModule
            importName: FooPluginPage
            menuItem:
              icon: fooIcon
              text: Foo Plugin Page
        menuItems:
          my-plugin:
            priority: 10
            parent: favorites
          favorites:
            icon: favorite
            title: Favorites
            priority: 100
  ```
  ::::

  - `my-plugin`: Matches the value of the `path` field in
    `dynamicRoutes`.

  - `priority`: Controls order of plugins under the parent menu item.

  - `parent`: Nests this plugin under the `favorites` parent menu item.

  - `favorites`: Configuration for the parent menu item.

  - `icon`: Displays the `favorite` icon from the RHDH system icons.

  - `title`: Displays the title name for the parent menu item.

  - `priority`: Order of the `favourites` menu item in the sidebar.

</div>

#### Modifying or adding a custom menu items for your Developer Hub instance {#proc-modifying-or-adding-rhdh-custom-menuitem_customizing-appearance}

Modify a main menu item or add a custom menu item using the following
step:

<div>

::: title
Procedure
:::

- In the `app-config.yaml` file, add a section to the
  `default.main-menu-items` \> `menuItems` section. Use the `default.`
  prefix to identify the key as a main menu item.

  ``` yaml
  dynamicPlugins:
    frontend:
      default.main-menu-items:
        menuItems:
          default._<menu_group_parent_item_name>_:
            icon: # home | group | category | extension | school | _<my_icon>_
            title: _<menu_group_parent_title>_
            priority: 10
          default._<menu_item_name>_:
            parent: _<menu_group_parent_item_name>_
            icon:  # home | group | category | extension | school | _<my_icon>_
            title: _<my_menu_title>_
            to: _<path_to_the_menu_target_page>_
            priority: 100
  ```

  - `default.<menu_group_parent_item_name>`: (Optional) Enter the menu
    group parent item name to configure static main menu items. If no
    `default.<menu_item_name>` has a `parent` value set, this field is
    not needed.

  - `icon`: Enter the menu icon. Required for parent menu items.

  - `title`: Enter the menu group title. Required for parent menu items.

  - `priority`: (Optional) Enter the order of this menu item within its
    menu level.

  - `default.<menu_item_name>`: Enter the menu item name for which you
    want to override the default value. Add the `default.` prefix to
    identify a main menu item.

  - `parent`: (Optional) Enter the parent menu item for this item.
    Required if \<menu_item_name\> is specified as the child of any menu
    items.

  - `icon`: (Optional) Enter the menu icon. To use the default icon, set
    the icon as an (`" "`) empty string.

  - `title`: (Optional) Enter the menu group title. Only required for
    adding a new custom main menu item. To hide a default main menu item
    title from the sidebar, set the title as an (`" "`) empty string.

  - `to`: (Optional) Enter the path that the menu item navigates to. If
    it is not set, it defaults to the home page.

  - `priority`: (Optional) Enter the order of this menu item within its
    menu level.

  :::: formalpara
  ::: title
  Example `mainItems` configuration
  :::

  ``` yaml
  default.main-menu-items:
        menuItems:
          default.catalog:
            icon: category
            title: My Catalog
            priority: 5
          default.learning-path:
            title: ''
          default.parentlist:
            title: Overview
            icon: bookmarks
          default.home:
            parent: default.parentlist
          default.references:
            title: References
            icon: school
            to: /references
  ```
  ::::

  - `icon`: Specifies if you want to change the icon default menu item
    for the catalog.

  - `title`: Specifies an empty string `" "` to hide the learning path
    from the default sidebar.

  - `default.parentlist`: Introduces the parent menu item.

  - `parent`: Nests home menu under the `default.parentlist` parent menu
    item.

  - `title`: Specifies a name for `default.references`

  - `icon`: Displays the `school` icon.

  - `to`: Redirects `default.references` to the `/references` page.

</div>

### Configuring entity tab titles {#configuring-entity-tab-titles_customizing-appearance}

Red Hat Developer Hub provides a default opinionated tab set for catalog
entity views. For consistency with your organization needs, you can
rename, reorder, remove, and add tab titles.

<div>

::: title
Procedure
:::

- For each tab to modify, enter your desired values in the `entityTabs`
  section in your `app-config.yaml` file:

  ``` yaml
  upstream:
    backstage:
      appConfig:
        dynamicPlugins:
          frontend:
           <plugin_name>:
              entityTabs:
                - mountPoint: <mount_point>
                  path: <path>
                  title: <title>
                  priority: <priority>
  ```

  `<plugin_name>`

  :   Enter the plugin name, such as
      `backstage-community.plugin-topology`.

  `mountPoint`

  :   Enter the tab mountpoint, such as `entity.page.topology`.

  `path`

  :   Enter the tab path, such as `/topology`.

  `title`

  :   Enter the tab title, such as `Topology`.

  `priority`

  :   Optional.

      To reorder tabs, enter the tab priority, such as `42`. Higher
      priority appears first.

      To remove a tab, enter a negative value, such as `-1`.

</div>

### Configuring entity detail tab layout {#configuring-entity-detail-tab-layout_customizing-appearance}

Each Red Hat Developer Hub entity detail tab has a default opinionated
layout. For consistency with your organization needs, you can change the
entity detail tab content when the plugin that contributes the tab
content allows a configuration.

<div>

::: title
Prerequisites
:::

- The plugin that contributes the tab content allows a configuration,
  such as [Developer Hub plugins defining a default configuration in a
  `config`
  section](https://github.com/redhat-developer/rhdh/blob/release-1.6/dynamic-plugins.default.yaml).

</div>

<div>

::: title
Procedure
:::

- Copy the plugin default configuration in your `app-config.yaml` file,
  and change the `layout` properties.

  ``` yaml
  global:
    dynamic:
      plugins:
        - package: <package_location>
          disabled: false
          pluginConfig:
            dynamicPlugins:
              frontend:
                <plugin_name>:
                  mountPoints:
                    - mountPoint: <mount_point>
                      importName: <import_name>
                      config:
                        layout:
                          gridColumn:
                            lg: span 6
                            xs: span 12
  ```

  `package`

  :   Enter your package location, such as
      `./dynamic-plugins/dist/backstage-community-plugin-tekton`.

  `<plugin_name>`

  :   Enter your plugin name, such as:
      `backstage-community.plugin-tekton`.

  `mountPoint`

  :   Copy the mount point defined in the plugin default configuration,
      such as: `entity.page.ci/cards`.

  `importName`

  :   Copy the import name defined in the plugin default configuration,
      such as: `TektonCI`.

  `layout`

  :   Enter your layout configuration. The tab content is displayed in a
      responsive grid that uses a 12 column-grid and supports different
      breakpoints (`xs`, `sm`, `md`, `lg`, `xl`) that can be specified
      for a CSS property, such as `gridColumn`. The example uses 6 of
      the 12 columns to show two Tekton CI cards side-by-side on large
      (`lg`) screens (`span 6` columns) and show them among themselves
      (`xs` and above `span 12` columns).

</div>

### Customizing the theme mode color palettes for your Developer Hub instance {#proc-customize-rhdh-branding_customizing-appearance}

You can customize the color palettes of the light and dark theme modes
in your Developer Hub instance by configuring the `light.palette` and
`dark.palette` parameters in the `branding.theme` section of the
`app-config.yaml` file, as shown in the following example:

``` yaml
app:
  branding:
    theme:
      light:
        palette:
          primary:
            main: <light_primary_color>
          navigation:
            indicator: <light_indicator_color>
        pageTheme:
          default:
            backgroundColor: [<light_background_color_1>, <light_background_color_2>]
      dark:
        palette:
          primary:
            main: <dark_primary_color>
          navigation:
            indicator: <dark_indicator_color>
        pageTheme:
          default:
            backgroundColor: [<dark_background_color_1>, <dark_background_color_2>]
# ...
```

- The main primary color for the light color palette, for example,
  `#ffffff` or `white`

- The color of the navigation indicator for the light color palette,
  which is a vertical bar that indicates the selected tab in the
  navigation panel, for example, `#FF0000` or `red`

- The background color for the default page theme for the light color
  palette, for example, `#ffffff` or `white`

- The main primary color for the dark color palette, for example,
  `#000000` or `black`

- The color of the navigation indicator for the dark color palette,
  which is a vertical bar that indicates the selected tab in the
  navigation panel, for example, `#FF0000` or `red`

- The background color for the default page theme for the dark color
  palette, for example, `#000000` or `black`

<div>

::: title
Additional resources
:::

- [Customizing the theme mode for your Developer Hub
  instance](#proc-customizing-rhdh-theme-mode_customizing-appearance)

</div>

### Customizing the page theme header for your Developer Hub instance {#proc-customize-rhdh-page-theme_customizing-appearance}

You can customize the header color for the light and dark theme modes in
your Developer Hub instance by modifying the `branding.theme` section of
the `app-config.yaml` file. You can also customize the page headers for
additional Developer Hub pages, such as the **Home**, **Catalog**, and
**APIs** pages.

``` yaml
app:
  branding:
    theme:
      light:
        palette: {}
        pageTheme:
          default:
            backgroundColor: "<default_light_background_color>"
            fontColor: "<default_light_font_color>"
            shape: none
          apis:
            backgroundColor: "<apis_light_background_color>"
            fontColor: "<apis_light_font_color>"
            shape: none
      dark:
        palette: {}
        pageTheme:
          default:
            backgroundColor: "<default_dark_background_color>"
            fontColor: "<default_dark_font_color>"
            shape: none
# ...
```

- The theme mode, for example, `light` or `dark`

- The `yaml` header for the default page theme configuration

- The color of the page header background, for example, `#ffffff` or
  `white`

- The color of the text in the page header, for example, `#000000` or
  `black`

- The pattern on the page header, for example, `wave`, `round`, or
  `none`

- The `yaml` header for a specific page theme configuration, for
  example, `apis`, `home`

### Customizing the font for your Developer Hub instance {#proc-customize-rhdh-font_customizing-appearance}

You can configure the `typography` section of the `app-config.yaml` file
to change the default font family and size of the page text, as well as
the font family and size of each heading level, as shown in the
following example:

``` yaml
app:
  branding:
    theme:
      light:
        typography:
          fontFamily: "Times New Roman"
          htmlFontSize: 11 # smaller is bigger
          h1:
            fontFamily: "Times New Roman"
            fontSize: 40
          h2:
            fontFamily: "Times New Roman"
            fontSize: 30
          h3:
            fontFamily: "Times New Roman"
            fontSize: 30
          h4:
            fontFamily: "Times New Roman"
            fontSize: 30
          h5:
            fontFamily: "Times New Roman"
            fontSize: 30
          h6:
            fontFamily: "Times New Roman"
            fontSize: 30
      dark:
        typography:
          fontFamily: "Times New Roman"
          htmlFontSize: 11 # smaller is bigger
          h1:
            fontFamily: "Times New Roman"
            fontSize: 40
          h2:
            fontFamily: "Times New Roman"
            fontSize: 30
          h3:
            fontFamily: "Times New Roman"
            fontSize: 30
          h4:
            fontFamily: "Times New Roman"
            fontSize: 30
          h5:
            fontFamily: "Times New Roman"
            fontSize: 30
          h6:
            fontFamily: "Times New Roman"
            fontSize: 30
# ...
```

### Default Red Hat Developer Hub theme {#ref-customize-rhdh-default-rhdh_customizing-appearance}

You can use the default Red Hat Developer Hub theme configurations to
make your Developer Hub instance look like a standard Red Hat Developer
Hub instance. You can also modify the `app-config.yaml` file to
customize or disable particular parameters.

#### Default Red Hat Developer Hub theme color palette {#_default-red-hat-developer-hub-theme-color-palette}

The `app-config.yaml` file uses the following configurations for the
default Red Hat Developer Hub color palette:

``` yaml
app:
  branding:
    theme:
      light:
        variant: "rhdh"
        mode: "light"
        palette:
          background:
            default: "#F8F8F8"
            paper: "#FFFFFF"
          banner:
            closeButtonColor: "#FFFFFF"
            error: "#E22134"
            info: "#2E77D0"
            link: "#000000"
            text: "#FFFFFF"
            warning: "#FF9800"
          border: "#E6E6E6"
          bursts:
            backgroundColor:
              default: "#7C3699"
            fontColor: "#FEFEFE"
            gradient:
              linear: "linear-gradient(-137deg, #4BB8A5 0%, #187656 100%)"
            slackChannelText: "#ddd"
          errorBackground: "#FFEBEE"
          errorText: "#CA001B"
          gold: "#FFD600"
          highlight: "#FFFBCC"
          infoBackground: "#ebf5ff"
          infoText: "#004e8a"
          link: "#0A6EBE"
          linkHover: "#2196F3"
          mode: "light"
          navigation:
            background: "#222427"
            indicator: "#0066CC"
            color: "#ffffff"
            selectedColor: "#ffffff"
            navItem:
              hoverBackground: "#3c3f42"
            submenu:
              background: "#222427"
          pinSidebarButton:
            background: "#BDBDBD"
            icon: "#181818"
          primary:
            main: "#0066CC"
          secondary:
            main: "#8476D1"
          status:
            aborted: "#757575"
            error: "#E22134"
            ok: "#1DB954"
            pending: "#FFED51"
            running: "#1F5493"
            warning: "#FF9800"
          tabbar:
            indicator: "#9BF0E1"
          textContrast: "#000000"
          textSubtle: "#6E6E6E"
          textVerySubtle: "#DDD"
          warningBackground: "#F59B23"
          warningText: "#000000"
          text:
            primary: "#151515"
            secondary: "#757575"
          rhdh:
            general:
              disabledBackground: "#D2D2D2"
              disabled: "#6A6E73"
              searchBarBorderColor: "#E4E4E4"
              formControlBackgroundColor: "#FFF"
              mainSectionBackgroundColor: "#FFF"
              headerBottomBorderColor: "#C7C7C7"
              cardBackgroundColor: "#FFF"
              sidebarBackgroundColor: "#212427"
              cardBorderColor: "#C7C7C7"
              tableTitleColor: "#181818"
              tableSubtitleColor: "#616161"
              tableColumnTitleColor: "#151515"
              tableRowHover: "#F5F5F5"
              tableBorderColor: "#E0E0E0"
              tableBackgroundColor: "#FFF"
              tabsBottomBorderColor: "#D2D2D2"
              contrastText: "#FFF"
            primary:
              main: "#0066CC"
              focusVisibleBorder: "#0066CC"
            secondary:
              main: "#8476D1"
              focusVisibleBorder: "#8476D1"
            cards:
              headerTextColor: "#151515"
              headerBackgroundColor: "#FFF"
              headerBackgroundImage: "none"

      dark:
        variant: "rhdh"
        mode: "dark"
        palette:
          background:
            default: "#333333"
            paper: "#424242"
          banner:
            closeButtonColor: "#FFFFFF"
            error: "#E22134"
            info: "#2E77D0"
            link: "#000000"
            text: "#FFFFFF"
            warning: "#FF9800"
          border: "#E6E6E6"
          bursts:
            backgroundColor:
              default: "#7C3699"
            fontColor: "#FEFEFE"
            gradient:
              linear: "linear-gradient(-137deg, #4BB8A5 0%, #187656 100%)"
            slackChannelText: "#ddd"
          errorBackground: "#FFEBEE"
          errorText: "#CA001B"
          gold: "#FFD600"
          highlight: "#FFFBCC"
          infoBackground: "#ebf5ff"
          infoText: "#004e8a"
          link: "#9CC9FF"
          linkHover: "#82BAFD"
          mode: "dark"
          navigation:
            background: "#0f1214"
            indicator: "#0066CC"
            color: "#ffffff"
            selectedColor: "#ffffff"
            navItem:
              hoverBackground: "#3c3f42"
            submenu:
              background: "#0f1214"
          pinSidebarButton:
            background: "#BDBDBD"
            icon: "#404040"
          primary:
            main: "#1FA7F8"
          secondary:
            main: "#B2A3FF"
          status:
            aborted: "#9E9E9E"
            error: "#F84C55"
            ok: "#71CF88"
            pending: "#FEF071"
            running: "#3488E3"
            warning: "#FFB84D"
          tabbar:
            indicator: "#9BF0E1"
          textContrast: "#FFFFFF"
          textSubtle: "#CCCCCC"
          textVerySubtle: "#727272"
          warningBackground: "#F59B23"
          warningText: "#000000"

          rhdh:
            general:
              disabledBackground: "#444548"
              disabled: "#AAABAC"
              searchBarBorderColor: "#57585a"
              formControlBackgroundColor: "#36373A"
              mainSectionBackgroundColor: "#0f1214"
              headerBottomBorderColor: "#A3A3A3"
              cardBackgroundColor: "#292929"
              sidebarBackgroundColor: "#1b1d21"
              cardBorderColor: "#A3A3A3"
              tableTitleColor: "#E0E0E0"
              tableSubtitleColor: "#E0E0E0"
              tableColumnTitleColor: "#E0E0E0"
              tableRowHover: "#0f1214"
              tableBorderColor: "#515151"
              tableBackgroundColor: "#1b1d21"
              tabsBottomBorderColor: "#444548"
              contrastText: "#FFF"
            primary:
              main: "#1FA7F8"
              focusVisibleBorder: "#ADD6FF"
            secondary:
              main: "#B2A3FF"
              focusVisibleBorder: "#D0C7FF"
            cards:
              headerTextColor: "#FFF"
              headerBackgroundColor: "#0f1214"
              headerBackgroundImage: "none"
```

Alternatively, you can use the following `variant` and `mode` values in
the `app-config.yaml` file to apply the previous default configuration:

``` yaml
app:
  branding:
    theme:
      light:
        variant: "rhdh"
        mode: "light"
      dark:
        variant: "rhdh"
        mode: "dark"
```

#### Default Red Hat Developer Hub page themes {#_default-red-hat-developer-hub-page-themes}

The default Developer Hub header color is white in light mode and black
in dark mode, as shown in the following `app-config.yaml` file
configuration:

``` yaml
app:
  branding:
    theme:
      light:
        palette: {}
        defaultPageTheme: default
        pageTheme:
          default:
            backgroundColor: "#ffffff"
      dark:
        palette: {}
        defaultPageTheme: default
        pageTheme:
          default:
            backgroundColor: "#0f1214"
```

### Default Backstage theme {#ref-customize-rhdh-default-backstage_customizing-appearance}

You can use the default Backstage theme configurations to make your
Developer Hub instance look like a standard Backstage instance. You can
also modify the `app-config.yaml` file to customize or disable
particular parameters.

#### Default Backstage theme color palette {#_default-backstage-theme-color-palette}

The `app-config.yaml` file uses the following configurations for the
default Backstage color palette:

``` yaml
app:
  branding:
    theme:
      light:
        variant: "backstage"
        mode: "light"
        palette:
          background:
            default: "#F8F8F8"
            paper: "#FFFFFF"
          banner:
            closeButtonColor: "#FFFFFF"
            error: "#E22134"
            info: "#2E77D0"
            link: "#000000"
            text: "#FFFFFF"
            warning: "#FF9800"
          border: "#E6E6E6"
          bursts:
            backgroundColor:
              default: "#7C3699"
            fontColor: "#FEFEFE"
            gradient:
              linear: "linear-gradient(-137deg, #4BB8A5 0%, #187656 100%)"
            slackChannelText: "#ddd"
          errorBackground: "#FFEBEE"
          errorText: "#CA001B"
          gold: "#FFD600"
          highlight: "#FFFBCC"
          infoBackground: "#ebf5ff"
          infoText: "#004e8a"
          link: "#0A6EBE"
          linkHover: "#2196F3"
          navigation:
            background: "#171717"
            color: "#b5b5b5"
            indicator: "#9BF0E1"
            navItem:
              hoverBackground: "#404040"
            selectedColor: "#FFF"
            submenu:
              background: "#404040"
          pinSidebarButton:
            background: "#BDBDBD"
            icon: "#181818"
          primary:
            main: "#1F5493"
          status:
            aborted: "#757575"
            error: "#E22134"
            ok: "#1DB954"
            pending: "#FFED51"
            running: "#1F5493"
            warning: "#FF9800"
          tabbar:
            indicator: "#9BF0E1"
          textContrast: "#000000"
          textSubtle: "#6E6E6E"
          textVerySubtle: "#DDD"
          warningBackground: "#F59B23"
          warningText: "#000000"

      dark:
        variant: "backstage"
        mode: "dark"
        palette:
          background:
            default: "#333333"
            paper: "#424242"
          banner:
            closeButtonColor: "#FFFFFF"
            error: "#E22134"
            info: "#2E77D0"
            link: "#000000"
            text: "#FFFFFF"
            warning: "#FF9800"
          border: "#E6E6E6"
          bursts:
            backgroundColor:
              default: "#7C3699"
            fontColor: "#FEFEFE"
            gradient:
              linear: "linear-gradient(-137deg, #4BB8A5 0%, #187656 100%)"
            slackChannelText: "#ddd"
          errorBackground: "#FFEBEE"
          errorText: "#CA001B"
          gold: "#FFD600"
          highlight: "#FFFBCC"
          infoBackground: "#ebf5ff"
          infoText: "#004e8a"
          link: "#9CC9FF"
          linkHover: "#82BAFD"
          mode: "dark"
          navigation:
            background: "#424242"
            color: "#b5b5b5"
            indicator: "#9BF0E1"
            navItem:
              hoverBackground: "#404040"
            selectedColor: "#FFF"
            submenu:
              background: "#404040"
          pinSidebarButton:
            background: "#BDBDBD"
            icon: "#404040"
          primary:
            dark: "#82BAFD"
            main: "#9CC9FF"
          secondary:
            main: "#FF88B2"
          status:
            aborted: "#9E9E9E"
            error: "#F84C55"
            ok: "#71CF88"
            pending: "#FEF071"
            running: "#3488E3"
            warning: "#FFB84D"
          tabbar:
            indicator: "#9BF0E1"
          textContrast: "#FFFFFF"
          textSubtle: "#CCCCCC"
          textVerySubtle: "#727272"
          warningBackground: "#F59B23"
          warningText: "#000000"
```

Alternatively, you can use the following `variant` and `mode` values in
the `app-config.yaml` file to apply the previous default configuration:

``` yaml
app:
  branding:
    theme:
      light:
        variant: "backstage"
        mode: "light"
      dark:
        variant: "backstage"
        mode: "dark"
```

#### Default Backstage page themes {#_default-backstage-page-themes}

The default Backstage header color is white in light mode and black in
dark mode, as shown in the following `app-config.yaml` file
configuration:

``` yaml
app:
  branding:
    theme:
      light:
        palette: {}
        defaultPageTheme: default
        pageTheme:
          default:
            backgroundColor: ['#005B4B'] # teal
            fontColor: '#ffffff'
            shape: wave
          documentation:
            backgroundColor: ['#C8077A', '#C2297D'] # pinkSea
            fontColor: '#ffffff'
            shape: wave2
          tool:
            backgroundColor: ['#8912CA', '#3E00EA'] # purpleSky
            fontColor: '#ffffff'
            shape: round
          service:
            backgroundColor: ['#006D8F', '#0049A1'] # marineBlue
            fontColor: '#ffffff'
            shape: wave
          website:
            backgroundColor: ['#0027AF', '#270094'] # veryBlue
            fontColor: '#ffffff'
            shape: wave
          library:
            backgroundColor: ['#98002B', '#8D1134'] # rubyRed
            fontColor: '#ffffff'
            shape: wave
          other:
            backgroundColor: ['#171717', '#383838'] # darkGrey
            fontColor: '#ffffff'
            shape: wave
          app:
            backgroundColor: ['#BE2200', '#A41D00'] # toastyOrange
            fontColor: '#ffffff'
            shape: shapes.wave
          apis:
            backgroundColor: ['#005B4B'] # teal
            fontColor: '#ffffff'
            shape: wave2
          card:
            backgroundColor: ['#4BB8A5', '#187656'] # greens
            fontColor: '#ffffff'
            shape: wave

      dark:
        palette: {}
        defaultPageTheme: default
        pageTheme:
          default:
            backgroundColor: ['#005B4B'] # teal
            fontColor: '#ffffff'
            shape: wave
          documentation:
            backgroundColor: ['#C8077A', '#C2297D'] # pinkSea
            fontColor: '#ffffff'
            shape: wave2
          tool:
            backgroundColor: ['#8912CA', '#3E00EA'] # purpleSky
            fontColor: '#ffffff'
            shape: round
          service:
            backgroundColor: ['#006D8F', '#0049A1'] # marineBlue
            fontColor: '#ffffff'
            shape: wave
          website:
            backgroundColor: ['#0027AF', '#270094'] # veryBlue
            fontColor: '#ffffff'
            shape: wave
          library:
            backgroundColor: ['#98002B', '#8D1134'] # rubyRed
            fontColor: '#ffffff'
            shape: wave
          other:
            backgroundColor: ['#171717', '#383838'] # darkGrey
            fontColor: '#ffffff'
            shape: wave
          app:
            backgroundColor: ['#BE2200', '#A41D00'] # toastyOrange
            fontColor: '#ffffff'
            shape: shapes.wave
          apis:
            backgroundColor: ['#005B4B'] # teal
            fontColor: '#ffffff'
            shape: wave2
          card:
            backgroundColor: ['#4BB8A5', '#187656'] # greens
            fontColor: '#ffffff'
            shape: wave
```

### Loading a custom Developer Hub theme by using a dynamic plugin {#proc-loading-custom-theme-using-dynamic-plugin-_customizing-appearance}

You can load a custom Developer Hub theme from a dynamic plugin.

<div>

::: title
Procedure
:::

1.  Export a theme provider function in your dynamic plugin, for
    example:

    :::: formalpara
    ::: title
    Sample `myTheme.ts` fragment
    :::

    ``` javascript
    import { lightTheme } from './lightTheme'; // some custom theme
    import { UnifiedThemeProvider } from '@backstage/theme';
    export const lightThemeProvider = ({ children }: { children: ReactNode }) => (
      <UnifiedThemeProvider theme={lightTheme} children={children} />
    );
    ```
    ::::

    For more information about creating a custom theme, see [Backstage
    documentation - Creating a Custom
    Theme](https://backstage.io/docs/getting-started/app-custom-theme/#creating-a-custom-theme).

2.  Configure Developer Hub to load the theme in the UI by using the
    `themes` configuration field:

    :::: formalpara
    ::: title
    `app-config.yaml` fragment
    :::

    ``` yaml
    dynamicPlugins:
      frontend:
        example.my-custom-theme-plugin:
          themes:
            - id: light
              title: Light
              variant: light
              icon: someIconReference
              importName: lightThemeProvider
    ```
    ::::

    - Set your theme ID by specifying the desired value. Optionally,
      override the default Developer Hub themes by using the following
      ID values: `light` to replace the default light theme, or `dark`
      to replace the default dark theme.

</div>

<div>

::: title
Verification
:::

- The theme is available in the Developer Hub **Settings** page.

</div>

### Custom component options for your Developer Hub instance {#ref-customize-rhdh-custom-components_customizing-appearance}

There are two component variants that you can use to customize various
components of your Developer Hub theme:

- **Patternfly**

- **MUI**

In addition to assigning a component variant to each parameter in the
light or dark theme mode configurations, you can toggle the
`rippleEffect` `on` or `off`.

The following code shows the options that you can use in the
[`app-config.yaml`
file](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index)
to configure the theme components for your Developer Hub instance:

``` yaml
app:
  branding:
    theme:
      light:
        options:
          rippleEffect: off / on
          paper: patternfly / mui
          buttons: patternfly / mui
          inputs: patternfly / mui
          accordions: patternfly / mui
          sidebars: patternfly / mui
          pages: patternfly / mui
          headers: patternfly / mui
          toolbars: patternfly / mui
          dialogs: patternfly / mui
          cards: patternfly / mui
          tables: patternfly / mui
          tabs: patternfly / mui
      dark:
        options:
          rippleEffect: off / on
          paper: patternfly / mui
          buttons: patternfly / mui
          inputs: patternfly / mui
          accordions: patternfly / mui
          sidebars: patternfly / mui
          pages: patternfly / mui
          headers: patternfly / mui
          toolbars: patternfly / mui
          dialogs: patternfly / mui
          cards: patternfly / mui
          tables: patternfly / mui
          tabs: patternfly / mui
```

## Customizing the Home page

When using the `app-config`, you can do the following:

- Customize and extend the default Home page layout with additional
  cards that appear based on the plugins you have installed and enabled.

- Change quick access links.

- Add, reorganize, and remove the following available cards:

  - Search bar

  - Quick access

  - Headline

  - Markdown

  - Placeholder

  - Catalog starred entities

  - Featured docs

### Customizing the Home page cards {#customizing-the-home-page-cards_customizing-the-home-page}

Administrators can change the fixed height of cards that are in a
12-column grid.

The default Home page is as shown in the following `app-config.yaml`
file configuration:

``` yaml
dynamicPlugins:
  frontend:
    red-hat-developer-hub.backstage-plugin-dynamic-home-page:
      dynamicRoutes:
        - path: /
          importName: DynamicHomePage
      mountPoints:
        - mountPoint: home.page/cards
          importName: SearchBar
          config:
            layouts:
              xl: { w: 10, h: 1, x: 1 }
              lg: { w: 10, h: 1, x: 1 }
              md: { w: 10, h: 1, x: 1 }
              sm: { w: 10, h: 1, x: 1 }
              xs: { w: 12, h: 1 }
              xxs: { w: 12, h: 1 }
        - mountPoint: home.page/cards
          importName: QuickAccessCard
          config:
            layouts:
              xl: { w: 7, h: 8 }
              lg: { w: 7, h: 8 }
              md: { w: 7, h: 8 }
              sm: { w: 12, h: 8 }
              xs: { w: 12, h: 8 }
              xxs: { w: 12, h: 8 }
        - mountPoint: home.page/cards
          importName: CatalogStarredEntitiesCard
          config:
            layouts:
              xl: { w: 5, h: 4, x: 7 }
              lg: { w: 5, h: 4, x: 7 }
              md: { w: 5, h: 4, x: 7 }
              sm: { w: 12, h: 4 }
              xs: { w: 12, h: 4 }
              xxs: { w: 12, h: 4 }
```

<div>

::: title
Prerequisites
:::

- You have administrative access and can modify the `app-config.yaml`
  file for dynamic plugin configurations.

</div>

<div>

::: title
Procedure
:::

- Configure different cards for your Home page in Red Hat Developer Hub
  as follows:

  Search

  :   ``` yaml
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-dynamic-home-page:
            mountPoints:
              - mountPoint: home.page/cards
                importName: SearchBar
                config:
                  layouts:
                    xl: { w: 10, h: 1, x: 1 }
                    lg: { w: 10, h: 1, x: 1 }
                    md: { w: 10, h: 1, x: 1 }
                    sm: { w: 10, h: 1, x: 1 }
                    xs: { w: 12, h: 1 }
                    xxs: { w: 12, h: 1 }
      ```

      +----------------------+----------------------+-----------------------+
      | Prop                 | Default              | Description           |
      +======================+======================+=======================+
      | `path`               | `/search`            | Override the linked   |
      |                      |                      | search path if needed |
      +----------------------+----------------------+-----------------------+
      | `queryParam`         | `query`              | Override the search   |
      |                      |                      | query parameter name  |
      |                      |                      | if needed             |
      +----------------------+----------------------+-----------------------+

      : Available props

  Quick access

  :   ``` yaml
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-dynamic-home-page:
            mountPoints:
              - mountPoint: home.page/cards
                importName: QuickAccessCard
                config:
                  layouts:
                    xl: { h: 8 }
                    lg: { h: 8 }
                    md: { h: 8 }
                    sm: { h: 8 }
                    xs: { h: 8 }
                    xxs: { h: 8 }
      ```

      +----------------------+----------------------+-----------------------+
      | Prop                 | Default              | Description           |
      +======================+======================+=======================+
      | `title`              | `Quick Access`       | Override the linked   |
      |                      |                      | search path if needed |
      +----------------------+----------------------+-----------------------+
      | `path`               | none                 | Override the search   |
      |                      |                      | query parameter name  |
      |                      |                      | if needed             |
      +----------------------+----------------------+-----------------------+

      : Available props

  Headline

  :   ``` yaml
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-dynamic-home-page:
            mountPoints:
              - mountPoint: home.page/cards
                importName: Headline
                config:
                  layouts:
                    xl: { h: 1 }
                    lg: { h: 1 }
                    md: { h: 1 }
                    sm: { h: 1 }
                    xs: { h: 1 }
                    xxs: { h: 1 }
                  props:
                    title: Important info
      ```

      +----------------------+----------------------+-----------------------+
      | Prop                 | Default              | Description           |
      +======================+======================+=======================+
      | `title`              | none                 | Title                 |
      +----------------------+----------------------+-----------------------+

      : Available props

  Markdown

  :   ``` yaml
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-dynamic-home-page:
            mountPoints:
              - mountPoint: home.page/cards
                importName: MarkdownCard
                config:
                  layouts:
                    xl: { w: 6, h: 4 }
                    lg: { w: 6, h: 4 }
                    md: { w: 6, h: 4 }
                    sm: { w: 6, h: 4 }
                    xs: { w: 6, h: 4 }
                    xxs: { w: 6, h: 4 }
                  props:
                    title: Company links
                    content: |
                      ### RHDH
                      * [Website](https://developers.redhat.com/rhdh/overview)
                      * [Documentation](https://docs.redhat.com/en/documentation/red_hat_developer_hub/)
                      * [Janus Plugins](https://github.com/janus-idp/backstage-plugins)
                      * [Backstage Community Plugins](https://github.com/backstage/community-plugins)
                      * [RHDH Plugins](https://github.com/redhat-developer/rhdh-plugins)
                      * [RHDH Showcase](https://github.com/redhat-developer/rhdh)
              - mountPoint: home.page/cards
                importName: Markdown
                config:
                  layouts:
                    xl: { w: 6, h: 4, x: 6 }
                    lg: { w: 6, h: 4, x: 6 }
                    md: { w: 6, h: 4, x: 6 }
                    sm: { w: 6, h: 4, x: 6 }
                    xs: { w: 6, h: 4, x: 6 }
                    xxs: { w: 6, h: 4, x: 6 }
                  props:
                    title: Important company links
                    content: |
                      ### RHDH
                      * [Website](https://developers.redhat.com/rhdh/overview)
                      * [Documentation](https://docs.redhat.com/en/documentation/red_hat_developer_hub/)
                      * [Documentation](https://docs.redhat.com/en/documentation/red_hat_developer_hub/)
                      * [Janus Plugins](https://github.com/janus-idp/backstage-plugins)
                      * [Backstage Community Plugins](https://github.com/backstage/community-plugins)
                      * [RHDH Plugins](https://github.com/redhat-developer/rhdh-plugins)
                      * [RHDH Showcase](https://github.com/redhat-developer/rhdh)
      ```

  Placeholder

  :   ``` yaml
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-dynamic-home-page:
            mountPoints:
              - mountPoint: home.page/cards
                importName: Placeholder
                config:
                  layouts:
                    xl: { w: 1, h: 1 }
                    lg: { w: 1, h: 1 }
                    md: { w: 1, h: 1 }
                    sm: { w: 1, h: 1 }
                    xs: { w: 1, h: 1 }
                    xxs: { w: 1, h: 1 }
                  props:
                    showBorder: true
                    debugContent: '1'
      ```

  Catalog starred entities

  :   ``` yaml
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-dynamic-home-page:
            mountPoints:
              - mountPoint: home.page/cards
                importName: CatalogStarredEntitiesCard
      ```

  Featured docs

  :   ``` yaml
      dynamicPlugins:
        frontend:
          red-hat-developer-hub.backstage-plugin-dynamic-home-page:
            mountPoints:
              - mountPoint: home.page/cards
                importName: FeaturedDocsCard
      ```

</div>

### Defining the layout of the Red Hat Developer Hub Home page {#defining-the-layout-of-the-product-home-page_customizing-the-home-page}

The Home page uses a 12-column grid to position your cards. You can use
the optimal parameters to define the layout of your Developer Hub Home
page.

<div>

::: title
Prerequisites
:::

- Include the following optimal parameters in each of your breakpoints:

  - width (w)

  - height (h)

  - position (x and y)

</div>

<div>

::: title
Procedure
:::

- Configure your Developer Hub `app-config.yaml` configuration file by
  choosing one of the following options:

  - Use the full space on smaller windows and half of the space on
    larger windows as follows:

</div>

``` yaml
dynamicPlugins:
  frontend:
    red-hat-developer-hub.backstage-plugin-dynamic-home-page:
      mountPoints:
        - mountPoint: home.page/cards
          importName: Placeholder
          config:
            layouts:
              xl: { w: 6, h: 2 }
              lg: { w: 6, h: 2 }
              md: { w: 6, h: 2 }
              sm: { w: 12, h: 2 }
              xs: { w: 12, h: 2 }
              xxs: { w: 12, h: 2 }
            props:
              showBorder: true
              debugContent: a placeholder
```

- Show the cards side by side by defining the `x` parameter as shown in
  the following example:

``` yaml
dynamicPlugins:
  frontend:
    red-hat-developer-hub.backstage-plugin-dynamic-home-page:
      mountPoints:
        - mountPoint: home.page/cards
          importName: Placeholder
          config:
            layouts:
              xl: { w: 6, h: 2 }
              lg: { w: 6, h: 2 }
              md: { w: 6, h: 2 }
              sm: { w: 12, h: 2 }
              xs: { w: 12, h: 2 }
              xxs: { w: 12, h: 2 }
            props:
              showBorder: true
              debugContent: left
        - mountPoint: home.page/cards
          importName: Placeholder
          config:
            layouts:
              xl: { w: 6, h: 2, x: 6 }
              lg: { w: 6, h: 2, x: 6 }
              md: { w: 6, h: 2, x: 6 }
              sm: { w: 12, h: 2, x: 0 }
              xs: { w: 12, h: 2, x: 0 }
              xxs: { w: 12, h: 2, x: 0 }
            props:
              showBorder: true
              debugContent: right
```

However, you can see a second card below this card by default.

- Show the cards in three columns by defining the `x` parameter as shown
  in the following example:

``` yaml
dynamicPlugins:
  frontend:
    red-hat-developer-hub.backstage-plugin-dynamic-home-page:
      mountPoints:
        - mountPoint: home.page/cards
          importName: Placeholder
          config:
            layouts:
              xl: { w: 4, h: 2 }
              lg: { w: 4, h: 2 }
              md: { w: 4, h: 2 }
              sm: { w: 6, h: 2 }
              xs: { w: 12, h: 2 }
              xxs: { w: 12, h: 2 }
            props:
              showBorder: true
              debugContent: left
        - mountPoint: home.page/cards
          importName: Placeholder
          config:
            layouts:
              xl: { w: 4, h: 2, x: 4 }
              lg: { w: 4, h: 2, x: 4 }
              md: { w: 4, h: 2, x: 4 }
              sm: { w: 6, h: 2, x: 6 }
              xs: { w: 12, h: 2 }
              xxs: { w: 12, h: 2 }
            props:
              showBorder: true
              debugContent: center
        - mountPoint: home.page/cards
          importName: Placeholder
          config:
            layouts:
              xl: { w: 4, h: 2, x: 8 }
              lg: { w: 4, h: 2, x: 8 }
              md: { w: 4, h: 2, x: 8 }
              sm: { w: 6, h: 2 }
              xs: { w: 12, h: 2 }
              xxs: { w: 12, h: 2 }
            props:
              showBorder: true
              debugContent: right
```

## Customizing the Quick access card

To access the Home page in Red Hat Developer Hub, the base URL must
include the `/developer-hub` proxy. You can configure the Home page by
passing the data into the `app-config.yaml` file as a proxy. You can
provide data to the Home page from the following sources:

- JSON files hosted on GitHub or GitLab.

- A dedicated service that provides the Home page data in JSON format
  using an API.

### Using hosted JSON files to provide data to the Quick access card {#using-hosted-json-files-to-provide-data-to-the-quick-access-card_customizing-the-quick-access-card}

<div>

::: title
Prerequisites
:::

- You have installed Red Hat Developer Hub by using either the Operator
  or Helm chart. See [Installing Red Hat Developer Hub on OpenShift
  Container
  Platform](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_red_hat_developer_hub_on_openshift_container_platform/index.html#assembly-install-rhdh-ocp).

</div>

<div>

::: title
Procedure
:::

- To access the data from the JSON files, add the following code to the
  `app-config.yaml` Developer Hub configuration file:

- Add the following code to the `app-config.yaml` file:

  ``` yaml
  proxy:
    endpoints:
      # Other Proxies
      # customize developer hub instance
      '/developer-hub':
        target: <DOMAIN_URL> # i.e https://raw.githubusercontent.com/
        pathRewrite:
          '^/api/proxy/developer-hub': <path to json file> # i.e /redhat-developer/rhdh/main/packages/app/public/homepage/data.json
        changeOrigin: true
        secure: true
        # Change to "false" in case of using self hosted cluster with a self-signed certificate
        headers:
      <HEADER_KEY>: <HEADER_VALUE> # optional and can be passed as needed i.e Authorization can be passed for private GitHub repo and PRIVATE-TOKEN can be passed for private GitLab repo
  ```

</div>

### Using a dedicated service to provide data to the Quick access card {#using-a-dedicated-service-to-provide-data-to-the-quick-access-card_customizing-the-quick-access-card}

When using a dedicated service, you can do the following tasks:

- Use the same service to provide the data to all configurable Developer
  Hub pages or use a different service for each page.

- Use the
  [`red-hat-developer-hub-customization-provider`](https://github.com/redhat-developer/red-hat-developer-hub-customization-provider)
  as an example service, which provides data for both the Home and Tech
  Radar pages. The `red-hat-developer-hub-customization-provider`
  service provides the same data as default Developer Hub data. You can
  fork the `red-hat-developer-hub-customization-provider` service
  repository from GitHub and modify it with your own data, if required.

- Deploy the `red-hat-developer-hub-customization-provider` service and
  the Developer Hub Helm chart on the same cluster.

<div>

::: title
Prerequisites
:::

- You have installed the Red Hat Developer Hub using Helm chart. For
  more information, see [Installing Red Hat Developer Hub on OpenShift
  Container Platform with the Helm
  chart](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_red_hat_developer_hub_on_openshift_container_platform/index.html#assembly-install-rhdh-ocp-helm).

</div>

:::: formalpara
::: title
Procedure
:::

To use a separate service to provide the Home page data, complete the
following steps:
::::

1.  From the **Developer** perspective in the Red Hat OpenShift
    Container Platform web console, click **+Add** \> **Import from
    Git**.

2.  Enter the URL of your Git repository into the **Git Repo URL**
    field.

    To use the `red-hat-developer-hub-customization-provider` service,
    add the URL for the
    [red-hat-developer-hub-customization-provider](https://github.com/redhat-developer/red-hat-developer-hub-customization-provider)
    repository or your fork of the repository containing your
    customizations.

3.  On the **General** tab, enter
    `red-hat-developer-hub-customization-provider` in the **Name** field
    and click **Create**.

4.  On the **Advanced Options** tab, copy the value from **Target
    Port**.

    :::: note
    ::: title
    :::

    **Target Port** automatically generates a Kubernetes or OpenShift
    Container Platform service to communicate with.
    ::::

5.  Add the following code to the [`app-config.yaml`
    file](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index):

    ``` yaml
    proxy:
      endpoints:
        # Other Proxies
        # customize developer hub instance
        '/developer-hub':
          target: ${HOMEPAGE_DATA_URL}
          changeOrigin: true
          # Change to "false" in case of using self-hosted cluster with a self-signed certificate
          secure: true
    ```

    - `http://<SERVICE_NAME>:8080`, for example,
      `http://rhdh-customization-provider:8080`.

      :::: note
      ::: title
      :::

      The `red-hat-developer-hub-customization-provider` service
      contains the 8080 port by default. If you are using a custom port,
      you can specify it with the \'PORT\' environmental variable in the
      `app-config.yaml` file.
      ::::

6.  Replace the `HOMEPAGE_DATA_URL` by adding the URL to `rhdh-secrets`
    or by directly replacing it in your custom ConfigMap.

7.  Delete the Developer Hub pod to ensure that the new configurations
    are loaded correctly.

<div>

::: title
Verification
:::

- To view the service, go to the **Administrator** perspective in the
  OpenShift Container Platform web console and click **Networking** \>
  **Service**.

  :::: note
  ::: title
  :::

  You can also view **Service Resources** in the Topology view.
  ::::

- Ensure that the provided API URL for the Home page returns the data in
  JSON format as shown in the following example:

  ``` json
  [
    {
      "title": "Dropdown 1",
      "isExpanded": false,
      "links": [
        {
          "iconUrl": "https://imagehost.com/image.png",
          "label": "Dropdown 1 Item 1",
          "url": "https://example.com/"
        },
        {
          "iconUrl": "https://imagehost2.org/icon.png",
          "label": "Dropdown 1 Item 2",
          "url": ""
        }
      ]
    },
    {
      "title": "Dropdown 2",
      "isExpanded": true,
      "links": [
        {
          "iconUrl": "http://imagehost3.edu/img.jpg",
          "label": "Dropdown 2 Item 1",
          "url": "http://example.com"
        }
      ]
    }
  ]
  ```

  :::: note
  ::: title
  :::

  If the request call fails or is not configured, the Developer Hub
  instance falls back to the default local data.
  ::::

- If the images or icons do not load, then allowlist them by adding your
  image or icon host URLs to the content security policy (csp) `img-src`
  in your custom ConfigMap as shown in the following example:

</div>

``` yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: app-config.yaml
data:
  app-config.yaml: |
    app:
      title: Red Hat Developer Hub
    backend:
      csp:
        connect-src:
          - "'self'"
          - 'http:'
          - 'https:'
        img-src:
          - "'self'"
          - 'data:'
          - <image host url 1>
          - <image host url 2>
          - <image host url 3>
    # Other Configurations
```
