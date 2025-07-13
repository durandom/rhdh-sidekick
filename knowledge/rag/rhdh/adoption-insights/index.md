## Adoption Insights {#assembly-adoption-insights}

:::: important
::: title
:::

This section describes Developer Preview features in the Adoption
Insights plugin. Developer Preview features are not supported by Red Hat
in any way and are not functionally complete or production-ready. Do not
use Developer Preview features for production or business-critical
workloads. Developer Preview features provide early access to
functionality in advance of possible inclusion in a Red Hat product
offering. Customers can use these features to test functionality and
provide feedback during the development process. Developer Preview
features might not have any documentation, are subject to change or
removal at any time, and have received limited testing. Red Hat might
provide ways to submit feedback on Developer Preview features without an
associated SLA.

For more information about the support scope of Red Hat Developer
Preview features, see [Developer Preview Support
Scope](https://access.redhat.com/support/offerings/devpreview/).
::::

### About Adoption Insights {#con-about-adoption-insights_title-adoption-insights}

As organizations generate an increasing number of data events, there is
a growing need for detailed insights into the adoption and engagement
metrics of the internal developer portal. These insights help platform
engineers make data-driven decisions to improve its performance,
usability, and translate them into actionable insights.

You can use Adoption Insights in Red Hat Developer Hub to visualize key
metrics and trends to get information about the usage of Developer Hub
in your organization. The information provided by Adoption Insights in
Developer Hub pinpoints areas of improvement, highlights popular
features, and evaluates progress toward adoption goals. You can also
monitor user growth against license users and identify trends over time.

:::: note
::: title
:::

Currently, the Adoption Insights plugin cannot be used alongside the
built-in `plugin-analytics-provider-segment` plugin. For a workaround,
see [Adoption Insights in Red Hat Developer
Hub.](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/red_hat_developer_hub_release_notes/index#developer-preview-rhdhpai-510)
::::

The Adoption Insights dashboard in Developer Hub includes the following
cards:

- **Active users**

- **Total nuber of users**

- **Top catalog entities**

- **Top 3 templates**

- **Top 3 techdocs**

- **Top 3 plugins**

- **Portal searches**

![adoption
insights](images/rhdh-plugins-reference/adoption-insights.jpg)

### Installing the Adoption Insights plugin in Red Hat Developer Hub {#proc-install-adoption-insights_title-adoption-insights}

For the Red Hat Developer Hub Adoption Insights plugin, you must
manually install the plugin.

:::: formalpara
::: title
Procedure
:::

To enable the Adoption Insights plugin, complete the following steps:
::::

1.  Set the `disabled` property to `false` in your
    `app-config-dynamic.yaml` file as shown in the following example:

    ``` yaml
    - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/red-hat-developer-hub-backstage-plugin-adoption-insights:bs_1.35.1__0.0.2!red-hat-developer-hub-backstage-plugin-adoption-insights
      disabled: false
      pluginConfig:
        dynamicPlugins:
          frontend:
            red-hat-developer-hub.backstage-plugin-adoption-insights:
              appIcons:
                - name: adoptionInsightsIcon
                  importName: AdoptionInsightsIcon
              dynamicRoutes:
                - path: /adoption-insights
                  importName: AdoptionInsightsPage
                  menuItem:
                    icon: adoptionInsightsIcon
                    text: Adoption Insights
              menuItems:
                adoption-insights:
                  parent: admin
                  icon: adoptionInsightsIcon
    - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/red-hat-developer-hub-backstage-plugin-adoption-insights-backend:bs_1.35.1__0.0.2!red-hat-developer-hub-backstage-plugin-adoption-insights-backend
      disabled: false
    - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/red-hat-developer-hub-backstage-plugin-analytics-module-adoption-insights:bs_1.35.1__0.0.2!red-hat-developer-hub-backstage-plugin-analytics-module-adoption-insights
      disabled: false
      pluginConfig:
        dynamicPlugins:
          frontend:
            red-hat-developer-hub.backstage-plugin-analytics-module-adoption-insights:
              apiFactories:
                - importName: AdoptionInsightsAnalyticsApiFactory
    ```

2.  Optional: Configure the required RBAC permission for the users who
    are not administrators as shown in the following example:

    ``` yaml
    p, role:default/_<your_team>_, adoption-insights.events.read, read, allow
    g, user:default/_<your_user>_, role:default/_<your_team>_
    ```

    See [Permission policies in Red Hat Developer
    Hub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/authorization_in_red_hat_developer_hub/index#ref-rbac-permission-policies_title-authorization).

### Configuring the Adoption Insights plugin in Red Hat Developer Hub {#proc-configure-adoption-insights_title-adoption-insights}

You can enable the Adoption Insights plugin by configuring the Red Hat
Developer Hub Helm chart or the Red Hat Developer Hub Operator
ConfigMap.

<div>

::: title
Procedure
:::

- To configure the Adoption Insights plugin in Developer Hub, in your
  Red Hat Developer Hub `app-config.yaml` file, add the following code:

  :::: formalpara
  ::: title
  `app-config.yaml` fragment
  :::

  ``` terminal
  app:
    analytics:
      adoptionInsights:
        maxBufferSize: 20
        flushInterval: 5000
        debug: false
        licensedUsers: 2000
  ```
  ::::

  - (Optional) Specifies the maximum buffer size for event batching. The
    default value is `20`.

  - (Optional) Specifies the flush interval in milliseconds for event
    batching. The default value is `5000ms`.

  - (Optional) The default value is `false`.

  - (Optional) Specifies the maximum number of licensed users who can
    access the RHDH instance. The default value is `100`.

</div>

### Using Adoption Insights in Red Hat Developer Hub {#proc-using-adoption-insights_title-adoption-insights}

In the Developer Hub application, on the navigation menu, click
**Administration → Adoption Insights**.

#### Setting the duration of data metrics {#proc-setting-duration-of-data-metrics_title-adoption-insights}

You can set the data metrics duration using any of the time ranges, such
as **Today**, **Last week**, **Last month**, **Last 28 days** (default),
**Last year**, or **Date range...​**.

<div>

::: title
Procedure
:::

1.  On the top of the screen, click the dropdown list to display the
    choices.

2.  Select the duration choice for which you want to see the data
    metrics.

</div>

![date
range](images/rhdh-plugins-reference/adoption-insights-daterange.jpg)

### Viewing the Adoption Insights card {#proc-viewing-adoption-insights-card_title-adoption-insights}

#### Viewing the active users {#_viewing-the-active-users}

The **Active users** card displays the total number of active users over
a specified time range. It also provides a breakdown comparison of **New
users** and **Returning users** in a line/area graph format. You can
export the user data in a .csv format.

- **Returning users**: Existing users who have logged into Developer Hub

- **New users**: New users who have registered and logged into Developer
  Hub

![active users](images/rhdh-plugins-reference/active-users.jpg)

<div>

::: title
Procedure
:::

- To view the list of active users in your Developer Hub instance, go to
  **Administration → Adoption Insights**, see the Active users card.

- To view the exact number of users for a particular day, hover over the
  corresponding date in the **Active users** card.

- To export the user data in a .csv format, click the **Export CSV**
  label.

</div>

#### Viewing the total number of users {#_viewing-the-total-number-of-users}

This card displays the total number of users that have license to use
Red Hat Developer Hub. It also provides a comparison of the number of
**Logged-in users** and **Licensed users** in numeric and percentage
form.

- **Logged-in users**: Total number of users, including licensed and
  unlicensed users, currently logged in to Developer Hub.

- **Licensed users**: Total number of licensed users logged in to
  Developer Hub. You can set the number of licensed users in your
  Developer Hub app-config.yaml file.

<div>

::: title
Procedure
:::

- To view the total number of users in your Developer Hub instance in
  numeric and percentage forms, go to **Administration → Adoption
  Insights** and see the **Total number of users** card.

- To view a percentage representation of the total number of logged-in
  users among the total number of licensed users, hover over the tooltip
  in the **Total number of users** card.

</div>

#### Viewing the top catalog entities {#_viewing-the-top-catalog-entities}

This card lists the most viewed catalog entities (like components, APIs,
and so on) and documentation entries, including usage statistics, in a
table.

Each item displays the following details:

- **Name**: Name of the catalog

- **Kind**: Type of the catalog

- **Last used**: The last time the catalog was used

- **Views**: The number of times the catalog was viewed

<div>

::: title
Procedure
:::

- To view the most commonly used catalog entities in your Developer Hub
  instance, go to **Administration → Adoption Insights** and see the
  **Top catalog entities** card.

- To know more about the displayed catalog entity, hover over the
  catalog entity name.

</div>

#### Viewing the top 3 templates {#_viewing-the-top-3-templates}

This card lists the three most commonly used templates in a table. You
can click the down arrow next to **3 rows** to view the full list of the
commonly used templates.

- **Name**: Name of the template

- **Mostly in use by**: Type of user using this template most frequently

- **Executions**: Number of times this template was used

<div>

::: title
Procedure
:::

- To view the most commonly used templates in your Developer Hub
  instance, go to **Administration → Adoption Insights** and see the
  **Top 3 templates** card.

- To know more about the displayed template, hover over the template
  name.

</div>

#### Viewing the top 3 techdocs {#_viewing-the-top-3-techdocs}

This card lists the most viewed documentation entries, including the
total views, in a table.

- **Name**: Name of the documentation

- **Entity**: Type of the documentation

- **Last used**: The last time the documentation was viewed

- **Views**: Number of times the documentation was visited

<div>

::: title
Procedure
:::

- To view the most commonly used templates in your Developer Hub
  instance, go to **Administration → Adoption Insights** and see the
  **Top 3 techdocs** card.

- To know more about the displayed techdocs, hover over the techdocs
  name.

</div>

#### Viewing the top 3 plugins {#_viewing-the-top-3-plugins}

This card lists the three most commonly used plugins in a table. You can
click the down arrow next to **3 rows** to view the full list of the
commonly used plugins.

- **Name**: Name of the plugin

- **Trend**: Popularity of the plugin as a graph

- **Views**: Number of times this plugin was seen

<div>

::: title
Procedure
:::

- To view the most commonly used plugins and the plugin page visit
  trends in your Developer Hub instance, go to **Administration →
  Adoption Insights** and see the **Top 3 plugins** card.

- To know more about the displayed plugin, hover over the plugin name.

</div>

### Modifying the number of displayed records {#proc-modify-number-of-displayed-records_title-adoption-insights}

#### Modifying the number of displayed records in Top catalog entities {#_modifying-the-number-of-displayed-records-in-top-catalog-entities}

You can modify the number of records that are displayed in the **Top
catalog entities** card. You can select any of the following number of
records for display:

- **Top 3**

- **Top 5**

- **Top 10**

- **Top 20**

By default, the top three most viewed catalog entities are displayed.

<div>

::: title
Procedure
:::

- Go to **Administration → Adoption Insights** and click the **Down**
  arrow next to **3 rows** to change the number of displayed records.

</div>

![Catalog Entities
dropdown](images/rhdh-plugins-reference/adoption-insights-catalog-entities.jpg)

#### Modifying the number of displayed records in Top 3 templates {#_modifying-the-number-of-displayed-records-in-top-3-templates}

You can modify the number of records that are displayed in the **Top 3
templates** card. You can select any of the following number of records
for display:

- **Top 3**

- **Top 5**

- **Top 10**

- **Top 20**

By default, the top three most viewed templates are displayed.

<div>

::: title
Procedure
:::

- Go to **Administration → Adoption Insights** and click the **Down**
  arrow next to **3 rows** to change the number of displayed records.

</div>

#### Modifying the number of displayed records in Top 3 techdocs {#_modifying-the-number-of-displayed-records-in-top-3-techdocs}

You can modify the number of records that are displayed in the **Top 3
techdocs** card. You can select any of the following number of records
for display:

- **Top 3**

- **Top 5**

- **Top 10**

- **Top 20**

By default, the top three most viewed TechDocs are displayed.

<div>

::: title
Procedure
:::

- Go to **Administration → Adoption Insights** and click the **Down**
  arrow next to **3 rows** to change the number of displayed records.

</div>

#### Modifying the number of displayed records in Top 3 plugins {#_modifying-the-number-of-displayed-records-in-top-3-plugins}

You can modify the number of records that are displayed in the **Top 3
plugins** card. You can select any of the following number of records
for display:

- **Top 3**

- **Top 5**

- **Top 10**

- **Top 20**

By default, the top three most viewed plugins are displayed.

<div>

::: title
Procedure
:::

- Go to **Administration → Adoption Insights** and click the **Down**
  arrow next to **3 rows** to change the number of displayed records.

</div>

### Filtering records to display specific catalog entities in Top catalog entities {#proc-filter-records-to-display-spec_title-adoption-insights}

You can use the dropdown filter in the title to filter the table display
by any of the items. By default, the **Top catalog entities** card
displays all of the items in your Developer Hub instance.

:::: formalpara
::: title
Procedure
:::

To view a specific catalog entity in the table, complete the following
step:
::::

- Go to **Administration → Adoption Insights**, click the dropdown
  filter on the **Top catalog entities** card, and select the item that
  you want to view.

### Viewing Searches {#proc-viewing-searches_title-adoption-insights}

In the **searches** card, you can view the following data:

- Visualizes the number of portal searches and trends over time as a
  graph

- Displays the total for the period in the card title

- Clarifies the average number each hour/day/week/month depending on the
  time period chosen
