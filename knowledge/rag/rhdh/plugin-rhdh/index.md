The Red Hat Developer Hub is an enterprise-grade, integrated developer
platform, extended through plugins, that helps reduce the friction and
frustration of developers while boosting their productivity.

## Plugins in Red Hat Developer Hub {#con-rhdh-plugins}

The Red Hat Developer Hub application offers a unified platform with
various plugins. Using the plugin ecosystem within the Developer Hub
application, you can access any kind of development infrastructure or
software development tool.

The plugins in Developer Hub maximize the productivity and streamline
the development workflows by maintaining the consistency in the overall
user experience.

## Dynamic plugin installation {#rhdh-installing-dynamic-plugins}

The dynamic plugin support is based on the backend plugin manager
package, which is a service that scans a configured root directory
(`dynamicPlugins.rootDirectory` in the app config) for dynamic plugin
packages and loads them dynamically.

You can use the dynamic plugins that come preinstalled with Red Hat
Developer Hub or install external dynamic plugins from a public NPM
registry.

### Preinstalled dynamic plugins {#con-preinstalled-dynamic-plugins}

Red Hat Developer Hub is preinstalled with a selection of dynamic
plugins.

The following preinstalled dynamic plugins are enabled by default:

- `@backstage-community/plugin-analytics-provider-segment`

- `@backstage-community/plugin-scaffolder-backend-module-quay`

- `@backstage-community/plugin-scaffolder-backend-module-regex`

- `@backstage/plugin-techdocs-backend`

- `@backstage/plugin-techdocs-module-addons-contrib`

- `@backstage/plugin-techdocs`

- `@red-hat-developer-hub/backstage-plugin-dynamic-home-page`

- `@red-hat-developer-hub/backstage-plugin-global-header`

The dynamic plugins that require custom configuration are disabled by
default.

Upon application startup, for each plugin that is disabled by default,
the `install-dynamic-plugins init container` within the Developer Hub
pod log displays a message similar to the following:

``` yaml
======= Skipping disabled dynamic plugin ./dynamic-plugins/dist/backstage-plugin-catalog-backend-module-github-dynamic
```

To enable this plugin, add a package with the same name to the Helm
chart and change the value in the `disabled` field to 'false'. For
example:

``` java
global:
  dynamic:
    includes:
      - dynamic-plugins.default.yaml
    plugins:
      - package: ./dynamic-plugins/dist/backstage-plugin-catalog-backend-module-github-dynamic
        disabled: false
```

:::: note
::: title
:::

The default configuration for a plugin is extracted from the
`dynamic-plugins.default.yaml` file, however, you can use a
`pluginConfig` entry to override the default configuration.
::::

#### Red Hat supported plugins {#_red-hat-supported-plugins}

Red Hat supports the following 21 plugins:

