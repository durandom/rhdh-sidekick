## About TechDocs {#about-techdocs_customizing-display}

The Red Hat Developer Hub instance comes with the TechDocs plugin
preinstalled and enabled by default. Your organization can use the
TechDocs plugin to create, find, and manage documentation in a central
location and in a standardized way. You can also enhance your technical
documentation experience with built-in TechDocs features and add-ons.
For example:

Docs-like-code approach

:   Write your technical documentation in Markdown files that are stored
    inside your project repository along with your code.

Documentation site generation

:   Use MkDocs to create a full-featured, Markdown-based, static HTML
    site for your documentation that is rendered centrally in Developer
    Hub.

Documentation site metadata and integrations

:   See additional metadata about the documentation site alongside the
    static documentation, such as the date of the last update, the site
    owner, top contributors, open GitHub issues, Slack support channels,
    and Stack Overflow Enterprise tags.

Built-in navigation and search

:   Locate the information that you need within a document quickly and
    easily.

Add-ons

:   Make your documentation more functional and interactive with
    supported TechDocs add-ons. Some add-ons are preinstalled and
    enabled by default. To extend the default functionality, you can
    dynamically load external and third-party add-ons into your Red Hat
    Developer Hub instance. If you want to further customize your
    TechDocs experience, you can create add-ons that meet specific
    documentation needs for your organization.

## TechDocs configuration {#configuring-techdocs}

The TechDocs plugin is preinstalled and enabled on a Developer Hub
instance by default. You can disable or enable the TechDocs plugin, and
change other parameters, by configuring the Red Hat Developer Hub Helm
chart or the Red Hat Developer Hub Operator ConfigMap.

:::: important
::: title
:::

Red Hat Developer Hub includes a built-in TechDocs builder that
generates static HTML documentation from your codebase. However, the
default basic setup of the local builder is not intended for production.
::::

You can use a CI/CD pipeline with the repository that has a dedicated
job to generate docs for TechDocs. The generated static files are stored
in OpenShift Data Foundation or in a cloud storage solution of your
choice and published to a static HTML documentation site.

After you configure OpenShift Data Foundation to store the files that
TechDocs generates, you can configure the TechDocs plugin to use the
OpenShift Data Foundation for cloud storage.

<div>

::: title
Additional resources
:::

- For more information, see [Configuring dynamic
  plugins](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/introduction_to_plugins/index).

</div>

### Configuring storage for TechDocs files {#con-techdocs-configure-storage_configuring-techdocs}

The TechDocs publisher stores generated files in local storage or in
cloud storage, such as OpenShift Data Foundation, Google GCS, AWS S3, or
Azure Blob Storage.

#### Using OpenShift Data Foundation for file storage {#proc-techdocs-using-odf-storage_configuring-techdocs}

You can configure OpenShift Data Foundation to store the files that
TechDocs generates instead of relying on other cloud storage solutions.

OpenShift Data Foundation provides an `ObjectBucketClaim` custom
resource (CR) that you can use to request an S3 compatible bucket
backend. You must install the OpenShift Data Foundation Operator to use
this feature.

<div>

::: title
Prerequisites
:::