+-----------------+-----------------+-----------------+-----------------+
| **Name**        | **Plugin**      | **Version**     | **Path and      |
|                 |                 |                 | required        |
|                 |                 |                 | variables**     |
+=================+=================+=================+=================+
| Analytics       | `@backstage     | 1.12.0          | `./             |
| Provider        | -community/plug |                 | dynamic-plugins |
| Segment         | in-analytics-pr |                 | /dist/backstage |
|                 | ovider-segment` |                 | -community-plug |
|                 |                 |                 | in-analytics-pr |
|                 |                 |                 | ovider-segment` |
|                 |                 |                 |                 |
|                 |                 |                 | `SEG            |
|                 |                 |                 | MENT_WRITE_KEY` |
|                 |                 |                 |                 |
|                 |                 |                 | `SEG            |
|                 |                 |                 | MENT_TEST_MODE` |
+-----------------+-----------------+-----------------+-----------------+
| Argo CD         | `@roadiehq/bac  | 3.2.3           | `./dynamic-plu  |
|                 | kstage-plugin-a |                 | gins/dist/roadi |
|                 | rgo-cd-backend` |                 | ehq-backstage-p |
|                 |                 |                 | lugin-argo-cd-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `A              |
|                 |                 |                 | RGOCD_USERNAME` |
|                 |                 |                 |                 |
|                 |                 |                 | `A              |
|                 |                 |                 | RGOCD_PASSWORD` |
|                 |                 |                 |                 |
|                 |                 |                 | `ARGOCD         |
|                 |                 |                 | _INSTANCE1_URL` |
|                 |                 |                 |                 |
|                 |                 |                 | `ARG            |
|                 |                 |                 | OCD_AUTH_TOKEN` |
|                 |                 |                 |                 |
|                 |                 |                 | `ARGOCD         |
|                 |                 |                 | _INSTANCE2_URL` |
|                 |                 |                 |                 |
|                 |                 |                 | `ARGO           |
|                 |                 |                 | CD_AUTH_TOKEN2` |
+-----------------+-----------------+-----------------+-----------------+
| Dynamic Home    | `@red-hat-deve  | 1.1.0           | `./dyn          |
| Page            | loper-hub/backs |                 | amic-plugins/di |
|                 | tage-plugin-dyn |                 | st/red-hat-deve |
|                 | amic-home-page` |                 | loper-hub-backs |
|                 |                 |                 | tage-plugin-dyn |
|                 |                 |                 | amic-home-page` |
+-----------------+-----------------+-----------------+-----------------+
| GitHub          | `@ba            | 0.7.9           | `./d            |
|                 | ckstage/plugin- |                 | ynamic-plugins/ |
|                 | catalog-backend |                 | dist/backstage- |
|                 | -module-github` |                 | plugin-catalog- |
|                 |                 |                 | backend-module- |
|                 |                 |                 | github-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `GITHUB_ORG`    |
+-----------------+-----------------+-----------------+-----------------+
| GitHub Org      | `@backst        | 0.3.6           | `./dynam        |
|                 | age/plugin-cata |                 | ic-plugins/dist |
|                 | log-backend-mod |                 | /backstage-plug |
|                 | ule-github-org` |                 | in-catalog-back |
|                 |                 |                 | end-module-gith |
|                 |                 |                 | ub-org-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `GITHUB_URL`    |
|                 |                 |                 |                 |
|                 |                 |                 | `GITHUB_ORG`    |
+-----------------+-----------------+-----------------+-----------------+
| Global Header   | `@red-hat-      | 1.0.0           | `.              |
|                 | developer-hub/b |                 | /dynamic-plugin |
|                 | ackstage-plugin |                 | s/dist/red-hat- |
|                 | -global-header` |                 | developer-hub-b |
|                 |                 |                 | ackstage-plugin |
|                 |                 |                 | -global-header` |
+-----------------+-----------------+-----------------+-----------------+
| Keycloak        | `               | 3.7.0           | `               |
|                 | @backstage-comm |                 | ./dynamic-plugi |
|                 | unity/plugin-ca |                 | ns/dist/backsta |
|                 | talog-backend-m |                 | ge-community-pl |
|                 | odule-keycloak` |                 | ugin-catalog-ba |
|                 |                 |                 | ckend-module-ke |
|                 |                 |                 | ycloak-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `KEY            |
|                 |                 |                 | CLOAK_BASE_URL` |
|                 |                 |                 |                 |
|                 |                 |                 | `KEYCLO         |
|                 |                 |                 | AK_LOGIN_REALM` |
|                 |                 |                 |                 |
|                 |                 |                 | `               |
|                 |                 |                 | KEYCLOAK_REALM` |
|                 |                 |                 |                 |
|                 |                 |                 | `KEYC           |
|                 |                 |                 | LOAK_CLIENT_ID` |
|                 |                 |                 |                 |
|                 |                 |                 | `KEYCLOAK       |
|                 |                 |                 | _CLIENT_SECRET` |
+-----------------+-----------------+-----------------+-----------------+
| Kubernetes      | `@backst        | 0.19.2          | `./dynam        |
|                 | age/plugin-kube |                 | ic-plugins/dist |
|                 | rnetes-backend` |                 | /backstage-plug |
|                 |                 |                 | in-kubernetes-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `K8             |
|                 |                 |                 | S_CLUSTER_NAME` |
|                 |                 |                 |                 |
|                 |                 |                 | `K              |
|                 |                 |                 | 8S_CLUSTER_URL` |
|                 |                 |                 |                 |
|                 |                 |                 | `K8S            |
|                 |                 |                 | _CLUSTER_TOKEN` |
+-----------------+-----------------+-----------------+-----------------+
| Kubernetes      | `@back          | 2.5.0           | `./dyn          |
|                 | stage-community |                 | amic-plugins/di |
|                 | /plugin-scaffol |                 | st/backstage-co |
|                 | der-backend-mod |                 | mmunity-plugin- |
|                 | ule-kubernetes` |                 | scaffolder-back |
|                 |                 |                 | end-module-kube |
|                 |                 |                 | rnetes-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| OCM             | `@b             | 5.3.0           | `./dynamic      |
|                 | ackstage-commun |                 | -plugins/dist/b |
|                 | ity/plugin-ocm` |                 | ackstage-commun |
|                 |                 |                 | ity-plugin-ocm` |
+-----------------+-----------------+-----------------+-----------------+
| OCM             | `@backstage     | 5.4.0           | `./dynamic-     |
|                 | -community/plug |                 | plugins/dist/ba |
|                 | in-ocm-backend` |                 | ckstage-communi |
|                 |                 |                 | ty-plugin-ocm-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `OCM_HUB_NAME`  |
|                 |                 |                 |                 |
|                 |                 |                 | `OCM_HUB_URL`   |
|                 |                 |                 |                 |
|                 |                 |                 | `OCM_SA_TOKEN`  |
+-----------------+-----------------+-----------------+-----------------+
| Quay            | `@ba            | 1.18.1          | `./dynamic-     |
|                 | ckstage-communi |                 | plugins/dist/ba |
|                 | ty/plugin-quay` |                 | ckstage-communi |
|                 |                 |                 | ty-plugin-quay` |
+-----------------+-----------------+-----------------+-----------------+
| Quay            | `@backstage-com | 2.4.0           | `./dynamic-plug |
|                 | munity/plugin-s |                 | ins/dist/backst |
|                 | caffolder-backe |                 | age-community-p |
|                 | nd-module-quay` |                 | lugin-scaffolde |
|                 |                 |                 | r-backend-modul |
|                 |                 |                 | e-quay-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| RBAC            | `@ba            | 1.38.2          | `./dynamic-     |
|                 | ckstage-communi |                 | plugins/dist/ba |
|                 | ty/plugin-rbac` |                 | ckstage-communi |
|                 |                 |                 | ty-plugin-rbac` |
+-----------------+-----------------+-----------------+-----------------+
| Regex           | `               | 2.4.0           | `               |
|                 | @backstage-comm |                 | ./dynamic-plugi |
|                 | unity/plugin-sc |                 | ns/dist/backsta |
|                 | affolder-backen |                 | ge-community-pl |
|                 | d-module-regex` |                 | ugin-scaffolder |
|                 |                 |                 | -backend-module |
|                 |                 |                 | -regex-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Signals         | `@bac           | 0.3.0           | `./dy           |
|                 | kstage/plugin-s |                 | namic-plugins/d |
|                 | ignals-backend` |                 | ist/backstage-p |
|                 |                 |                 | lugin-signals-b |
|                 |                 |                 | ackend-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| TechDocs        | `@backstage/p   | 1.12.2          | `./dy           |
|                 | lugin-techdocs` |                 | namic-plugins/d |
|                 |                 |                 | ist/backstage-p |
|                 |                 |                 | lugin-techdocs` |
+-----------------+-----------------+-----------------+-----------------+
| TechDocs        | `@back          | 1.11.5          | `./dyn          |
|                 | stage/plugin-te |                 | amic-plugins/di |
|                 | chdocs-backend` |                 | st/backstage-pl |
|                 |                 |                 | ugin-techdocs-b |
|                 |                 |                 | ackend-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| TechDocs Module | `@bac           | 1.1.20          | `./dynamic-p    |
| Addons Contrib  | kstage/plugin-t |                 | lugins/dist/bac |
|                 | echdocs-module- |                 | kstage-plugin-t |
|                 | addons-contrib` |                 | echdocs-module- |
|                 |                 |                 | addons-contrib` |
+-----------------+-----------------+-----------------+-----------------+
| Tekton          | `@back          | 3.19.0          | `./dynamic-pl   |
|                 | stage-community |                 | ugins/dist/back |
|                 | /plugin-tekton` |                 | stage-community |
|                 |                 |                 | -plugin-tekton` |
+-----------------+-----------------+-----------------+-----------------+
| Topology        | `@backst        | 1.32.0          | `./dynamic-plug |
|                 | age-community/p |                 | ins/dist/backst |
|                 | lugin-topology` |                 | age-community-p |
|                 |                 |                 | lugin-topology` |
+-----------------+-----------------+-----------------+-----------------+

:::: note
::: title
:::

- For more information about configuring KeyCloak, see [Configuring
  dynamic
  plugins](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/introduction_to_plugins/index).

- For more information about configuring TechDocs, see [Configuring
  TechDocs](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/customizing_red_hat_developer_hub/index#configuring-techdocs).
::::

#### Technology Preview plugins {#snip-dynamic-plugins-support_plugin-rhdh}

:::: important
::: title
:::

Red Hat Developer Hub includes a select number of Technology Preview
plugins, available for customers to configure and enable. These plugins
are provided with support scoped per Technical Preview terms, might not
be functionally complete, and Red Hat does not recommend using them for
production. These features provide early access to upcoming product
features, enabling customers to test functionality and provide feedback
during the development process.

For more information on Red Hat Technology Preview features, see
[Technology Preview Features
Scope](https://access.redhat.com/support/offerings/techpreview/).
::::

##### Red Hat Technology Preview plugins {#rhdh-tech-preview-plugins}

Red Hat provides Technology Preview support for the following 56
plugins:

+-----------------+-----------------+-----------------+-----------------+
| **Name**        | **Plugin**      | **Version**     | **Path and      |
|                 |                 |                 | required        |
|                 |                 |                 | variables**     |
+=================+=================+=================+=================+
| 3scale          | `@backstage-co  | 3.2.0           | `./dynamic-plu  |
|                 | mmunity/plugin- |                 | gins/dist/backs |
|                 | 3scale-backend` |                 | tage-community- |
|                 |                 |                 | plugin-3scale-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `THREE          |
|                 |                 |                 | SCALE_BASE_URL` |
|                 |                 |                 |                 |
|                 |                 |                 | `THREESCAL      |
|                 |                 |                 | E_ACCESS_TOKEN` |
+-----------------+-----------------+-----------------+-----------------+
| ACR             | `@b             | 1.11.0          | `./dynamic      |
|                 | ackstage-commun |                 | -plugins/dist/b |
|                 | ity/plugin-acr` |                 | ackstage-commun |
|                 |                 |                 | ity-plugin-acr` |
+-----------------+-----------------+-----------------+-----------------+
| Argo CD (Red    | `@backstage-c   | 1.14.0          | `./dy           |
| Hat)            | ommunity/plugin |                 | namic-plugins/d |
|                 | -redhat-argocd` |                 | ist/backstage-c |
|                 |                 |                 | ommunity-plugin |
|                 |                 |                 | -redhat-argocd` |
+-----------------+-----------------+-----------------+-----------------+
| Argo CD         | `@roadi         | 1.5.0           | `./dyna         |
|                 | ehq/scaffolder- |                 | mic-plugins/dis |
|                 | backend-argocd` |                 | t/roadiehq-scaf |
|                 |                 |                 | folder-backend- |
|                 |                 |                 | argocd-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `A              |
|                 |                 |                 | RGOCD_USERNAME` |
|                 |                 |                 |                 |
|                 |                 |                 | `A              |
|                 |                 |                 | RGOCD_PASSWORD` |
|                 |                 |                 |                 |
|                 |                 |                 | `ARGOCD         |
|                 |                 |                 | _INSTANCE1_URL` |
|                 |                 |                 |                 |
|                 |                 |                 | `ARG            |
|                 |                 |                 | OCD_AUTH_TOKEN` |
|                 |                 |                 |                 |
|                 |                 |                 | `ARGOCD         |
|                 |                 |                 | _INSTANCE2_URL` |
|                 |                 |                 |                 |
|                 |                 |                 | `ARGO           |
|                 |                 |                 | CD_AUTH_TOKEN2` |
+-----------------+-----------------+-----------------+-----------------+
| Azure           | `@back          | 0.2.5           | `./dyn          |
|                 | stage/plugin-sc |                 | amic-plugins/di |
|                 | affolder-backen |                 | st/backstage-pl |
|                 | d-module-azure` |                 | ugin-scaffolder |
|                 |                 |                 | -backend-module |
|                 |                 |                 | -azure-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Azure Devops    | `@backstage-    | 0.9.0           | `./d            |
|                 | community/plugi |                 | ynamic-plugins/ |
|                 | n-azure-devops` |                 | dist/backstage- |
|                 |                 |                 | community-plugi |
|                 |                 |                 | n-azure-devops` |
+-----------------+-----------------+-----------------+-----------------+
| Azure Devops    | `@bac           | 0.11.0          | `./dy           |
|                 | kstage-communit |                 | namic-plugins/d |
|                 | y/plugin-azure- |                 | ist/backstage-c |
|                 | devops-backend` |                 | ommunity-plugin |
|                 |                 |                 | -azure-devops-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `AZURE_TOKEN`   |
|                 |                 |                 |                 |
|                 |                 |                 | `AZURE_ORG`     |
+-----------------+-----------------+-----------------+-----------------+
| Azure           | `@parfu         | 0.3.0           | `./dyna         |
| Repositories    | emerie-douglas/ |                 | mic-plugins/dis |
|                 | scaffolder-back |                 | t/parfuemerie-d |
|                 | end-module-azur |                 | ouglas-scaffold |
|                 | e-repositories` |                 | er-backend-modu |
|                 |                 |                 | le-azure-reposi |
|                 |                 |                 | tories-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Bitbucket Cloud | `@backstage/p   | 0.4.4           | `./dynamic-pl   |
|                 | lugin-catalog-b |                 | ugins/dist/back |
|                 | ackend-module-b |                 | stage-plugin-ca |
|                 | itbucket-cloud` |                 | talog-backend-m |
|                 |                 |                 | odule-bitbucket |
|                 |                 |                 | -cloud-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `BITBU          |
|                 |                 |                 | CKET_WORKSPACE` |
+-----------------+-----------------+-----------------+-----------------+
| Bitbucket Cloud | `               | 0.2.5           | `               |
|                 | @backstage/plug |                 | ./dynamic-plugi |
|                 | in-scaffolder-b |                 | ns/dist/backsta |
|                 | ackend-module-b |                 | ge-plugin-scaff |
|                 | itbucket-cloud` |                 | older-backend-m |
|                 |                 |                 | odule-bitbucket |
|                 |                 |                 | -cloud-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Bitbucket       | `@backstage/pl  | 0.3.1           | `./dynamic-plu  |
| Server          | ugin-catalog-ba |                 | gins/dist/backs |
|                 | ckend-module-bi |                 | tage-plugin-cat |
|                 | tbucket-server` |                 | alog-backend-mo |
|                 |                 |                 | dule-bitbucket- |
|                 |                 |                 | server-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `               |
|                 |                 |                 | BITBUCKET_HOST` |
+-----------------+-----------------+-----------------+-----------------+
| Bitbucket       | `@              | 0.2.5           | `.              |
| Server          | backstage/plugi |                 | /dynamic-plugin |
|                 | n-scaffolder-ba |                 | s/dist/backstag |
|                 | ckend-module-bi |                 | e-plugin-scaffo |
|                 | tbucket-server` |                 | lder-backend-mo |
|                 |                 |                 | dule-bitbucket- |
|                 |                 |                 | server-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Bulk Import     | `@red-ha        | 1.11.0          | `./dynamic-plug |
|                 | t-developer-hub |                 | ins/dist/red-ha |
|                 | /backstage-plug |                 | t-developer-hub |
|                 | in-bulk-import` |                 | -backstage-plug |
|                 |                 |                 | in-bulk-import` |
+-----------------+-----------------+-----------------+-----------------+
| Bulk Import     | `               | 5.3.0           | `               |
|                 | @red-hat-develo |                 | ./dynamic-plugi |
|                 | per-hub/backsta |                 | ns/dist/red-hat |
|                 | ge-plugin-bulk- |                 | -developer-hub- |
|                 | import-backend` |                 | backstage-plugi |
|                 |                 |                 | n-bulk-import-b |
|                 |                 |                 | ackend-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Datadog         | `@road          | 2.4.2           | `./dynamic-pl   |
|                 | iehq/backstage- |                 | ugins/dist/road |
|                 | plugin-datadog` |                 | iehq-backstage- |
|                 |                 |                 | plugin-datadog` |
+-----------------+-----------------+-----------------+-----------------+
| Dynatrace       | `@backsta       | 10.2.0          | `               |
|                 | ge-community/pl |                 | ./dynamic-plugi |
|                 | ugin-dynatrace` |                 | ns/dist/backsta |
|                 |                 |                 | ge-community-pl |
|                 |                 |                 | ugin-dynatrace` |
+-----------------+-----------------+-----------------+-----------------+
| Gerrit          | `@backs         | 0.2.5           | `./dyna         |
|                 | tage/plugin-sca |                 | mic-plugins/dis |
|                 | ffolder-backend |                 | t/backstage-plu |
|                 | -module-gerrit` |                 | gin-scaffolder- |
|                 |                 |                 | backend-module- |
|                 |                 |                 | gerrit-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| GitHub          | `@backs         | 0.5.5           | `./dyna         |
|                 | tage/plugin-sca |                 | mic-plugins/dis |
|                 | ffolder-backend |                 | t/backstage-plu |
|                 | -module-github` |                 | gin-scaffolder- |
|                 |                 |                 | backend-module- |
|                 |                 |                 | github-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| GitHub Actions  | `@backstage-co  | 0.7.1           | `./dyn          |
|                 | mmunity/plugin- |                 | amic-plugins/di |
|                 | github-actions` |                 | st/backstage-co |
|                 |                 |                 | mmunity-plugin- |
|                 |                 |                 | github-actions` |
+-----------------+-----------------+-----------------+-----------------+
| GitHub Insights | `@roadiehq/bac  | 3.1.3           | `./dyn          |
|                 | kstage-plugin-g |                 | amic-plugins/di |
|                 | ithub-insights` |                 | st/roadiehq-bac |
|                 |                 |                 | kstage-plugin-g |
|                 |                 |                 | ithub-insights` |
+-----------------+-----------------+-----------------+-----------------+
| GitHub Issues   | `@backstage-c   | 0.6.0           | `./dy           |
|                 | ommunity/plugin |                 | namic-plugins/d |
|                 | -github-issues` |                 | ist/backstage-c |
|                 |                 |                 | ommunity-plugin |
|                 |                 |                 | -github-issues` |
+-----------------+-----------------+-----------------+-----------------+
| GitHub Pull     | `@ro            | 3.2.1           | `./dynamic-     |
| Requests        | adiehq/backstag |                 | plugins/dist/ro |
|                 | e-plugin-github |                 | adiehq-backstag |
|                 | -pull-requests` |                 | e-plugin-github |
|                 |                 |                 | -pull-requests` |
+-----------------+-----------------+-----------------+-----------------+
| GitLab          | `@immobiliar    | 6.8.0           | `./d            |
|                 | elabs/backstage |                 | ynamic-plugins/ |
|                 | -plugin-gitlab` |                 | dist/immobiliar |
|                 |                 |                 | elabs-backstage |
|                 |                 |                 | -plugin-gitlab` |
+-----------------+-----------------+-----------------+-----------------+
| GitLab          | `@ba            | 0.6.2           | `./d            |
|                 | ckstage/plugin- |                 | ynamic-plugins/ |
|                 | catalog-backend |                 | dist/backstage- |
|                 | -module-gitlab` |                 | plugin-catalog- |
|                 |                 |                 | backend-module- |
|                 |                 |                 | gitlab-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| GitLab          | `@imm           | 6.8.0           | `./dy           |
|                 | obiliarelabs/ba |                 | namic-plugins/d |
|                 | ckstage-plugin- |                 | ist/immobiliare |
|                 | gitlab-backend` |                 | labs-backstage- |
|                 |                 |                 | plugin-gitlab-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `GITLAB_HOST`   |
|                 |                 |                 |                 |
|                 |                 |                 | `GITLAB_TOKEN`  |
+-----------------+-----------------+-----------------+-----------------+
| GitLab          | `@backs         | 0.7.1           | `./dyna         |
|                 | tage/plugin-sca |                 | mic-plugins/dis |
|                 | ffolder-backend |                 | t/backstage-plu |
|                 | -module-gitlab` |                 | gin-scaffolder- |
|                 |                 |                 | backend-module- |
|                 |                 |                 | gitlab-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| GitLab Org      | `@backst        | 0.2.5           | `./dynam        |
|                 | age/plugin-cata |                 | ic-plugins/dist |
|                 | log-backend-mod |                 | /backstage-plug |
|                 | ule-gitlab-org` |                 | in-catalog-back |
|                 |                 |                 | end-module-gitl |
|                 |                 |                 | ab-org-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Http Request    | `@roa           | 5.3.0           | `./dy           |
|                 | diehq/scaffolde |                 | namic-plugins/d |
|                 | r-backend-modul |                 | ist/roadiehq-sc |
|                 | e-http-request` |                 | affolder-backen |
|                 |                 |                 | d-module-http-r |
|                 |                 |                 | equest-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Jenkins         | `@backs         | 0.16.0          | `./dynamic-plu  |
|                 | tage-community/ |                 | gins/dist/backs |
|                 | plugin-jenkins` |                 | tage-community- |
|                 |                 |                 | plugin-jenkins` |
+-----------------+-----------------+-----------------+-----------------+
| Jenkins         | `@backstage-com | 0.11.0          | `./dynamic-plug |
|                 | munity/plugin-j |                 | ins/dist/backst |
|                 | enkins-backend` |                 | age-community-p |
|                 |                 |                 | lugin-jenkins-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `JENKINS_URL`   |
|                 |                 |                 |                 |
|                 |                 |                 | `JE             |
|                 |                 |                 | NKINS_USERNAME` |
|                 |                 |                 |                 |
|                 |                 |                 | `JENKINS_TOKEN` |
+-----------------+-----------------+-----------------+-----------------+
| JFrog           | `@              | 1.13.0          | `./dynami       |
| Artifactory     | backstage-commu |                 | c-plugins/dist/ |
|                 | nity/plugin-jfr |                 | backstage-commu |
|                 | og-artifactory` |                 | nity-plugin-jfr |
|                 |                 |                 | og-artifactory` |
+-----------------+-----------------+-----------------+-----------------+
| Jira            | `@r             | 2.8.2           | `./dynamic      |
|                 | oadiehq/backsta |                 | -plugins/dist/r |
|                 | ge-plugin-jira` |                 | oadiehq-backsta |
|                 |                 |                 | ge-plugin-jira` |
+-----------------+-----------------+-----------------+-----------------+
| Kubernetes      | `@backstage/plu | 0.12.3          | `./dyna         |
|                 | gin-kubernetes` |                 | mic-plugins/dis |
|                 |                 |                 | t/backstage-plu |
|                 |                 |                 | gin-kubernetes` |
+-----------------+-----------------+-----------------+-----------------+
| Ldap            | `@              | 0.11.1          | `.              |
|                 | backstage/plugi |                 | /dynamic-plugin |
|                 | n-catalog-backe |                 | s/dist/backstag |
|                 | nd-module-ldap` |                 | e-plugin-catalo |
|                 |                 |                 | g-backend-modul |
|                 |                 |                 | e-ldap-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Lighthouse      | `@backstag      | 0.6.0           | `.              |
|                 | e-community/plu |                 | /dynamic-plugin |
|                 | gin-lighthouse` |                 | s/dist/backstag |
|                 |                 |                 | e-community-plu |
|                 |                 |                 | gin-lighthouse` |
+-----------------+-----------------+-----------------+-----------------+
| Marketplace     | `@red-ha        | 0.2.1           | `./dynamic-plug |
|                 | t-developer-hub |                 | ins/dist/red-ha |
|                 | /backstage-plug |                 | t-developer-hub |
|                 | in-marketplace` |                 | -backstage-plug |
|                 |                 |                 | in-marketplace` |
+-----------------+-----------------+-----------------+-----------------+
| Marketplace     | `               | 0.2.2           | `               |
|                 | @red-hat-develo |                 | ./dynamic-plugi |
|                 | per-hub/backsta |                 | ns/dist/red-hat |
|                 | ge-plugin-catal |                 | -developer-hub- |
|                 | og-backend-modu |                 | backstage-plugi |
|                 | le-marketplace` |                 | n-catalog-backe |
|                 |                 |                 | nd-module-marke |
|                 |                 |                 | tplace-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Marketplace     | `               | 0.2.0           | `               |
|                 | @red-hat-develo |                 | ./dynamic-plugi |
|                 | per-hub/backsta |                 | ns/dist/red-hat |
|                 | ge-plugin-marke |                 | -developer-hub- |
|                 | tplace-backend` |                 | backstage-plugi |
|                 |                 |                 | n-marketplace-b |
|                 |                 |                 | ackend-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| MS Graph        | `@bac           | 0.6.6           | `./dy           |
|                 | kstage/plugin-c |                 | namic-plugins/d |
|                 | atalog-backend- |                 | ist/backstage-p |
|                 | module-msgraph` |                 | lugin-catalog-b |
|                 |                 |                 | ackend-module-m |
|                 |                 |                 | sgraph-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Nexus           | `@backsta       | 1.12.0          | `               |
| Repository      | ge-community/pl |                 | ./dynamic-plugi |
| Manager         | ugin-nexus-repo |                 | ns/dist/backsta |
|                 | sitory-manager` |                 | ge-community-pl |
|                 |                 |                 | ugin-nexus-repo |
|                 |                 |                 | sitory-manager` |
+-----------------+-----------------+-----------------+-----------------+
| Notifications   | `@b             | 0.5.1           | `./dynamic      |
|                 | ackstage/plugin |                 | -plugins/dist/b |
|                 | -notifications` |                 | ackstage-plugin |
|                 |                 |                 | -notifications` |
+-----------------+-----------------+-----------------+-----------------+
| Notifications   | `@backstage     | 0.5.1           | `./dynamic-     |
|                 | /plugin-notific |                 | plugins/dist/ba |
|                 | ations-backend` |                 | ckstage-plugin- |
|                 |                 |                 | notifications-b |
|                 |                 |                 | ackend-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Notifications   | `@backsta       | 0.3.5           | `./dynami       |
| Module Email    | ge/plugin-notif |                 | c-plugins/dist/ |
|                 | ications-backen |                 | backstage-plugi |
|                 | d-module-email` |                 | n-notifications |
|                 |                 |                 | -backend-module |
|                 |                 |                 | -email-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `               |
|                 |                 |                 | EMAIL_HOSTNAME` |
|                 |                 |                 |                 |
|                 |                 |                 | `               |
|                 |                 |                 | EMAIL_USERNAME` |
|                 |                 |                 |                 |
|                 |                 |                 | `               |
|                 |                 |                 | EMAIL_PASSWORD` |
|                 |                 |                 |                 |
|                 |                 |                 | `EMAIL_SENDER`  |
+-----------------+-----------------+-----------------+-----------------+
| PagerDuty       | `@pagerduty/ba  | 0.15.2          | `./dyn          |
|                 | ckstage-plugin` |                 | amic-plugins/di |
|                 |                 |                 | st/pagerduty-ba |
|                 |                 |                 | ckstage-plugin` |
+-----------------+-----------------+-----------------+-----------------+
| PagerDuty       | `@pager         | 0.9.2           | `./dyna         |
|                 | duty/backstage- |                 | mic-plugins/dis |
|                 | plugin-backend` |                 | t/pagerduty-bac |
|                 |                 |                 | kstage-plugin-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `PAGE           |
|                 |                 |                 | RDUTY_API_BASE` |
|                 |                 |                 |                 |
|                 |                 |                 | `PAGER          |
|                 |                 |                 | DUTY_CLIENT_ID` |
|                 |                 |                 |                 |
|                 |                 |                 | `PAGERDUTY      |
|                 |                 |                 | _CLIENT_SECRET` |
|                 |                 |                 |                 |
|                 |                 |                 | `PAGER          |
|                 |                 |                 | DUTY_SUBDOMAIN` |
+-----------------+-----------------+-----------------+-----------------+
| Pingidentity    | `@bac           | 0.2.0           | `./dy           |
|                 | kstage-communit |                 | namic-plugins/d |
|                 | y/plugin-catalo |                 | ist/backstage-c |
|                 | g-backend-modul |                 | ommunity-plugin |
|                 | e-pingidentity` |                 | -catalog-backen |
|                 |                 |                 | d-module-pingid |
|                 |                 |                 | entity-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Scaffolder      | `@backs         | 2.2.0           | `./dyna         |
| Relation        | tage-community/ |                 | mic-plugins/dis |
| Processor       | plugin-catalog- |                 | t/backstage-com |
|                 | backend-module- |                 | munity-plugin-c |
|                 | scaffolder-rela |                 | atalog-backend- |
|                 | tion-processor` |                 | module-scaffold |
|                 |                 |                 | er-relation-pro |
|                 |                 |                 | cessor-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Security        | `               | 3.1.2           | `./dynam        |
| Insights        | @roadiehq/backs |                 | ic-plugins/dist |
|                 | tage-plugin-sec |                 | /roadiehq-backs |
|                 | urity-insights` |                 | tage-plugin-sec |
|                 |                 |                 | urity-insights` |
+-----------------+-----------------+-----------------+-----------------+
| ServiceNow      | `@back          | 2.4.0           | `./dyn          |
|                 | stage-community |                 | amic-plugins/di |
|                 | /plugin-scaffol |                 | st/backstage-co |
|                 | der-backend-mod |                 | mmunity-plugin- |
|                 | ule-servicenow` |                 | scaffolder-back |
|                 |                 |                 | end-module-serv |
|                 |                 |                 | icenow-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `SERVI          |
|                 |                 |                 | CENOW_BASE_URL` |
|                 |                 |                 |                 |
|                 |                 |                 | `SERVI          |
|                 |                 |                 | CENOW_USERNAME` |
|                 |                 |                 |                 |
|                 |                 |                 | `SERVI          |
|                 |                 |                 | CENOW_PASSWORD` |
+-----------------+-----------------+-----------------+-----------------+
| Signals         | `@backstage/    | 0.0.15          | `./d            |
|                 | plugin-signals` |                 | ynamic-plugins/ |
|                 |                 |                 | dist/backstage- |
|                 |                 |                 | plugin-signals` |
+-----------------+-----------------+-----------------+-----------------+
| SonarQube       | `@backsta       | 0.10.0          | `               |
|                 | ge-community/pl |                 | ./dynamic-plugi |
|                 | ugin-sonarqube` |                 | ns/dist/backsta |
|                 |                 |                 | ge-community-pl |
|                 |                 |                 | ugin-sonarqube` |
+-----------------+-----------------+-----------------+-----------------+
| SonarQube       | `@              | 0.5.0           | `.              |
|                 | backstage-commu |                 | /dynamic-plugin |
|                 | nity/plugin-son |                 | s/dist/backstag |
|                 | arqube-backend` |                 | e-community-plu |
|                 |                 |                 | gin-sonarqube-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `SONARQUBE_URL` |
|                 |                 |                 |                 |
|                 |                 |                 | `S              |
|                 |                 |                 | ONARQUBE_TOKEN` |
+-----------------+-----------------+-----------------+-----------------+
| SonarQube       | `@bac           | 2.4.0           | `./dy           |
|                 | kstage-communit |                 | namic-plugins/d |
|                 | y/plugin-scaffo |                 | ist/backstage-c |
|                 | lder-backend-mo |                 | ommunity-plugin |
|                 | dule-sonarqube` |                 | -scaffolder-bac |
|                 |                 |                 | kend-module-son |
|                 |                 |                 | arqube-dynamic` |
+-----------------+-----------------+-----------------+-----------------+
| Tech Radar      | `@backstag      | 1.2.0           | `.              |
|                 | e-community/plu |                 | /dynamic-plugin |
|                 | gin-tech-radar` |                 | s/dist/backstag |
|                 |                 |                 | e-community-plu |
|                 |                 |                 | gin-tech-radar` |
+-----------------+-----------------+-----------------+-----------------+
| Tech Radar      | `@b             | 1.2.0           | `./             |
|                 | ackstage-commun |                 | dynamic-plugins |
|                 | ity/plugin-tech |                 | /dist/backstage |
|                 | -radar-backend` |                 | -community-plug |
|                 |                 |                 | in-tech-radar-b |
|                 |                 |                 | ackend-dynamic` |
|                 |                 |                 |                 |
|                 |                 |                 | `TECH_          |
|                 |                 |                 | RADAR_DATA_URL` |
+-----------------+-----------------+-----------------+-----------------+
| Utils           | `@roadiehq/sc   | 3.3.0           | `./dynamic-pl   |
|                 | affolder-backen |                 | ugins/dist/road |
|                 | d-module-utils` |                 | iehq-scaffolder |
|                 |                 |                 | -backend-module |
|                 |                 |                 | -utils-dynamic` |
+-----------------+-----------------+-----------------+-----------------+

##### Community plugins {#rhdh-community-plugins}

:::: important
::: title
:::

Red Hat Developer Hub (RHDH) includes a select number of
community-supported plugins, available for customers to enable and
configure. These community plugins are augmented by Red Hat to be
dynamic plugin capable, and are provided with support scoped per
Technical Preview terms.

Details on how Red Hat provides support for bundled community dynamic
plugins are available on the [Red Hat Developer Support
Policy](https://access.redhat.com/policy/developerhub-support-policy)
page.
::::

RHDH includes the following 2 community plugins:

+-----------------+-----------------+-----------------+-----------------+
| **Name**        | **Plugin**      | **Version**     | **Path and      |
|                 |                 |                 | required        |
|                 |                 |                 | variables**     |
+=================+=================+=================+=================+
| Argo CD         | `@road          | 2.8.4           | `./dynamic-pl   |
|                 | iehq/backstage- |                 | ugins/dist/road |
|                 | plugin-argo-cd` |                 | iehq-backstage- |
|                 |                 |                 | plugin-argo-cd` |
+-----------------+-----------------+-----------------+-----------------+
| Global Floating | `@red-hat-d     | 1.0.0           | `./             |
| Action Button   | eveloper-hub/ba |                 | dynamic-plugins |
|                 | ckstage-plugin- |                 | /dist/red-hat-d |
|                 | global-floating |                 | eveloper-hub-ba |
|                 | -action-button` |                 | ckstage-plugin- |
|                 |                 |                 | global-floating |
|                 |                 |                 | -action-button` |
+-----------------+-----------------+-----------------+-----------------+

### Other installable plugins {#rhdh-compatible-plugins}

The following Technology Preview plugins are not preinstalled and must
be installed from an external source:

+-----------------+-----------------+-----------------+-----------------+
| **Name**        | **Plugin**      | **Version**     | **Installation  |
|                 |                 |                 | Details**       |
+=================+=================+=================+=================+
| Ansible         | `@a             | 1.0.0           | [Learn          |
| Automation      | nsible/plugin-b |                 | more](https     |
| Platform        | ackstage-rhaap` |                 | ://docs.redhat. |
| Frontend        |                 |                 | com/en/document |
|                 |                 |                 | ation/red_hat_a |
|                 |                 |                 | nsible_automati |
|                 |                 |                 | on_platform/2.4 |
|                 |                 |                 | /html/installin |
|                 |                 |                 | g_ansible_plug- |
|                 |                 |                 | ins_for_red_hat |
|                 |                 |                 | _developer_hub) |
+-----------------+-----------------+-----------------+-----------------+
| Ansible         | `@ansible/p     | 1.0.0           | [Learn          |
| Automation      | lugin-backstage |                 | more](https     |
| Platform        | -rhaap-backend` |                 | ://docs.redhat. |
|                 |                 |                 | com/en/document |
|                 |                 |                 | ation/red_hat_a |
|                 |                 |                 | nsible_automati |
|                 |                 |                 | on_platform/2.4 |
|                 |                 |                 | /html/installin |
|                 |                 |                 | g_ansible_plug- |
|                 |                 |                 | ins_for_red_hat |
|                 |                 |                 | _developer_hub) |
+-----------------+-----------------+-----------------+-----------------+
| Ansible         | `@ansible/plug  | 1.0.0           | [Learn          |
| Automation      | in-scaffolder-b |                 | more](https     |
| Platform        | ackend-module-b |                 | ://docs.redhat. |
| Scaffolder      | ackstage-rhaap` |                 | com/en/document |
| Backend         |                 |                 | ation/red_hat_a |
|                 |                 |                 | nsible_automati |
|                 |                 |                 | on_platform/2.4 |
|                 |                 |                 | /html/installin |
|                 |                 |                 | g_ansible_plug- |
|                 |                 |                 | ins_for_red_hat |
|                 |                 |                 | _developer_hub) |
+-----------------+-----------------+-----------------+-----------------+