- An OpenShift Container Platform administrator has installed the
  OpenShift Data Foundation Operator in Red Hat OpenShift Container
  Platform. For more information, see [OpenShift Container Platform -
  Installing Red Hat OpenShift Data Foundation
  Operator](https://access.redhat.com/documentation/en-us/red_hat_openshift_data_foundation/4.15/html/deploying_openshift_data_foundation_using_amazon_web_services/deploy-using-dynamic-storage-devices-aws#installing-openshift-data-foundation-operator-using-the-operator-hub_cloud-storage).

- An OpenShift Container Platform administrator has created an OpenShift
  Data Foundation cluster and configured the `StorageSystem` schema. For
  more information, see [OpenShift Container Platform - Creating an
  OpenShift Data Foundation
  cluster](https://access.redhat.com/documentation/en-us/red_hat_openshift_data_foundation/latest/html/deploying_openshift_data_foundation_using_amazon_web_services/deploy-using-dynamic-storage-devices-aws#creating-an-openshift-data-foundation-service_cloud-storage).

</div>

<div>

::: title
Procedure
:::

- Create an `ObjectBucketClaim` CR where the generated TechDocs files
  are stored. For example:

  ``` yaml
  apiVersion: objectbucket.io/v1alpha1
  kind: ObjectBucketClaim
  metadata:
    name: <rhdh_bucket_claim_name>
  spec:
    generateBucketName: <rhdh_bucket_claim_name>
    storageClassName: openshift-storage.noobaa.io
  ```

  :::: note
  ::: title
  :::

  Creating the Developer Hub `ObjectBucketClaim` CR automatically
  creates both the Developer Hub `ObjectBucketClaim` config map and
  secret. The config map and secret have the same name as the
  `ObjectBucketClaim` CR.
  ::::

</div>

After you create the `ObjectBucketClaim` CR, you can use the information
stored in the config map and secret to make the information accessible
to the Developer Hub container as environment variables. Depending on
the method that you used to install Developer Hub, you add the access
information to either the Red Hat Developer Hub Helm chart or Operator
configuration.

<div>

::: title
Additional resources
:::

- For more information about the Object Bucket Claim, see [OpenShift
  Container Platform - Object Bucket
  Claim](https://access.redhat.com/documentation/en-us/red_hat_openshift_data_foundation/4.12/html/managing_hybrid_and_multicloud_resources/object-bucket-claim#doc-wrapper).

</div>

#### Making object storage accessible to containers by using the Helm chart {#proc-techdocs-configure-odf-helm_configuring-techdocs}

Creating a `ObjectBucketClaim` custom resource (CR) automatically
generates both the Developer Hub `ObjectBucketClaim` config map and
secret. The config map and secret contain `ObjectBucket` access
information. Adding the access information to the Helm chart
configuration makes it accessible to the Developer Hub container by
adding the following environment variables to the container:

- `BUCKET_NAME`

- `BUCKET_HOST`

- `BUCKET_PORT`

- `BUCKET_REGION`

- `BUCKET_SUBREGION`

- `AWS_ACCESS_KEY_ID`

- `AWS_SECRET_ACCESS_KEY`

These variables are then used in the TechDocs plugin configuration.

<div>

::: title
Prerequisites
:::

- You have installed Red Hat Developer Hub on OpenShift Container
  Platform using the Helm chart.

- You have created an `ObjectBucketClaim` CR for storing files generated
  by TechDocs. For more information see [Using OpenShift Data Foundation
  for file
  storage](#proc-techdocs-using-odf-storage_configuring-techdocs)

</div>

<div>

::: title
Procedure
:::

- In the `upstream.backstage` key in the Helm chart values, enter the
  name of the Developer Hub `ObjectBucketClaim` secret as the value for
  the `extraEnvVarsSecrets` field and the `extraEnvVarsCM` field. For
  example:

  ``` yaml
  upstream:
    backstage:
      extraEnvVarsSecrets:
        - <rhdh_bucket_claim_name>
      extraEnvVarsCM:
        - <rhdh_bucket_claim_name>
  ```

</div>

##### Example TechDocs Plugin configuration for the Helm chart {#ref-techdocs-example-config-plugin-helm_configuring-techdocs}

The following example shows a Developer Hub Helm chart configuration for
the TechDocs plugin:

``` yaml
global:
  dynamic:
    includes:
      - 'dynamic-plugins.default.yaml'
  plugins:
    - disabled: false
      package: ./dynamic-plugins/dist/backstage-plugin-techdocs-backend-dynamic
      pluginConfig:
        techdocs:
          builder: external
          generator:
            runIn: local
          publisher:
            awsS3:
              bucketName: '${BUCKET_NAME}'
              credentials:
                accessKeyId: '${AWS_ACCESS_KEY_ID}'
                secretAccessKey: '${AWS_SECRET_ACCESS_KEY}'
              endpoint: 'https://${BUCKET_HOST}'
              region: '${BUCKET_REGION}'
              s3ForcePathStyle: true
            type: awsS3
```

#### Making object storage accessible to containers by using the Operator {#proc-techdocs-configure-odf-operator_configuring-techdocs}

Creating a `ObjectBucketClaim` custom resource (CR) automatically
generates both the Developer Hub `ObjectBucketClaim` config map and
secret. The config map and secret contain `ObjectBucket` access
information. Adding the access information to the Operator configuration
makes it accessible to the Developer Hub container by adding the
following environment variables to the container:

- `BUCKET_NAME`

- `BUCKET_HOST`

- `BUCKET_PORT`

- `BUCKET_REGION`

- `BUCKET_SUBREGION`

- `AWS_ACCESS_KEY_ID`

- `AWS_SECRET_ACCESS_KEY`

These variables are then used in the TechDocs plugin configuration.

<div>

::: title
Prerequisites
:::

- You have installed Red Hat Developer Hub on OpenShift Container
  Platform using the Operator.

- You have created an `ObjectBucketClaim` CR for storing files generated
  by TechDocs.

</div>

<div>

::: title
Procedure
:::

- In your `Backstage` CR, enter the name of the Developer Hub
  `ObjectBucketClaim` config map as the value for the
  `spec.application.extraEnvs.configMaps` field and enter the Developer
  Hub `ObjectBucketClaim` secret name as the value for the
  `spec.application.extraEnvs.secrets` field. For example:

  ``` yaml
  apiVersion: objectbucket.io/v1alpha1
  kind: Backstage
  metadata:
   name: <name>
  spec:
    application:
      extraEnvs:
        configMaps:
          - name: <rhdh_bucket_claim_name>
        secrets:
          - name: <rhdh_bucket_claim_name>
  ```

</div>

##### Example TechDocs Plugin configuration for the Operator {#ref-techdocs-example-config-plugin-operator_configuring-techdocs}

The following example shows a Red Hat Developer Hub Operator config map
configuration for the TechDocs plugin:

``` yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: dynamic-plugins-rhdh
data:
  dynamic-plugins.yaml: |
    includes:
      - dynamic-plugins.default.yaml
    plugins:
      - disabled: false
        package: ./dynamic-plugins/dist/backstage-plugin-techdocs-backend-dynamic
        pluginConfig:
          techdocs:
            builder: external
            generator:
              runIn: local
            publisher:
              awsS3:
                bucketName: '${BUCKET_NAME}'
                credentials:
                  accessKeyId: '${AWS_ACCESS_KEY_ID}'
                  secretAccessKey: '${AWS_SECRET_ACCESS_KEY}'
                endpoint: 'https://${BUCKET_HOST}'
                region: '${BUCKET_REGION}'
                s3ForcePathStyle: true
              type: awsS3
```

### Configuring CI/CD to generate and publish TechDocs sites {#con-techdocs-config-cicd_configuring-techdocs}

TechDocs reads the static generated documentation files from a cloud
storage bucket, such as OpenShift Data Foundation. The documentation
site is generated on the CI/CD workflow associated with the repository
containing the documentation files. You can generate docs on CI and
publish to a cloud storage using the `techdocs-cli` CLI tool.

You can use the following example to create a script for TechDocs
publication:

``` shell
# Prepare
REPOSITORY_URL='https://github.com/org/repo'
git clone $REPOSITORY_URL
cd repo

# Install @techdocs/cli, mkdocs and mkdocs plugins
npm install -g @techdocs/cli
pip install "mkdocs-techdocs-core==1.*"

# Generate
techdocs-cli generate --no-docker

# Publish
techdocs-cli publish --publisher-type awsS3 --storage-name <bucket/container> --entity <Namespace/Kind/Name>
```

The TechDocs workflow starts the CI when a user makes changes in the
repository containing the documentation files. You can configure the
workflow to start only when files inside the `docs/` directory or
`mkdocs.yml` are changed.

#### Preparing your repository for CI {#proc-techdocs-config-cicd-prep-repo_configuring-techdocs}

The first step on the CI is to clone your documentation source
repository in a working directory.

<div>

::: title
Procedure
:::

- To clone your documentation source repository in a working directory,
  enter the following command:

  ``` terminal
  git clone <https://path/to/docs-repository/>
  ```

</div>

#### Generating the TechDocs site {#proc-techdocs-generate-site_configuring-techdocs}

:::: formalpara
::: title
Procedure
:::

To configure CI/CD to generate your techdocs, complete the following
steps:
::::

1.  Install the `npx` package to run `techdocs-cli` using the following
    command:

        npm install -g npx

2.  Install the `techdocs-cli` tool using the following command:

        npm install -g @techdocs/cli

3.  Install the `mkdocs` plugins using the following command:

        pip install "mkdocs-techdocs-core==1.*"

4.  Generate your techdocs site using the following command:

    ``` terminal
    npx @techdocs/cli generate --no-docker --source-dir <path_to_repo> --output-dir ./site
    ```

    Where `<path_to_repo>` is the location in the file path that you
    used to clone your repository.

#### Publishing the TechDocs site {#proc-techdocs-publish-site_configuring-techdocs}

:::: formalpara
::: title
Procedure
:::

To publish your techdocs site, complete the following steps:
::::

1.  Set the necessary authentication environment variables for your
    cloud storage provider.

2.  Publish your techdocs using the following command:

    ``` terminal
    npx @techdocs/cli publish --publisher-type <awsS3|googleGcs> --storage-name <bucket/container> --entity <namespace/kind/name> --directory ./site
    ```

3.  Add a `.github/workflows/techdocs.yml` file in your Software
    Template(s). For example:

    ``` yaml
    name: Publish TechDocs Site

    on:
     push:
       branches: [main]
       # You can even set it to run only when TechDocs related files are updated.
       # paths:
       #   - "docs/**"
       #   - "mkdocs.yml"

    jobs:
     publish-techdocs-site:
       runs-on: ubuntu-latest

       # The following secrets are required in your CI environment for publishing files to AWS S3.
       # e.g. You can use GitHub Organization secrets to set them for all existing and new repositories.
       env:
         TECHDOCS_S3_BUCKET_NAME: ${{ secrets.TECHDOCS_S3_BUCKET_NAME }}
         AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
         AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
         AWS_REGION: ${{ secrets.AWS_REGION }}
         ENTITY_NAMESPACE: 'default'
         ENTITY_KIND: 'Component'
         ENTITY_NAME: 'my-doc-entity'
         # In a Software template, Scaffolder will replace {{cookiecutter.component_id | jsonify}}
         # with the correct entity name. This is same as metadata.name in the entity's catalog-info.yaml
         # ENTITY_NAME: '{{ cookiecutter.component_id | jsonify }}'

       steps:
         - name: Checkout code
           uses: actions/checkout@v3

         - uses: actions/setup-node@v3
         - uses: actions/setup-python@v4
           with:
             python-version: '3.9'

         - name: Install techdocs-cli
           run: sudo npm install -g @techdocs/cli

         - name: Install mkdocs and mkdocs plugins
           run: python -m pip install mkdocs-techdocs-core==1.*

         - name: Generate docs site
           run: techdocs-cli generate --no-docker --verbose

         - name: Publish docs site
           run: techdocs-cli publish --publisher-type awsS3 --storage-name $TECHDOCS_S3_BUCKET_NAME --entity $ENTITY_NAMESPACE/$ENTITY_KIND/$ENTITY_NAME
    ```

## Using TechDocs {#assembly-using-techdocs}

The TechDocs plugin is installed and enabled on your Red Hat Developer
Hub instance by default. After an administrator configures the TechDocs
plugin, an authorized developer can use the TechDocs plugin to add,
view, or manage documentation.

### Adding documentation to TechDocs {#assembly-techdocs-add-docs}

After an administrator configures the TechDocs plugin, a developer can
add documentation to TechDocs by importing it from a remote repository.
Any authorized user or group can access the documentation that is
imported into the TechDocs plugin.

#### Importing documentation into TechDocs from a remote repository {#proc-techdocs-add-docs-from-remote-repo_assembly-techdocs-add-docs}

Teams can store their documentation files in the same remote repository
where they store their code files. You can import documentation into
your TechDocs plugin from a remote repository that contains the
documentation files that your team uses.

<div>

::: title
Prerequisites
:::

- Your organization has documentation files stored in a remote
  repository.

- You have a `mkdocs.yaml` file in the root directory of your
  repository.

- You have the `catalog.entity.create` and `catalog.location.create`
  permissions to import documentation into TechDocs from a remote
  repository.

</div>

<div>

::: title
Procedure
:::

1.  In your Red Hat Developer Hub instance, click **Catalog \>
    Self-service \> Register Existing Component**.

2.  In the **Select URL** box, enter the URL to the `catalog-info.yaml`
    file that you want to import from your repository using the
    following format:

    `https://github.com/<project_name>/<repo_name>/blob/<branch_name>/<file_directory>/catalog-info.yaml`

3.  Click **Analyze**

4.  Click **Finish**

</div>

<div>

::: title
Verification
:::

1.  In the Red Hat Developer Hub navigation menu, click **Docs**.

2.  Verify that the documentation that you imported is listed in the
    table on the **Documentation** page.

</div>

### Finding documentation in TechDocs {#proc-techdocs-find-docs_assembly-techdocs-add-docs}

By default, the TechDocs plugin **Documentation** page shows all of the
documentation that your organization has imported into your Red Hat
Developer Hub instance. You can use any combination of the following
methods to find the documentation that you want to view:

- Enter a keyword in the search bar to see all documents that contain
  the keyword anywhere in the document.

- Filter by **Owner** to see only documents that are owned by a
  particular user or group in your organization.

- Filter by **Tags** to see only documents that contain a particular
  tag.

- Filter by **Owned** to see only documents that are owned by you or by
  a group that you belong

- Filter by **Starred** to see only documents that you have added to
  favorites.

By default, the **All** field shows the total number of documents that
have been imported into TechDocs. If you search or use filters, the
**All** field shows the number of documents that meet the search and
filter criteria that you applied.

<div>

::: title
Prerequisites
:::

- The TechDocs plugin in enabled and configured

- Documentation is imported into TechDocs

- You have the required roles and permissions to add and view
  documentation to TechDocs

</div>

<div>

::: title
Procedure
:::

1.  In the Red Hat Developer Hub navigation menu, click **Docs**.

2.  On the **Documentation** page, use the search bar, filters, or both
    to locate the document that you want to view.

</div>

### Viewing documentation in TechDocs {#proc-techdocs-view-docs_assembly-techdocs-add-docs}

In TechDocs, a document might be part of a book that contains other
documents that are related to the same topic.

Clicking the name of a document in the table on the **Documentation**
page opens the document in a book page. The name of the book is
displayed on book the page. The book page contains the following
elements:

- The contents of the document.

- A search bar that you can use to search for keywords within the
  document.

- A navigation menu that you can use to navigate to other documents in
  the book.

- A **Table of contents** that you can use to navigate to other sections
  of the document.

- A **Next** button that you can use to navigate to the next sequential
  document in the book.

You can use the elements on the book page to search, view, and navigate
the documentation in the book.

<div>

::: title
Prerequisites
:::

- The TechDocs plugin in enabled and configured

- Documentation is imported into TechDocs

- You have the required roles and permissions to add and view
  documentation to TechDocs

- Optional: TechDocs add-ons are installed and configured

</div>

<div>

::: title
Procedure
:::

1.  In the Red Hat Developer Hub navigation menu, click **Docs**.

2.  In the **Documentation** table, click the name of the document that
    you want to view.

3.  On the book page, you can do any of the following optional actions:

    - Use installed add-ons that extend the functionality of the default
      TechDocs plugin.

    - Use the search bar to find keywords within the document.

    - Use any of the following methods to navigate the documentation in
      the book:

      - Use the **Table of contents** to navigate the any section of the
        document.

      - Use the navigation menu to navigate to any document in the book.

      - Click **Next** to navigate to the next sequential document in
        the book.

</div>

<div>

::: title
Additional resources
:::

- [TechDocs add-ons](#techdocs-addon)

</div>

### Editing documentation in TechDocs {#proc-techdocs-edit-docs_assembly-techdocs-add-docs}

You can edit a document in your TechDocs plugin directly from the
document book page. Any authorized user in your organization can edit a
document regardless of whether or not they are the owner of the
document.

<div>

::: title
Procedure
:::

1.  In the Red Hat Developer Hub navigation menu, click **Docs**.

2.  In the **Documentation** table, click the name of the document that
    you want to edit.

3.  In the document, click the **Edit this page** icon to open the
    document in your remote repository.

4.  In your remote repository, edit the document as needed.

5.  Use the repository provider UI and your usual team processes to
    commit and merge your changes.

</div>

## TechDocs add-ons {#techdocs-addon}

TechDocs add-ons are dynamic plugins that extend the functionality of
the built-in TechDocs plugin. For example, you can use add-ons to report
documentation issues, change text size, or view images in overlay in
either the TechDocs Reader page or an Entity page.

The following table describes the TechDocs add-ons that are available
for Red Hat Developer Hub 1.6:

+-----------------+-----------------+-----------------+-----------------+
| TechDocs Add-on | Package/Plugin  | Description     | Type            |
+=================+=================+=================+=================+
| `<              | `bac            | Select a        | Preinstalled    |
| ReportIssue />` | kstage-plugin-t | portion of text |                 |
|                 | echdocs-module- | on a TechDocs   |                 |
|                 | addons-contrib` | page and open   |                 |
|                 |                 | an issue        |                 |
|                 |                 | against the     |                 |
|                 |                 | repository that |                 |
|                 |                 | contains the    |                 |
|                 |                 | documentation.  |                 |
|                 |                 | The issue       |                 |
|                 |                 | template is     |                 |
|                 |                 | automatically   |                 |
|                 |                 | populated with  |                 |
|                 |                 | the selected    |                 |
|                 |                 | text.           |                 |
+-----------------+-----------------+-----------------+-----------------+
| `<TextSize />`  | `bac            | Customize text  | External        |
|                 | kstage-plugin-t | size on         |                 |
|                 | echdocs-module- | documentation   |                 |
|                 | addons-contrib` | pages by        |                 |
|                 |                 | increasing or   |                 |
|                 |                 | decreasing the  |                 |
|                 |                 | font size with  |                 |
|                 |                 | a slider or     |                 |
|                 |                 | buttons. The    |                 |
|                 |                 | default value   |                 |
|                 |                 | for font size   |                 |
|                 |                 | is 100% and     |                 |
|                 |                 | this setting is |                 |
|                 |                 | kept in the     |                 |
|                 |                 | browser's local |                 |
|                 |                 | storage         |                 |
|                 |                 | whenever it is  |                 |
|                 |                 | changed.        |                 |
+-----------------+-----------------+-----------------+-----------------+
| `<LightBox />`  | `bac            | Open images in  | External        |
|                 | kstage-plugin-t | a light-box on  |                 |
|                 | echdocs-module- | documentation   |                 |
|                 | addons-contrib` | pages, to       |                 |
|                 |                 | navigate to     |                 |
|                 |                 | multiple images |                 |
|                 |                 | on a single     |                 |
|                 |                 | page. The image |                 |
|                 |                 | size of the     |                 |
|                 |                 | light-box image |                 |
|                 |                 | is the same as  |                 |
|                 |                 | the image size  |                 |
|                 |                 | on the document |                 |
|                 |                 | page. Clicking  |                 |
|                 |                 | the zoom icon   |                 |
|                 |                 | increases the   |                 |
|                 |                 | image size to   |                 |
|                 |                 | fit the screen. |                 |
+-----------------+-----------------+-----------------+-----------------+

: TechDocs Add-ons available in Red Hat Developer Hub

The `backstage-plugin-techdocs-module-addons-contrib` plugin package
exports both preinstalled and external add-ons supported by Red Hat to
the TechDocs plugin. This plugin package is preinstalled on Red Hat
Developer Hub and is enabled by default. If the plugin package is
disabled, all of the TechDocs add-ons exported by the package as also
disabled.

### Installing and configuring a TechDocs add-on {#techdocs-addon-installing}

TechDocs add-ons supported by Red Hat are exported to the TechDocs
plugin by the\`backstage-plugin-techdocs-module-addons-contrib\` plugin
package, which is preinstalled on Red Hat Developer Hub and enabled by
default. The `<ReportIssue />` add-on is part of the default
configuration of this plugin package and comes ready to use in the
TechDocs plugin.

You can install other supported TechDocs add-ons by configuring
the\`backstage-plugin-techdocs-module-addons-contrib\` plugin package in
the Red Hat Developer Hub ConfigMap or Helm chart, depending on whether
you use the Operator or Helm chart for installation. If you want to
customize your TechDocs experience beyond the functions of the supported
add-ons, you can install third-party add-ons on your TechDocs plugin,
including add-ons that you create yourself.

#### Installing and configuring an external TechDocs add-on using the Operator {#proc-techdocs-addon-install-operator_techdocs-addon-installing}

You can use a dynamic plugin to import TechDocs add-ons into your
TechDocs plugin. If you use the Red Hat Developer Hub Operator to
install the dynamic plugin, you can add TechDocs add-ons to the plugin
package in your ConfigMap.

Preinstalled add-ons, such as `ReportIssue`, are included in the default
`backstage-plugin-techdocs-module-addons-contrib` package configuration.
External add-ons that are supported by Red Hat are installed by manually
adding them to the `techdocsAddons` section of the configuration file.

<div>

::: title
Procedure
:::

1.  From the Developer perspective in the OpenShift Container Platform
    web console, click **ConfigMaps** \> **Create ConfigMap**.

2.  From the **Create ConfigMap** page, select the **YAML view** option
    in the **Configure via** field.

3.  In the newly created ConfigMap, add the default
    `backstage-plugin-techdocs-module-addons-contrib` package
    configuration. For example:

    ``` yaml
    kind: ConfigMap
    apiVersion: v1
    metadata:
      name: dynamic-plugins-rhdh
    data:
      dynamic-plugins.yaml: |
        includes:
          - dynamic-plugins.default.yaml
        plugins:
          - package: ./dynamic-plugins/dist/backstage-plugin-techdocs-module-addons-contrib
            disabled: false
            pluginConfig:
              dynamicPlugins:
                frontend:
                  backstage.plugin-techdocs-module-addons-contrib:
                    techdocsAddons:
                      - importName: ReportIssue
    ```

4.  In the `techdocsAddons` section of the ConfigMap, add
    `importName: <external_techdocs_add-on>` for each external TechDocs
    add-on that you want to add from the specified plugin package. For
    example:

    ``` yaml
    kind: ConfigMap
    apiVersion: v1
    metadata:
      name: dynamic-plugins-rhdh
    data:
      dynamic-plugins.yaml: |
        includes:
          - dynamic-plugins.default.yaml
        plugins:
          - package: ./dynamic-plugins/dist/backstage-plugin-techdocs-module-addons-contrib
            disabled: false
            pluginConfig:
              dynamicPlugins:
                frontend:
                  backstage.plugin-techdocs-module-addons-contrib:
                    techdocsAddons:
                      - importName: ReportIssue
                      - importName: <external_techdocs_add-on>
    ```

    where:

    *\<external_techdocs_add-on\>*

    :   Specifies the external TechDocs add-on that you want to install,
        for example, `TextSize` or `LightBox`.

5.  Click **Create**.

6.  In the web console navigation menu, click **Topology**.

7.  Click on the overflow menu for the Red Hat Developer Hub instance
    that you want to use and select **Edit Backstage** to load the YAML
    view of the Red Hat Developer Hub instance.

8.  In your `Backstage` CR, add the
    `dynamicPluginsConfigMapName: <dynamic_plugins_configmap>` key-value
    pair. For example:

    ``` yaml
    apiVersion: rhdh.redhat.com/v1alpha3
    kind: Backstage
    metadata:
      name: my-rhdh
    spec:
      application:
    # ...
        dynamicPluginsConfigMapName: _<dynamic_plugins_configmap>_
    # ...
    ```

    where:

    *\<dynamic_plugins_configmap\>*

    :   Specifies the name of your dynamic plugins ConfigMap for your
        Red Hat Developer Hub instance, for example,
        `dynamic-plugins-rhdh`.

9.  Click **Save**.

10. In the web console navigation menu, click **Topology** and wait for
    the Red Hat Developer Hub pod to start.

11. Click the **Open URL** icon to start using the Red Hat Developer Hub
    platform with the new configuration changes.

</div>

#### Installing and configuring an external TechDocs add-on using the Helm chart {#proc-techdocs-addon-install-helm_techdocs-addon-installing}

You can use a dynamic plugin to import TechDocs add-ons into your
TechDocs plugin. If you use the Red Hat Developer Hub Helm chart to
install the dynamic plugin, you can add TechDocs add-ons to the plugin
package in your Helm chart.

Preinstalled add-ons, such as `ReportIssue`, are included in the default
`backstage-plugin-techdocs-module-addons-contrib` package configuration.
External add-ons that are supported by Red Hat are installed by manually
adding them to the `techdocsAddons` section of the configuration file.

<div>

::: title
Prerequisites
:::

- The TechDocs plugin is installed and enabled.

</div>

<div>

::: title
Procedure
:::

1.  In your Helm chart, add the `global.dynamic` parameters required to
    install a dynamic plugin, as shown in [Installing dynamic plugins
    using the Helm chart
    ](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_and_viewing_plugins_in_red_hat_developer_hub/rhdh-installing-rhdh-plugins_title-plugins-rhdh-about#con-install-dynamic-plugin-helm_rhdh-installing-rhdh-plugins)

    :::: note
    ::: title
    :::

    The default configuration includes the
    `dynamic-plugins.default.yaml` file, which contains all of the
    dynamic plugins, including TechDocs add-ons, that are preinstalled
    in Red Hat Developer Hub, whether they are enabled or disabled by
    default.
    ::::

2.  In your Helm chart, add the default
    `backstage-plugin-techdocs-module-addons-contrib` package
    configuration. For example:

    ``` yaml
    global:
      dynamic:
        plugins:
          - package: ./dynamic-plugins/dist/backstage-plugin-techdocs-module-addons-contrib
            disabled: false
            pluginConfig:
              dynamicPlugins:
                frontend:
                  backstage.plugin-techdocs-module-addons-contrib:
                    techdocsAddons:
                      - importName: ReportIssue
    ```

3.  In the `techdocsAddons` section of the Helm chart, add
    `importName: <external_techdocs_add-on>` for each external TechDocs
    add-on that you want to add from the specified plugin package. For
    example:

    ``` yaml
    global:
      dynamic:
        plugins:
          - package: ./dynamic-plugins/dist/backstage-plugin-techdocs-module-addons-contrib
            disabled: false
            pluginConfig:
              dynamicPlugins:
                frontend:
                  backstage.plugin-techdocs-module-addons-contrib:
                    techdocsAddons:
                      - importName: ReportIssue
                      - importName: <external_techdocs_add-on>
    ```

    where:

    *\<external_techdocs_add-on\>*

    :   Specifies the external TechDocs add-on that you want to install,
        for example, `TextSize` or `LightBox`.

</div>

#### Installing and configuring a third-party TechDocs add-on {#proc-techdocs-addon-install-third-party_techdocs-addon-installing}

You can install compatible third-party TechDocs add-on on your Red Hat
Developer Hub instance as a front-end dynamic plugin.

<div>

::: title
Prerequisites
:::

- The third-party TechDocs add-on has a valid `package.json` file in its
  root directory, containing all required metadata and dependencies.

- The third-party plugin is packaged as a dynamic plugin in an OCI
  image. For alternative package types, see [Installing third-party
  plugins in Red Hat Developer
  Hub](https://redhat-developer.github.io/red-hat-developers-documentation-rhdh/release-1.5/plugins-rhdh-install/#assembly-install-third-party-plugins-rhdh).

- You have installed the `yarn` package manager.

- The third-party plugin is packaged as a dynamic plugin in an OCI
  image.\* You have installed and configured Node.js and NPM.

</div>

<div>

::: title
Procedure
:::

1.  Install the third-party plugin that you want to use to import your
    third-party add-on by entering the following command:

    ``` terminal
    yarn install
    ```

2.  Obtain the source code for the third-party TechDocs add-on that you
    want to use.

3.  Export the TechDocs add-on as a dynamic plugin using the following
    command:

    ``` terminal
    npx @janus-idp/cli@latest package export-dynamic-plugin
    ```

    :::: note
    ::: title
    :::

    The `@latest` tag pulls the latest version of the \@janus-idp/cli
    package, which is compatible with the most recent features and
    fixes. Use a version that is compatible with your Red Hat Developer
    Hub version.
    ::::

4.  To package the third-party TechDocs add-on as a dynamic plugin,
    navigate to the root directory where the plugin is stored (not the
    dist-dynamic directory) and run the `npx` command with the `--tag`
    option to specify the image name and tag. For example:

    ``` terminal
    npx @janus-idp/cli@latest package package-dynamic-plugins --tag quay.io/<user_name>/<techdocs_add-on_image>:latest
    ```

    :::: note
    ::: title
    :::

    The output of the package-dynamic-plugins command provides the file
    path to the plugin for use in the `dynamic-plugin-config.yaml` file.
    ::::

5.  To publish the third-party TechDocs add-on to a Quay repository,
    push the image to a registry using one of the following commands,
    depending on your virtualization tool:

    - To use `podman`, enter the following command:

      ``` terminal
      podman push quay.io/<user_name>/<techdocs_add-on_image>:latest
      ```

    - To use `docker`, enter the following command:

      ``` terminal
      docker push quay.io/<user_name>/<techdocs_add-on_image>:latest
      ```

6.  Open your `dynamic-plugins.yaml` file to view or modify the
    configuration for the third-party TechDocs add-on. For example:

    ``` yaml
    plugins:
          - package: oci://quay.io/<user_name>/<techdocs_add-on_image>:latest!<techdocs_add-on_package>
            disabled: false
            pluginConfig:
              dynamicPlugins:
                frontend:
                 <techdocs_add-on_package>
                    techdocsAddons:
                      - importName: <third-party_add-on_name>
                       config:
                          props:
                           <techdocs_add-on_property_key>: <techdocs_add-on_property_value>
    ```

    where

    *\<user_name\>*

    :   Specifies your Quay user name or organization name.

    *\<techdocs_add-on_image\>*

    :   Specifies the name of the image for the third-party add-on that
        you want to use, for example, `mermaid`.

    *\<techdocs_add-on_package\>*

    :   Specifies the , for example,
        `backstage-plugin-techdocs-addon-mermaid`.

    *\<third-party_add-on_name\>*

    :   Specifies the name of the third-party add-on that you want to
        use, for example, `Mermaid`.

    *\<techdocs_add-on_property_key\>*

    :   Specifies the name of the custom property that can be passed to
        the third-party add-on, for example, `themeVariables`.
        Properties are specific to each add-on. You can list multiple
        properties for an add-on.

    *\<techdocs_add-on_property_value\>*

    :   Specifies the value of a property key for the third-party
        add-on, for example, `lineColor: #000000`.

</div>

<div>

::: title
Additional resources
:::

- [Installing dynamic plugins in Red Hat Developer
  Hub](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_and_viewing_plugins_in_red_hat_developer_hub/rhdh-installing-rhdh-plugins_title-plugins-rhdh-about)

- [Third-party plugins in Red Hat Developer
  Hub](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_and_viewing_plugins_in_red_hat_developer_hub/assembly-third-party-plugins)

</div>

### Removing a TechDocs add-on {#techdocs-addon-removing}

Administrators can remove installed TechDocs add-ons from your Red Hat
Developer Hub instance by using either the Operator or Helm chart,
depending on the method used to install the add-on. If you used the
Operator to install the add-on, remove it from the ConfigMap. If you
used the Helm chart to install the add-on, remove it from the Helm
chart.

If you want to disable a plugin instead of removing it from your Red Hat
Developer Hub instance, you can disable the plugin that you are using to
import the TechDocs add-on. Since the `disabled` status is controlled at
the plugin level, disabling the plugin disables all of the TechDocs
add-ons in the specified plugin package.

#### Removing an external TechDocs add-on from your ConfigMap {#proc-techdocs-addon-remove-operator_techdocs-addon-removing}

If you no longer want to use the functionality of a TechDocs add-on that
is imported from a particular plugin that you installed on your Red Hat
Developer Hub instance with the Operator, you can temporarily disable it
or permanently remove it from your ConfigMap. The `disabled` status is
controlled at the plugin level, therefore, disabling the plugin disables
all of the TechDocs add-ons in the disabled plugin package.

<div>

::: title
Procedure
:::

1.  From the Developer perspective in the OpenShift Container Platform
    web console, click **ConfigMaps**.

2.  From the **ConfigMaps** page, click the ConfigMap that contains the
    TechDocs add-on that you want to remove.

3.  Select the **YAML view** option in the **Configure via** field.

4.  In the `plugins` section of the ConfigMap, do one of the following
    actions based on whether you want to disable or remove a TechDocs
    add-on:

    - To temporarily disable all of the TechDocs add-ons in a particular
      plugin package, change the value of the `disabled` field to
      `true`. For example:

      ``` yaml
      kind: ConfigMap
      apiVersion: v1
      metadata:
        name: dynamic-plugins-rhdh
      data:
        dynamic-plugins.yaml: |
          includes:
            - dynamic-plugins.default.yaml
          plugins:
            - package: ./dynamic-plugins/dist/backstage-plugin-techdocs-module-addons-contrib
              disabled: true
              pluginConfig:
                dynamicPlugins:
                  frontend:
                    backstage.plugin-techdocs-module-addons-contrib:
                      techdocsAddons:
                        - importName: ReportIssue
                        - importName: <external_techdocs_add-on>
      ```

      where:

      *\<external_techdocs_add-on\>*

      :   Specifies the external TechDocs add-on that you want to
          remove, for example, `TextSize`.

    - To remove one or more TechDocs add-ons from your Red Hat Developer
      Hub instance, delete `importName: <external_techdocs_add-on>` for
      each external TechDocs add-on that you want to remove from the
      `techdocsAddons` section of your ConfigMap. For example:

      ``` yaml
      kind: ConfigMap
      apiVersion: v1
      metadata:
        name: dynamic-plugins-rhdh
      data:
        dynamic-plugins.yaml: |
          includes:
            - dynamic-plugins.default.yaml
          plugins:
            - package: ./dynamic-plugins/dist/backstage-plugin-techdocs-module-addons-contrib
              disabled: false
              pluginConfig:
                dynamicPlugins:
                  frontend:
                    backstage.plugin-techdocs-module-addons-contrib:
                      techdocsAddons:
                        - importName: ReportIssue
                        - importName: <external_techdocs_add-on>
      ```

      where:

      *\<external_techdocs_add-on\>*

      :   Specifies the external TechDocs add-on that you want to
          remove, for example, `TextSize`.

5.  Click **Save**.

6.  In the web console navigation menu, click **Topology** and wait for
    the Red Hat Developer Hub pod to start.

7.  Click the **Open URL** icon to start using the Red Hat Developer Hub
    platform with the new configuration changes.

</div>

#### Removing an external TechDocs add-on from your Helm chart {#proc-techdocs-addon-remove-helm_techdocs-addon-removing}

If you no longer want to use the functionality of a TechDocs add-on that
is imported from a particular plugin that you installed on your Red Hat
Developer Hub instance with the Helm chart, you can temporarily disable
it or permanently remove it from your Helm chart. The `disabled` status
is controlled at the plugin level, therefore, disabling the plugin
disables all of the TechDocs add-ons in the disabled plugin package.

<div>

::: title
Procedure
:::

- In the `plugins` section of the Helm chart, do one of the following
  actions based on whether you want to disable or remove a TechDocs
  add-on:

  - To temporarily disable all of the TechDocs add-ons in a particular
    plugin package, change the value of the `disabled` field to `true`.
    For example:

    ``` yaml
    global:
      dynamic:
        plugins:
          - package: ./dynamic-plugins/dist/backstage-plugin-techdocs-module-addons-contrib
            disabled: true
            pluginConfig:
              dynamicPlugins:
                frontend:
                  backstage.plugin-techdocs-module-addons-contrib:
                    techdocsAddons:
                      - importName: ReportIssue
                      - importName: <external_techdocs_add-on>
    ```

    where:

    *\<external_techdocs_add-on\>*

    :   Specifies the external TechDocs add-on that you want to remove,
        for example, `TextSize`.

  - To remove one or more TechDocs add-ons from your Red Hat Developer
    Hub instance, delete `importName: <external_techdocs_add-on>` for
    each external TechDocs add-on that you want to remove from the
    `techdocsAddons` section of your Helm chart. For example:

    ``` yaml
    global:
      dynamic:
        plugins:
          - package: ./dynamic-plugins/dist/backstage-plugin-techdocs-module-addons-contrib
            disabled: false
            pluginConfig:
              dynamicPlugins:
                frontend:
                  backstage.plugin-techdocs-module-addons-contrib:
                    techdocsAddons:
                      - importName: ReportIssue
                      - importName: <external_techdocs_add-on>
    ```

    where:

    *\<external_techdocs_add-on\>*

    :   Specifies the external TechDocs add-on that you want to remove,
        for example, `TextSize`.

</div>

### Using TechDocs add-ons {#techdocs-addon-using}

After an administrator installs a TechDocs add-on in your Red Hat
Developer Hub instance, you can use it to extend the functionality of
the TechDocs plugin and enhance your documentation experience.

#### Using the ReportIssue TechDocs add-on {#proc-techdocs-addon-use-report-issue_techdocs-addon-using}

If you find an error in your organization's TechDocs documentation, you
can use the `ReportIssue` add-on to open a new GitHub or GitLab issue
directly from the documentation. `ReportIssue` automatically imports the
text that you highlight in the document into a new issue template in
your repository.

<div>

::: title
Prerequisites
:::

- The `ReportIssue` add-on is installed and enabled in your TechDocs
  plugin.

- You have permissions to create issues in the repository where
  documentation issues are reported.

</div>

<div>

::: title
Procedure
:::

1.  In your TechDocs documentation, highlight the text that you want to
    report an issue for.

2.  Click the text in the `ReportIssue` box, for example, **Open new
    GitHub issue**.

3.  From the new issue page in your repository, use the template to
    create the issue that you want to report.

    :::: note
    ::: title
    :::

    The default issue title is **Documentation feedback:
    *\<highlighted_text\>***, where *\<highlighted_text\>* is the text
    that you highlighted in your TechDocs documentation.

    In the issue description, *\<highlighted_text\>* is the default
    value for the **The highlighted text** field.
    ::::

</div>

<div>

::: title
Verification
:::

- The issue that you created is listed on the issues page in your
  repository.

</div>

#### Using the TextSize TechDocs add-on {#proc-techdocs-addon-use-text-size_techdocs-addon-using}

You can use the `TextSize` add-on to change the size of the text on
either the TechDocs Reader page or an Entity page.

<div>

::: title
Prerequisites
:::

- The `TextSize` add-on is installed and enabled in your TechDocs
  plugin.

</div>

<div>

::: title
Procedure
:::

1.  In your TechDocs header, click the **Settings** icon.

2.  Use the sliding scale to adjust the size of your documentation text.

    :::: note
    ::: title
    :::

    - The default text size is 100%

    - The minimize text size is 90%

    - The maximum text size is 150%
    ::::

</div>

#### Using the LightBox TechDocs add-on {#proc-techdocs-addon-use-light-box_techdocs-addon-using}

If your TechDocs documentation contains an image, you can use the
`LightBox` add-on to view an enlarged version of the image in a
lightbox, or overlay window. You can also zoom to change the size the
lightbox image. If a single documentation page contains multiple images,
you can navigate between images in the lightbox.

<div>

::: title
Prerequisites
:::

- The `LightBox` add-on is installed and enabled in your TechDocs
  plugin.

</div>

<div>

::: title
Procedure
:::

1.  In your TechDocs documentation, click on the image that you want to
    view in a lightbox.

2.  In the lightbox, you can do any of the following actions:

    - Click the image or scroll to zoom in or zoom out.

    - Click the arrow to navigate between images.

</div>

### Creating a TechDocs add-on {#proc-techdocs-addon-create_techdocs-addon-using}

If your organization has documentation needs that are not met by the
functions of existing TechDocs add-ons, developers can create a new
add-on for your TechDocs plugin.

A TechDocs add-on is a React component that is imported from a front-end
plugin. If you do not have an existing plugin that you can use to export
your TechDocs add-on, you can create a new plugin by using
`backstage-cli` to generate a default front-end plugin structure that
you can customize.

The folder structure of a new plugin that can be used to import TechDocs
add-ons into the TechDocs plugin looks similar to the following example:

``` json
<new_plugin_for_techdocs_add-on>/
   dev/
       index.ts
   src/
       components/
         <new_techdocs_add-on_component>/
              <new_techdocs_add-on_component>.test.tsx
              <new_techdocs_add-on_component>.tsx
               index.ts
         <new_techdocs_add-on_fetch-component>/
              <new_techdocs_add-on_fetch-component>.test.tsx
              <new_techdocs_add-on_fetch-component>.tsx
               index.ts
       index.ts
       plugin.test.ts
       plugin.ts
       routes.ts
       setupTests.ts
   .eslintrc.js
   package.json
   README.md
```

<div>

::: title
Prerequisites
:::

- The `yarn` package manager is installed.

- Docker v3.2.0 or later or Podman v3.2.0 or later is installed and
  running.

</div>

<div>

::: title
Procedure
:::

1.  In the terminal, navigate to the root folder of the repository where
    you want to create your new plugin.

2.  To create a new front-end plugin, run the following command:

    ``` terminal
    yarn new
    ```

    :::: formalpara
    ::: title
    Example output
    :::

    ``` terminal
    ? What do you want to create? plugin - A new frontend plugin
    ? Enter the ID of the plugin [required]
    ```
    ::::

3.  In the terminal prompt, type a name for the new plugin. For example:

    ``` terminal
    ? Enter the ID of the plugin [required] <new_plugin_for_techdocs_add-on>
    ```

    :::: formalpara
    ::: title
    Example output
    :::

    ``` terminal
    Successfully created plugin
    ```
    ::::

    :::: formalpara
    ::: title
    Result
    :::

    In the `plugins` directory, a sub-directory with the same name that
    you gave to your plugin is automatically generated. The directory
    contains all of the files that you need to configure to create your
    new plugin.
    ::::

4.  In the terminal, navigate to your new plugin directory. For example:

    ``` terminal
    cd plugins/<new_techdocs_add-on_directory>
    ```

5.  Add the\`@backstage/plugin-techdocs-react\` package to get frontend
    utilities for TechDocs add-ons. For example:

    ``` terminal
    yarn add @backstage/plugin-techdocs-react
    ```

6.  In the directory containing the components of your custom TechDocs
    add-on, delete any default files or file components that are not
    required for your add-on, such as the `routes.ts` file or components
    of the `index.tsx` and `plugins.ts` files.

7.  In the `plugins.ts` file, add the following code:

    ``` java
    import { createPlugin } from '@backstage/core-plugin-api';
    import { createTechDocsAddonExtension } from '@backstage/plugin-techdocs-react';

    export const <new_plugin_for_techdocs_add-on> = createPlugin({
      id: '<new_techdocs_add-on>',
     });

     /*
     *
     * @public
     */
    export const <new_techdocs_add-on> = <new_plugin_for_techdocs_add-on>.provide(
     createTechDocsAddonExtension<_<new_techdocs_addon_props>_>({
        name: '<new_techdocs_add-on>',
        location: TechDocsAddonLocations.Content,
        component: <new_techdocs_add-on_component>,
      }),
    );
    ```

    where

    *\<new_plugin_for_techdocs_add-on\>*

    :   Specifies the new plugin that you use to import the TechDocs
        add-on to your Red Hat Developer Hub instance.

    *\<new_techdocs_add-on\>*

    :   Specifies the custom TechDocs add-on that you want to create.

    *\<new_techdocs_addon_props\>* (Optional)

    :   Specifies the `props` for your new TechDocs add-on, as specified
        in your `<new_techdocs_add-on>.tsx` file, if applicable.

    *\<new_techdocs_add-on_component\>*

    :   Specifies the React component for the custom TechDocs add-on
        that you want to create. You will create this component in a
        `.tsx` file in a later step.

8.  In the `index.ts` file, export the custom TechDocs add-on that you
    want to create by adding the following code:

    ``` java
    export { <new_plugin_for_techdocs_add-on>, <new_techdocs_add-on> } from './plugin';
    ```

9.  Create a new `<new_techdocs_add-on>.tsx` file and add the code for
    your new TechDocs add-on component.

10. Create a new `index.tsx` file and use it to export your new TechDocs
    add-on component by adding the following code:

    ``` java
    export { <new_techdocs_add-on>, type <new_techdocs_addon_props>} from './<new_techdocs_add-on_directory>'
    ```

    where

    *\<new_techdocs_addon_props\>* (Optional)

    :   Specifies the `props` for your new TechDocs add-on, as specified
        in your `<new_techdocs_add-on>.tsx` file, if applicable.

11. In the `plugins.ts` file, import your new TechDocs add-on component.

12. Install and configure your new TechDocs add-on by following the
    steps in [Installing and configuring a TechDocs
    add-on](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/techdocs_for_red_hat_developer_hub/index#techdocs-addon-installing)

</div>

<div>

::: title
Verification
:::

1.  Restart the RHDH application and verify that the plugin is
    successfully activated and configured.

2.  Verify the application logs for confirmation and ensure the plugin
    is functioning as expected.

</div>