### Installing and using Ansible plug-ins for Red Hat Developer Hub {#rhdh-ansible}

Ansible plug-ins for Red Hat Developer Hub deliver an Ansible-specific
portal experience with curated learning paths, push-button content
creation, integrated development tools, and other opinionated resources.

:::: important
::: title
:::

The Ansible plug-ins are a Technology Preview feature only.

Technology Preview features are not supported with Red Hat production
service level agreements (SLAs), might not be functionally complete, and
Red Hat does not recommend using them for production. These features
provide early access to upcoming product features, enabling customers to
test functionality and provide feedback during the development process.

For more information on Red Hat Technology Preview features, see
[Technology Preview Features
Scope](https://access.redhat.com/support/offerings/techpreview/).

Additional detail on how Red Hat provides support for bundled community
dynamic plugins is available on the [Red Hat Developer Support
Policy](https://access.redhat.com/policy/developerhub-support-policy)
page.
::::

#### For administrators {#_for-administrators}

To install and configure the Ansible plugins, see [*Installing Ansible
plug-ins for Red Hat Developer
Hub*](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.4/html/installing_ansible_plug-ins_for_red_hat_developer_hub/index).

#### For users {#_for-users}

To use the Ansible plugins, see [*Using Ansible plug-ins for Red Hat
Developer
Hub*](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.4/html/using_ansible_plug-ins_for_red_hat_developer_hub/index).

### Installation and configuration of Keycloak {#rhdh-keycloak_plugin-rhdh}

The Keycloak backend plugin, which integrates Keycloak into Developer
Hub, has the following capabilities:

- Synchronization of Keycloak users in a realm.

- Synchronization of Keycloak groups and their users in a realm.

#### Installation {#_installation}

The Keycloak plugin is pre-loaded in Developer Hub with basic
configuration properties. To enable it, set the `disabled` property to
`false` as follows:

``` yaml
global:
  dynamic:
    includes:
      - dynamic-plugins.default.yaml
    plugins:
      - package: ./dynamic-plugins/dist/backstage-community-plugin-catalog-backend-module-keycloak-dynamic
        disabled: false
```

#### Basic configuration {#_basic-configuration}

To enable the Keycloak plugin, you must set the following environment
variables:

- `KEYCLOAK_BASE_URL`

- `KEYCLOAK_LOGIN_REALM`

- `KEYCLOAK_REALM`

- `KEYCLOAK_CLIENT_ID`

- `KEYCLOAK_CLIENT_SECRET`

#### Advanced configuration {#_advanced-configuration}

:::: formalpara
::: title
Schedule configuration
:::

You can configure a schedule in the `app-config.yaml` file, as follows:
::::

``` yaml
     catalog:
       providers:
         keycloakOrg:
           default:
             # ...
             # highlight-add-start
             schedule: # optional; same options as in TaskScheduleDefinition
               # supports cron, ISO duration, "human duration" as used in code
               frequency: { minutes: 1 }
               # supports ISO duration, "human duration" as used in code
               timeout: { minutes: 1 }
               initialDelay: { seconds: 15 }
               # highlight-add-end
```

:::: note
::: title
:::

If you have made any changes to the schedule in the `app-config.yaml`
file, then restart to apply the changes.
::::

:::: formalpara
::: title
Keycloak query parameters
:::

You can override the default Keycloak query parameters in the
`app-config.yaml` file, as follows:
::::

``` yaml
   catalog:
     providers:
       keycloakOrg:
         default:
           # ...
           # highlight-add-start
           userQuerySize: 500 # Optional
           groupQuerySize: 250 # Optional
           # highlight-add-end
```

Communication between Developer Hub and Keycloak is enabled by using the
Keycloak API. Username and password, or client credentials are supported
authentication methods.

The following table describes the parameters that you can configure to
enable the plugin under
`catalog.providers.keycloakOrg.<ENVIRONMENT_NAME>` object in the
`app-config.yaml` file:

+-----------------+-----------------+-----------------+-----------------+
| Name            | Description     | Default Value   | Required        |
+=================+=================+=================+=================+
| `baseUrl`       | Location of the | \"\"            | Yes             |
|                 | Keycloak        |                 |                 |
|                 | server, such as |                 |                 |
|                 | `https://localh |                 |                 |
|                 | ost:8443/auth`. |                 |                 |
|                 | Note that the   |                 |                 |
|                 | newer versions  |                 |                 |
|                 | of Keycloak     |                 |                 |
|                 | omit the        |                 |                 |
|                 | `/auth` context |                 |                 |
|                 | path.           |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| `realm`         | Realm to        | `master`        | No              |
|                 | synchronize     |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| `loginRealm`    | Realm used to   | `master`        | No              |
|                 | authenticate    |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| `username`      | Username to     | \"\"            | Yes if using    |
|                 | authenticate    |                 | password based  |
|                 |                 |                 | authentication  |
+-----------------+-----------------+-----------------+-----------------+
| `password`      | Password to     | \"\"            | Yes if using    |
|                 | authenticate    |                 | password based  |
|                 |                 |                 | authentication  |
+-----------------+-----------------+-----------------+-----------------+
| `clientId`      | Client ID to    | \"\"            | Yes if using    |
|                 | authenticate    |                 | client          |
|                 |                 |                 | credentials     |
|                 |                 |                 | based           |
|                 |                 |                 | authentication  |
+-----------------+-----------------+-----------------+-----------------+
| `clientSecret`  | Client Secret   | \"\"            | Yes if using    |
|                 | to authenticate |                 | client          |
|                 |                 |                 | credentials     |
|                 |                 |                 | based           |
|                 |                 |                 | authentication  |
+-----------------+-----------------+-----------------+-----------------+
| `userQuerySize` | Number of users | `100`           | No              |
|                 | to query at a   |                 |                 |
|                 | time            |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| `               | Number of       | `100`           | No              |
| groupQuerySize` | groups to query |                 |                 |
|                 | at a time       |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

When using client credentials, the access type must be set to
`confidential` and service accounts must be enabled. You must also add
the following roles from the `realm-management` client role:

- `query-groups`

- `query-users`

- `view-users`

#### Limitations {#_limitations}

If you have self-signed or corporate certificate issues, you can set the
following environment variable before starting Developer Hub:

`NODE_TLS_REJECT_UNAUTHORIZED=0`

:::: note
::: title
:::

The solution of setting the environment variable is not recommended.
::::

### Installation and configuration of Nexus Repository Manager {#rhdh-nexus}

The Nexus Repository Manager plugin displays the information about your
build artifacts in your Developer Hub application. The build artifacts
are available in the Nexus Repository Manager.

:::: important
::: title
:::

The Nexus Repository Manager plugin is a Technology Preview feature
only.

Technology Preview features are not supported with Red Hat production
service level agreements (SLAs), might not be functionally complete, and
Red Hat does not recommend using them for production. These features
provide early access to upcoming product features, enabling customers to
test functionality and provide feedback during the development process.

For more information on Red Hat Technology Preview features, see
[Technology Preview Features
Scope](https://access.redhat.com/support/offerings/techpreview/).

Additional detail on how Red Hat provides support for bundled community
dynamic plugins is available on the [Red Hat Developer Support
Policy](https://access.redhat.com/policy/developerhub-support-policy)
page.
::::

#### For administrators {#_for-administrators-2}

##### Installing and configuring the Nexus Repository Manager plugin {#_installing-and-configuring-the-nexus-repository-manager-plugin}

:::: formalpara
::: title
Installation
:::

The Nexus Repository Manager plugin is pre-loaded in Developer Hub with
basic configuration properties. To enable it, set the disabled property
to `false` as follows:
::::

``` yaml
global:
  dynamic:
    includes:
      - dynamic-plugins.default.yaml
    plugins:
      - package: ./dynamic-plugins/dist/backstage-community-plugin-nexus-repository-manager
        disabled: false
```

<div>

::: title
Configuration
:::

1.  Set the proxy to the desired Nexus Repository Manager server in the
    `app-config.yaml` file as follows:

    ``` yaml
    proxy:
        '/nexus-repository-manager':
        target: 'https://<NEXUS_REPOSITORY_MANAGER_URL>'
        headers:
            X-Requested-With: 'XMLHttpRequest'
            # Uncomment the following line to access a private Nexus Repository Manager using a token
            # Authorization: 'Bearer <YOUR TOKEN>'
        changeOrigin: true
        # Change to "false" in case of using self hosted Nexus Repository Manager instance with a self-signed certificate
        secure: true
    ```

2.  Optional: Change the base URL of Nexus Repository Manager proxy as
    follows:

    ``` yaml
    nexusRepositoryManager:
        # default path is `/nexus-repository-manager`
        proxyPath: /custom-path
    ```

3.  Optional: Enable the following experimental annotations:

    ``` yaml
    nexusRepositoryManager:
        experimentalAnnotations: true
    ```

4.  Annotate your entity using the following annotations:

    ``` yaml
    metadata:
        annotations:
        # insert the chosen annotations here
        # example
        nexus-repository-manager/docker.image-name: `<ORGANIZATION>/<REPOSITORY>`,
    ```

</div>

#### For users {#_for-users-2}

##### Using the Nexus Repository Manager plugin in Developer Hub {#_using-the-nexus-repository-manager-plugin-in-developer-hub}

The Nexus Repository Manager is a front-end plugin that enables you to
view the information about build artifacts.

<div>

::: title
Prerequisites
:::

- Your Developer Hub application is installed and running.

- You have installed the Nexus Repository Manager plugin. For the
  installation process, see [Installing and configuring the Nexus
  Repository Manager
  plugin](#_installing-and-configuring-the-nexus-repository-manager-plugin).

</div>

<div>

::: title
Procedure
:::

1.  Open your Developer Hub application and select a component from the
    **Catalog** page.

2.  Go to the **BUILD ARTIFACTS** tab.

    The **BUILD ARTIFACTS** tab contains a list of build artifacts and
    related information, such as **VERSION**, **REPOSITORY**,
    **REPOSITORY TYPE**, **MANIFEST**, **MODIFIED**, and **SIZE**.

    ![nexus-repository-manager-tab](images/rhdh-plugins-reference/nexus-repository-manager.png)

</div>

### Installation and configuration of Tekton {#installation-and-configuration-tekton}

You can use the Tekton plugin to visualize the results of CI/CD pipeline
runs on your Kubernetes or OpenShift clusters. The plugin allows users
to visually see high level status of all associated tasks in the
pipeline for their applications.

#### For administrators {#_for-administrators-3}

##### Installation {#installing-tekton-plugin}

<div>

::: title
Prerequisites
:::

- You have installed and configured the `@backstage/plugin-kubernetes`
  and `@backstage/plugin-kubernetes-backend` dynamic plugins.

- You have configured the Kubernetes plugin to connect to the cluster
  using a `ServiceAccount`.

- The `ClusterRole` must be granted for custom resources (PipelineRuns
  and TaskRuns) to the `ServiceAccount` accessing the cluster.

  :::: note
  ::: title
  :::

  If you have the RHDH Kubernetes plugin configured, then the
  `ClusterRole` is already granted.
  ::::

- To view the pod logs, you have granted permissions for `pods/log`.

- You can use the following code to grant the `ClusterRole` for custom
  resources and pod logs:

  ``` yaml
  kubernetes:
     ...
     customResources:
       - group: 'tekton.dev'
         apiVersion: 'v1'
         plural: 'pipelineruns'
       - group: 'tekton.dev'
         apiVersion: 'v1'


   ...
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: backstage-read-only
    rules:
      - apiGroups:
          - ""
        resources:
          - pods/log
        verbs:
          - get
          - list
          - watch
      ...
      - apiGroups:
          - tekton.dev
        resources:
          - pipelineruns
          - taskruns
        verbs:
          - get
          - list
  ```

  You can use the prepared manifest for a read-only `ClusterRole`, which
  provides access for both Kubernetes plugin and Tekton plugin.

- Add the following annotation to the entity's `catalog-info.yaml` file
  to identify whether an entity contains the Kubernetes resources:

  ``` yaml
  annotations:
    ...

    backstage.io/kubernetes-id: <BACKSTAGE_ENTITY_NAME>
  ```

- You can also add the `backstage.io/kubernetes-namespace` annotation to
  identify the Kubernetes resources using the defined namespace.

  ``` yaml
  annotations:
    ...

    backstage.io/kubernetes-namespace: <RESOURCE_NS>
  ```

- Add the following annotation to the `catalog-info.yaml` file of the
  entity to enable the Tekton related features in RHDH. The value of the
  annotation identifies the name of the RHDH entity:

  ``` yaml
  annotations:
    ...

    janus-idp.io/tekton : <BACKSTAGE_ENTITY_NAME>
  ```

- Add a custom label selector, which RHDH uses to find the Kubernetes
  resources. The label selector takes precedence over the ID
  annotations.

  ``` yaml
  annotations:
    ...

    backstage.io/kubernetes-label-selector: 'app=my-app,component=front-end'
  ```

- Add the following label to the resources so that the Kubernetes plugin
  gets the Kubernetes resources from the requested entity:

  ``` yaml
  labels:
    ...

    backstage.io/kubernetes-id: <BACKSTAGE_ENTITY_NAME>
  ```

  :::: note
  ::: title
  :::

  When you use the label selector, the mentioned labels must be present
  on the resource.
  ::::

</div>

<div>

::: title
Procedure
:::

- The Tekton plugin is pre-loaded in RHDH with basic configuration
  properties. To enable it, set the disabled property to false as
  follows:

  ``` yaml
  global:
    dynamic:
      includes:
        - dynamic-plugins.default.yaml
      plugins:
        - package: ./dynamic-plugins/dist/backstage-community-plugin-tekton
          disabled: false
  ```

</div>

#### For users {#_for-users-3}

##### Using the Tekton plugin in RHDH {#using-tekton-plugin}

You can use the Tekton front-end plugin to view `PipelineRun` resources.

<div>

::: title
Prerequisites
:::

- You have installed the Red Hat Developer Hub (RHDH).

- You have installed the Tekton plugin. For the installation process,
  see [Installing and configuring the Tekton
  plugin](#installation-and-configuration-tekton).

</div>

<div>

::: title
Procedure
:::

1.  Open your RHDH application and select a component from the
    **Catalog** page.

2.  Go to the **CI** tab.

    The **CI** tab displays the list of PipelineRun resources associated
    with a Kubernetes cluster. The list contains pipeline run details,
    such as **NAME**, **VULNERABILITIES**, **STATUS**, **TASK STATUS**,
    **STARTED**, and **DURATION**.

    ![ci-cd-tab-tekton](images/rhdh-plugins-reference/tekton-plugin-pipeline.png)

3.  Click the expand row button besides PipelineRun name in the list to
    view the PipelineRun visualization. The pipeline run resource
    includes tasks to complete. When you hover the mouse pointer on a
    task card, you can view the steps to complete that particular task.

    ![ci-cd-tab-tekton](images/rhdh-plugins-reference/tekton-plugin-pipeline-expand.png)

</div>

### Enabling and configuring Argo CD plugin {#rhdh-argocd}

You can use the Argo CD plugin to visualize the Continuous Delivery (CD)
workflows in OpenShift GitOps. This plugin provides a visual overview of
the application's status, deployment details, commit message, author of
the commit, container image promoted to environment and deployment
history.

#### Using the Argo CD plugin {#_using-the-argo-cd-plugin}

<div>

::: title
Prerequisites
:::

- You have enabled the Argo CD plugin in Red Hat Developer Hub RHDH.

</div>

<div>

::: title
Procedures
:::

1.  Select the **Catalog** tab and choose the component that you want to
    use.

2.  Select the **CD** tab to view insights into deployments managed by
    Argo CD.

    ![CD tab Argo CD](images/rhdh-plugins-reference/argocd.png)

3.  Select an appropriate card to view the deployment details (for
    example, commit message, author name, and deployment history).

    ![Sidebar](images/rhdh-plugins-reference/sidebar.png)

    a.  Click the link icon (![Link
        icon](images/rhdh-plugins-reference/link.png)) to open the
        deployment details in Argo CD.

4.  Select the **Overview** tab and navigate to the Deployment summary
    section to review the summary of your application's deployment
    across namespaces. Additionally, select an appropriate Argo CD app
    to open the deployment details in Argo CD, or select a commit ID
    from the Revision column to review the changes in GitLab or GitHub.

    ![Deployment
    summary](images/rhdh-plugins-reference/deployment_summary.png)

</div>

<div>

::: title
Additional resources
:::

- For more information on installing dynamic plugins, see [Installing
  and viewing plugins in Red Hat Developer
  Hub](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_and_viewing_plugins_in_red_hat_developer_hub/index).

</div>
