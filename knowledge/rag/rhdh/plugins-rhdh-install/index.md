## Installing dynamic plugins in Red Hat Developer Hub {#rhdh-installing-rhdh-plugins_title-plugins-rhdh-about}

The dynamic plugin support is based on the backend plugin manager
package, which is a service that scans a configured root directory
(`dynamicPlugins.rootDirectory` in the `app-config.yaml` file) for
dynamic plugin packages and loads them dynamically.

You can use the dynamic plugins that come preinstalled with Red Hat
Developer Hub or install external dynamic plugins from a public NPM
registry.

### Installing dynamic plugins with the Red Hat Developer Hub Operator {#proc-config-dynamic-plugins-rhdh-operator_rhdh-installing-rhdh-plugins}

You can store the configuration for dynamic plugins in a `ConfigMap`
object that your `Backstage` custom resource (CR) can reference.

:::: note
::: title
:::

If the `pluginConfig` field references environment variables, you must
define the variables in your `<my_product_secrets>` secret.
::::

<div>

::: title
Procedure
:::

1.  From the OpenShift Container Platform web console, select the
    **ConfigMaps** tab.

2.  Click **Create ConfigMap**.

3.  From the **Create ConfigMap** page, select the **YAML view** option
    in **Configure via** and edit the file, if needed.

    :::: formalpara
    ::: title
    Example `ConfigMap` object using the GitHub dynamic plugin
    :::

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
          - package: './dynamic-plugins/dist/backstage-plugin-catalog-backend-module-github-dynamic'
            disabled: false
            pluginConfig:
              catalog:
                providers:
                  github:
                    organization: "${GITHUB_ORG}"
                    schedule:
                      frequency: { minutes: 1 }
                      timeout: { minutes: 1 }
                      initialDelay: { seconds: 100 }
    ```
    ::::

4.  Click **Create**.

5.  Go to the **Topology** view.

6.  Click on the overflow menu for the Red Hat Developer Hub instance
    that you want to use and select **Edit Backstage** to load the YAML
    view of the Red Hat Developer Hub instance.

    ![operator install 2](images/rhdh/operator-install-2.png)

7.  Add the `dynamicPluginsConfigMapName` field to your `Backstage` CR.
    For example:

    ``` yaml
    apiVersion: rhdh.redhat.com/v1alpha3
    kind: Backstage
    metadata:
      name: my-rhdh
    spec:
      application:
    # ...
        dynamicPluginsConfigMapName: dynamic-plugins-rhdh
    # ...
    ```

8.  Click **Save**.

9.  Navigate back to the **Topology** view and wait for the Red Hat
    Developer Hub pod to start.

10. Click the **Open URL** icon to start using the Red Hat Developer Hub
    platform with the new configuration changes.

</div>

<div>

::: title
Verification
:::

- Ensure that the dynamic plugins configuration has been loaded, by
  appending `/api/dynamic-plugins-info/loaded-plugins` to your Red Hat
  Developer Hub root URL and checking the list of plugins:

  :::: formalpara
  ::: title
  Example list of plugins
  :::

  ``` json
  [
    {
      "name": "backstage-plugin-catalog-backend-module-github-dynamic",
      "version": "0.5.2",
      "platform": "node",
      "role": "backend-plugin-module"
    },
    {
      "name": "backstage-plugin-techdocs",
      "version": "1.10.0",
      "role": "frontend-plugin",
      "platform": "web"
    },
    {
      "name": "backstage-plugin-techdocs-backend-dynamic",
      "version": "1.9.5",
      "platform": "node",
      "role": "backend-plugin"
    },
  ]
  ```
  ::::

</div>

### Installing dynamic plugins using the Helm chart {#con-install-dynamic-plugin-helm_rhdh-installing-rhdh-plugins}

You can deploy a Developer Hub instance by using a Helm chart, which is
a flexible installation method. With the Helm chart, you can sideload
dynamic plugins into your Developer Hub instance without having to
recompile your code or rebuild the container.

To install dynamic plugins in Developer Hub using Helm, add the
following `global.dynamic` parameters in your Helm chart:

- `plugins`: the dynamic plugins list intended for installation. By
  default, the list is empty. You can populate the plugins list with the
  following fields:

  - `package`: a package specification for the dynamic plugin package
    that you want to install. You can use a package for either a local
    or an external dynamic plugin installation. For a local
    installation, use a path to the local folder containing the dynamic
    plugin. For an external installation, use a package specification
    from a public NPM repository.

  - `integrity` (required for external packages): an integrity checksum
    in the form of `<alg>-<digest>` specific to the package. Supported
    algorithms include `sha256`, `sha384` and `sha512`.

  - `pluginConfig`: an optional plugin-specific `app-config.yaml` YAML
    fragment. See plugin configuration for more information.

  - `disabled`: disables the dynamic plugin if set to `true`. Default:
    `false`.

  - `forceDownload`: Set the value to `true` to force a reinstall of the
    plugin, bypassing the cache. The default value is `false`.

  - `pullPolicy`: Similar to the `forceDownload` parameter and is
    consistent with other image container platforms. You can use one of
    the following values for this key:

    - `Always`: This value compares the image digest in the remote
      registry and downloads the artifact if it has changed, even if the
      plugin was previously downloaded.

    - `IfNotPresent`: This value downloads the artifact if it is not
      already present in the dynamic-plugins-root folder, without
      checking image digests.

      :::: note
      ::: title
      :::

      The `pullPolicy` setting is also applied to the NPM downloading
      method, although `Always` will download the remote artifact
      without a digest check. The existing `forceDownload` option
      remains functional, however, the `pullPolicy` option takes
      precedence. The `forceDownload` option may be deprecated in a
      future Developer Hub release.
      ::::

- `includes`: a list of YAML files utilizing the same syntax.

:::: note
::: title
:::

The `plugins` list in the `includes` file is merged with the `plugins`
list in the main Helm values. If a plugin package is mentioned in both
`plugins` lists, the `plugins` fields in the main Helm values override
the `plugins` fields in the `includes` file. The default configuration
includes the `dynamic-plugins.default.yaml` file, which contains all of
the dynamic plugins preinstalled in Developer Hub, whether enabled or
disabled by default.
::::

#### Example Helm chart configurations for dynamic plugin installations {#ref-example-dynamic-plugin-helm-installations}

The following examples demonstrate how to configure the Helm chart for
specific types of dynamic plugin installations.

:::: formalpara
::: title
Configuring a local plugin and an external plugin when the external
plugin requires a specific configuration
:::

``` yaml
global:
  dynamic:
    plugins:
      - package: <alocal package-spec used by npm pack>
      - package: <external package-spec used by npm pack>
        integrity: sha512-<some hash>
        pluginConfig: ...
```
::::

:::: formalpara
::: title
Disabling a plugin from an included file
:::

``` yaml
global:
  dynamic:
    includes:
      - dynamic-plugins.default.yaml
    plugins:
      - package: <some imported plugins listed in dynamic-plugins.default.yaml>
        disabled: true
```
::::

:::: formalpara
::: title
Enabling a plugin from an included file
:::

``` yaml
global:
  dynamic:
    includes:
      - dynamic-plugins.default.yaml
    plugins:
      - package: <some imported plugins listed in dynamic-plugins.custom.yaml>
        disabled: false
```
::::

:::: formalpara
::: title
Enabling a plugin that is disabled in an included file
:::

``` yaml
global:
  dynamic:
    includes:
      - dynamic-plugins.default.yaml
    plugins:
      - package: <some imported plugins listed in dynamic-plugins.custom.yaml>
        disabled: false
```
::::

### Installing dynamic plugins in an air-gapped environment {#proc-install-plugins-using-custom-npm-registry}

You can install external plugins in an air-gapped environment by setting
up a custom NPM registry.

You can configure the NPM registry URL and authentication information
for dynamic plugin packages using a Helm chart. For dynamic plugin
packages obtained through `npm pack`, you can use a `.npmrc` file.

Using the Helm chart, add the `.npmrc` file to the NPM registry by
creating a secret. For example:

``` yaml
apiVersion: v1
kind: Secret
metadata:
  name: <release_name>-dynamic-plugins-npmrc
type: Opaque
stringData:
  .npmrc: |
    registry=<registry-url>
    //<registry-url>:_authToken=<auth-token>
          ...
```

- Replace `<release_name>` with your Helm release name. This name is a
  unique identifier for each chart installation in the Kubernetes
  cluster.

## Third-party plugins in Red Hat Developer Hub {#assembly-third-party-plugins}

You can integrate third-party dynamic plugins into Red Hat Developer Hub
to enhance its functionality without modifying its source code or
rebuilding it. To add these plugins, export them as derived packages.

While exporting the plugin package, you must ensure that dependencies
are correctly bundled or marked as shared, depending on their
relationship to the Developer Hub environment.

To integrate a third-party plugin into Developer Hub:

1.  First, obtain the plugin's source code.

2.  Export the plugin as a dynamic plugin package. See [Exporting
    third-party plugins in Red Hat Developer
    Hub](#proc-export-third-party-plugins-rhdh_assembly-third-party-plugins).

3.  Package and publish the dynamic plugin. See [Packaging and
    publishing third-party plugins as dynamic
    plugins](#assembly-package-publish-third-party-dynamic-plugin).

4.  Install the plugin in the Developer Hub environment. See [Installing
    third-party plugins in Red Hat Developer
    Hub](#assembly-install-third-party-plugins-rhdh).

### Exporting third-party plugins in Red Hat Developer Hub {#proc-export-third-party-plugins-rhdh_assembly-third-party-plugins}

To use plugins in Red Hat Developer Hub, you can export plugins as
derived dynamic plugin packages. These packages contain the plugin code
and dependencies, ready for dynamic plugin integration into Developer
Hub.

<div>

::: title
Prerequisites
:::

- The `@janus-idp/cli` package is installed. Use the latest version
  (`@latest` tag) for compatibility with the most recent features and
  fixes.

- Node.js and NPM is installed and configured.

- The third-party plugin is compatible with your Red Hat Developer Hub
  version. For more information, see [Version compatibility
  matrix](https://github.com/redhat-developer/rhdh/blob/main/docs/dynamic-plugins/versions.md).

- The third-party plugin must have a valid `package.json` file in its
  root directory, containing all required metadata and dependencies.

  Backend plugins

  :   To ensure compatibility with the dynamic plugin support and enable
      their use as dynamic plugins, existing backend plugins must be
      compatible with the new Backstage backend system. Additionally,
      these plugins must be rebuilt using a dedicated CLI command.

      The new Backstage backend system entry point (created using
      `createBackendPlugin()` or `createBackendModule()`) must be
      exported as the default export from either the main package or an
      `alpha` package (if the plugin instance support is still provided
      using `alpha` APIs). This doesn't add any additional requirement
      on top of the standard plugin development guidelines of the plugin
      instance.

      The dynamic export mechanism identifies private dependencies and
      sets the `bundleDependencies` field in the `package.json` file.
      This export mechanism ensures that the dynamic plugin package is
      published as a self-contained package, with its private
      dependencies bundled in a private `node_modules` folder.

      Certain plugin dependencies require specific handling in the
      derived packages, such as:

      - **Shared dependencies** are provided by the RHDH application and
        listed as `peerDependencies` in `package.json` file, not bundled
        in the dynamic plugin package. For example, by default, all
        `@backstage` scoped packages are shared.

        You can use the `--shared-package` flag to specify shared
        dependencies, that are expected to be provided by Red Hat
        Developer Hub application and not bundled in the dynamic plugin
        package.

        To treat a `@backstage` package as private, use the negation
        prefix (`!`). For example, when a plugin depends on the package
        in `@backstage` that is not provided by the Red Hat Developer
        Hub application.

      - **Embedded dependencies** are bundled into the dynamic plugin
        package with their dependencies hoisted to the top level. By
        default, packages with `-node` or `-common` suffixes are
        embedded.

        You can use the `--embed-package` flag to specify additional
        embedded packages. For example, packages from the same workspace
        that do not follow the default naming convention.

        The following is an example of exporting a dynamic plugin with
        shared and embedded packages:

        :::: formalpara
        ::: title
        Example dynamic plugin export with shared and embedded packages
        :::

        ``` terminal
        npx @janus-idp/cli@latest export-dynamic-plugin --shared-package '!/@backstage/plugin-notifications/' --embed-package @backstage/plugin-notifications-backend
        ```
        ::::

        In the previous example:

      - `@backstage/plugin-notifications` package is treated as a
        private dependency and is bundled in the dynamic plugin package,
        despite being in the `@backstage` scope.

      - `@backstage/plugin-notifications-backend` package is marked as
        an embedded dependency and is bundled in the dynamic plugin
        package.

  Front-end plugins

  :   Front-end plugins can use `scalprum` for configuration, which the
      CLI can generate automatically during the export process. The
      generated default configuration is logged when running the
      following command:

      :::: formalpara
      ::: title
      Example command to log the default configuration
      :::

      ``` terminal
      npx @janus-idp/cli@latest export-dynamic
      ```
      ::::

      The following is an example of default `scalprum` configuration:

      :::: formalpara
      ::: title
      Default `scalprum` configuration
      :::

      ``` json
      "scalprum": {
        "name": "<package_name>",  // The Webpack container name matches the NPM package name, with "@" replaced by "." and "/" removed.
        "exposedModules": {
          "PluginRoot": "./src/index.ts"  // The default module name is "PluginRoot" and doesn't need explicit specification in the app-config.yaml file.
        }
      }
      ```
      ::::

      You can add a `scalprum` section to the `package.json` file. For
      example:

      :::: formalpara
      ::: title
      Example `scalprum` customization
      :::

      ``` json
      "scalprum": {
        "name": "custom-package-name",
        "exposedModules": {
          "FooModuleName": "./src/foo.ts",
          "BarModuleName": "./src/bar.ts"
          // Define multiple modules here, with each exposed as a separate entry point in the Webpack container.
        }
      }
      ```
      ::::

      Dynamic plugins might need adjustments for Developer Hub needs,
      such as static JSX for mountpoints or dynamic routes. These
      changes are optional but might be incompatible with static
      plugins.

      To include static JSX, define an additional export and use it as
      the dynamic plugin's `importName`. For example:

      :::: formalpara
      ::: title
      Example static and dynamic plugin export
      :::

      ``` tsx
      // For a static plugin
      export const EntityTechdocsContent = () => {...}

      // For a dynamic plugin
      export const DynamicEntityTechdocsContent = {
        element: EntityTechdocsContent,
        staticJSXContent: (
          <TechDocsAddons>
            <ReportIssue />
          </TechDocsAddons>
        ),
      };
      ```
      ::::

</div>

<div>

::: title
Procedure
:::

- Use the `package export-dynamic-plugin` command from the
  `@janus-idp/cli` package to export the plugin:

  :::: formalpara
  ::: title
  Example command to export a third-party plugin
  :::

  ``` terminal
  npx @janus-idp/cli@latest package export-dynamic-plugin
  ```
  ::::

  Ensure that you execute the previous command in the root directory of
  the plugin's JavaScript package (containing `package.json` file).

  The resulting derived package will be located in the `dist-dynamic`
  subfolder. The exported package name consists of the original plugin
  name with `-dynamic` appended.

  :::: warning
  ::: title
  :::

  The derived dynamic plugin JavaScript packages must not be published
  to the public NPM registry. For more appropriate packaging options,
  see [Packaging and publishing third-party plugins as dynamic
  plugins](#assembly-package-publish-third-party-dynamic-plugin). If you
  must publish to the NPM registry, use a private registry.
  ::::

</div>

### Packaging and publishing third-party plugins as dynamic plugins {#assembly-package-publish-third-party-dynamic-plugin}

After [exporting a third-party
plugin](#proc-export-third-party-plugins-rhdh_assembly-third-party-plugins),
you can package the derived package into one of the following supported
formats:

- Open Container Initiative (OCI) image (recommended)

- TGZ file

- JavaScript package

  :::: important
  ::: title
  :::

  Exported dynamic plugin packages must only be published to private NPM
  registries.
  ::::

#### Creating an OCI image with dynamic packages {#proc-create-plugin-oci-image_assembly-package-publish-third-party-dynamic-plugin}

<div>

::: title
Prerequisites
:::

- You have installed `podman` or `docker`.

- You have exported a third-party dynamic plugin package. For more
  information, see [Exporting third-party plugins in Red Hat Developer
  Hub](#proc-export-third-party-plugins-rhdh_assembly-third-party-plugins).

</div>

<div>

::: title
Procedure
:::

1.  Navigate to the plugin's root directory (not the `dist-dynamic`
    directory).

2.  Run the following command to package the plugin into an OCI image:

    :::: formalpara
    ::: title
    Example command to package an exported third-party plugin
    :::

    ``` terminal
    npx @janus-idp/cli@latest package package-dynamic-plugins --tag quay.io/example/image:v0.0.1
    ```
    ::::

    In the previous command, the `--tag` argument specifies the image
    name and tag.

3.  Run one of the following commands to push the image to a registry:

    :::: formalpara
    ::: title
    Example command to push an image to a registry using podman
    :::

    ``` terminal
    podman push quay.io/example/image:v0.0.1
    ```
    ::::

    :::: formalpara
    ::: title
    Example command to push an image to a registry using docker
    :::

    ``` terminal
    docker push quay.io/example/image:v0.0.1
    ```
    ::::

    The output of the `package-dynamic-plugins` command provides the
    plugin's path for use in the `dynamic-plugin-config.yaml` file.

</div>

#### Creating a TGZ file with dynamic packages {#proc-create-plugin-tgz-file_assembly-package-publish-third-party-dynamic-plugin}

<div>

::: title
Prerequisites
:::

- You have exported a third-party dynamic plugin package. For more
  information, see [Exporting third-party plugins in Red Hat Developer
  Hub](#proc-export-third-party-plugins-rhdh_assembly-third-party-plugins).

</div>

<div>

::: title
Procedure
:::

1.  Navigate to the `dist-dynamic` directory.

2.  Run the following command to create a `tgz` archive:

    :::: formalpara
    ::: title
    Example command to create a `tgz` archive
    :::

    ``` terminal
    npm pack
    ```
    ::::

    You can obtain the integrity hash from the output of the `npm pack`
    command by using the `--json` flag as follows:

    :::: formalpara
    ::: title
    Example command to obtain the integrity hash of a `tgz` archive
    :::

    ``` terminal
    npm pack --json | head -n 10
    ```
    ::::

3.  Host the archive on a web server accessible to your RHDH instance,
    and reference its URL in the `dynamic-plugin-config.yaml` file as
    follows:

    :::: formalpara
    ::: title
    Example `dynamic-plugin-config.yaml` file
    :::

    ``` yaml
    plugins:
      - package: https://example.com/backstage-plugin-myplugin-1.0.0.tgz
        integrity: sha512-<hash>
    ```
    ::::

4.  Run the following command to package the plugins:

    :::: formalpara
    ::: title
    Example command to package a dynamic plugin
    :::

    ``` terminal
    npm pack --pack-destination ~/test/dynamic-plugins-root/
    ```
    ::::

    :::::: tip
    ::: title
    :::

    To create a plugin registry using HTTP server on OpenShift Container
    Platform, run the following commands:

    :::: formalpara
    ::: title
    Example commands to build and deploy an HTTP server in OpenShift
    Container Platform
    :::

    ``` terminal
    oc project my-rhdh-project
    oc new-build httpd --name=plugin-registry --binary
    oc start-build plugin-registry --from-dir=dynamic-plugins-root --wait
    oc new-app --image-stream=plugin-registry
    ```
    ::::
    ::::::

5.  Configure your RHDH to use plugins from the HTTP server by editing
    the `dynamic-plugin-config.yaml` file:

    :::: formalpara
    ::: title
    Example configuration to use packaged plugins in RHDH
    :::

    ``` yaml
    plugins:
      - package: http://plugin-registry:8080/backstage-plugin-myplugin-1.9.6.tgz
    ```
    ::::

</div>

#### Creating a JavaScript package with dynamic packages {#proc-create-plugin-js-package_assembly-package-publish-third-party-dynamic-plugin}

:::: warning
::: title
:::

The derived dynamic plugin JavaScript packages must not be published to
the public NPM registry. If you must publish to the NPM registry, use a
private registry.
::::

<div>

::: title
Prerequisites
:::

- You have exported a third-party dynamic plugin package. For more
  information, see [Exporting third-party plugins in Red Hat Developer
  Hub](#proc-export-third-party-plugins-rhdh_assembly-third-party-plugins).

</div>

<div>

::: title
Procedure
:::

1.  Navigate to the `dist-dynamic` directory.

2.  Run the following command to publish the package to your private NPM
    registry:

    :::: formalpara
    ::: title
    Example command to publish a plugin package to an NPM registry
    :::

    ``` terminal
    npm publish --registry <npm_registry_url>
    ```
    ::::

    :::::: tip
    ::: title
    :::

    You can add the following to your `package.json` file before running
    the `export` command:

    :::: formalpara
    ::: title
    Example `package.json` file
    :::

    ``` json
    {
      "publishConfig": {
        "registry": "<npm_registry_url>"
      }
    }
    ```
    ::::

    If you modify `publishConfig` after exporting the dynamic plugin,
    re-run the `export-dynamic-plugin` command to ensure the correct
    configuration is included.
    ::::::

</div>

### Installing third-party plugins in Red Hat Developer Hub {#assembly-install-third-party-plugins-rhdh}

You can install a third-party plugins in Red Hat Developer Hub without
rebuilding the RHDH application.

The location of the `dynamic-plugin-config.yaml` file depends on the
deployment method. For more details, refer to [Installing dynamic
plugins with the Red Hat Developer Hub
Operator](#proc-config-dynamic-plugins-rhdh-operator_rhdh-installing-rhdh-plugins)
and [Installing dynamic plugins using the Helm
chart](#con-install-dynamic-plugin-helm_rhdh-installing-rhdh-plugins).

Plugins are defined in the `plugins` array within the
`dynamic-plugin-config.yaml` file. Each plugin is represented as an
object with the following properties:

- `package`: The plugin's package definition, which can be an OCI image,
  a TGZ file, a JavaScript package, or a directory path.

- `disabled`: A boolean value indicating whether the plugin is enabled
  or disabled.

- `integrity`: The integrity hash of the package, required for TGZ file
  and JavaScript packages.

- `pluginConfig`: The plugin's configuration. For backend plugins, this
  is optional; for frontend plugins, it is required. The `pluginConfig`
  is a fragment of the `app-config.yaml` file, and any added properties
  are merged with the RHDH `app-config.yaml` file.

:::: note
::: title
:::

You can also load dynamic plugins from another directory, though this is
intended for development or testing purposes and is not recommended for
production, except for plugins included in the RHDH container image. For
more information, see [Enabling plugins added in the RHDH container
image](#proc-enable-plugins-rhdh-container-image_assembly-install-third-party-plugins-rhdh).
::::

#### Loading a plugin packaged as an OCI image {#proc-load-plugin-oci-image_assembly-install-third-party-plugins-rhdh}

<div>

::: title
Prerequisites
:::

- The third-party plugin is packaged as a dynamic plugin in an OCI
  image.

  For more information about packaging a third-party plugin, see
  [Packaging and publishing third-party plugins as dynamic
  plugins](#assembly-package-publish-third-party-dynamic-plugin).

</div>

<div>

::: title
Procedure
:::

1.  Define the plugin with the `oci://` prefix in the following format
    in `dynamic-plugins.yaml` file:

    `oci://<image-name>:<tag>!<plugin-name>`

    :::: formalpara
    ::: title
    Example configuration in `dynamic-plugins.yaml` file
    :::

    ``` yaml
    plugins:
      - disabled: false
        package: oci://quay.io/example/image:v0.0.1!backstage-plugin-myplugin
    ```
    ::::

2.  Configure authentication for private registries by setting the
    `REGISTRY_AUTH_FILE` environment variable to the path of the
    registry configuration file. For example,
    `~/.config/containers/auth.json` or `~/.docker/config.json`.

3.  To perform an integrity check, use the image digest in place of the
    tag in the `dynamic-plugins.yaml` file as follows:

    :::: formalpara
    ::: title
    Example configuration in `dynamic-plugins.yaml` file
    :::

    ``` yaml
    plugins:
      - disabled: false
        package: oci://quay.io/example/image@sha256:28036abec4dffc714394e4ee433f16a59493db8017795049c831be41c02eb5dc!backstage-plugin-myplugin
    ```
    ::::

4.  To apply the changes, restart the RHDH application.

</div>

#### Loading a plugin packaged as a TGZ file {#proc-load-plugin-tgz-file_assembly-install-third-party-plugins-rhdh}

<div>

::: title
Prerequisites
:::

- The third-party plugin is packaged as a dynamic plugin in a TGZ file.

  For more information about packaging a third-party plugin, see
  [Packaging and publishing third-party plugins as dynamic
  plugins](#assembly-package-publish-third-party-dynamic-plugin).

</div>

<div>

::: title
Procedure
:::

1.  Specify the archive URL and its integrity hash in the
    `dynamic-plugins.yaml` file using the following example:

    :::: formalpara
    ::: title
    Example configuration in `dynamic-plugins.yaml` file
    :::

    ``` yaml
    plugins:
      - disabled: false
        package: https://example.com/backstage-plugin-myplugin-1.0.0.tgz
        integrity: sha512-9WlbgEdadJNeQxdn1973r5E4kNFvnT9GjLD627GWgrhCaxjCmxqdNW08cj+Bf47mwAtZMt1Ttyo+ZhDRDj9PoA==
    ```
    ::::

2.  To apply the changes, restart the RHDH application.

</div>

#### Loading a plugin packaged as a JavaScript package {#proc-load-plugin-js-package_assembly-install-third-party-plugins-rhdh}

<div>

::: title
Prerequisites
:::

- The third-party plugin is packaged as a dynamic plugin in a JavaScript
  package.

  For more information about packaging a third-party plugin, see
  [Packaging and publishing third-party plugins as dynamic
  plugins](#assembly-package-publish-third-party-dynamic-plugin).

</div>

<div>

::: title
Procedure
:::

1.  Run the following command to obtain the integrity hash from the NPM
    registry:

    ``` terminal
    npm view --registry <registry-url> <npm package>@<version> dist.integrity
    ```

2.  Specify the package name, version, and its integrity hash in the
    `dynamic-plugins.yaml` file as follows:

    :::: formalpara
    ::: title
    Example configuration in `dynamic-plugins.yaml` file
    :::

    ``` yaml
    plugins:
      - disabled: false
        package: @example/backstage-plugin-myplugin@1.0.0
        integrity: sha512-9WlbgEdadJNeQxdn1973r5E4kNFvnT9GjLD627GWgrhCaxjCmxqdNW08cj+Bf47mwAtZMt1Ttyo+ZhDRDj9PoA==
    ```
    ::::

3.  If you are using a custom NPM registry, create a `.npmrc` file with
    the registry URL and authentication details:

    :::: formalpara
    ::: title
    Example code for `.npmrc` file
    :::

    ``` text
    registry=<registry-url>
    //<registry-url>:_authToken=<auth-token>
    ```
    ::::

4.  When using OpenShift Container Platform or Kubernetes:

    - Use the Helm chart to add the `.npmrc` file by creating a secret.
      For example:

      :::: formalpara
      ::: title
      Example secret configuration
      :::

      ``` yaml
      apiVersion: v1
      kind: Secret
      metadata:
        name: <release_name>-dynamic-plugins-npmrc
      type: Opaque
      stringData:
        .npmrc: |
          registry=<registry-url>
          //<registry-url>:_authToken=<auth-token>
      ```
      ::::

      - Replace `<release_name>` with your Helm release name. This name
        is a unique identifier for each chart installation in the
        Kubernetes cluster.

    - For RHDH Helm chart, name the secret using the following format
      for automatic mounting:

      `<release_name>-dynamic-plugins-npmrc`

5.  To apply the changes, restart the RHDH application.

</div>

#### Example of installing a third-party plugin in Red Hat Developer Hub {#ref-example-third-party-plugin-installation_assembly-install-third-party-plugins-rhdh}

This section describes the process for integrating the [Todo
plugin](https://github.com/backstage/community-plugins/tree/main/workspaces/todo/plugins)
into your Developer Hub.

1.  **Obtain the third-party plugin source code**: Clone the plugins
    repository and navigate to the [Todo
    plugin](https://github.com/backstage/community-plugins/tree/main/workspaces/todo/plugins)
    directory:

    :::: formalpara
    ::: title
    Obtain the third-party plugin source code
    :::

    ``` terminal
    $ git clone https://github.com/backstage/community-plugins
    $ cd community-plugins/workspaces/todo
    $ yarn install
    ```
    ::::

2.  **Export backend and front-end plugins**: Run the following commands
    to build the backend plugin, adjust package dependencies for dynamic
    loading, and generate self-contained configuration schema:

    :::: formalpara
    ::: title
    Export the backend plugin
    :::

    ``` terminal
    $ cd todo-backend
    $ npx @janus-idp/cli@latest package export-dynamic-plugin
    ```
    ::::

    :::: formalpara
    ::: title
    Output of exporting the backend plugin commands
    :::

    ``` terminal
    Building main package
      executing     yarn build ✔
    Packing main package to dist-dynamic/package.json
    Customizing main package in dist-dynamic/package.json for dynamic loading
      moving @backstage/backend-common to peerDependencies
      moving @backstage/backend-openapi-utils to peerDependencies
      moving @backstage/backend-plugin-api to peerDependencies
      moving @backstage/catalog-client to peerDependencies
      moving @backstage/catalog-model to peerDependencies
      moving @backstage/config to peerDependencies
      moving @backstage/errors to peerDependencies
      moving @backstage/integration to peerDependencies
      moving @backstage/plugin-catalog-node to peerDependencies
    Installing private dependencies of the main package
       executing     yarn install --no-immutable ✔
    Validating private dependencies
    Validating plugin entry points
    Saving self-contained config schema in /Users/user/Code/community-plugins/workspaces/todo/plugins/todo-backend/dist-dynamic/dist/configSchema.json
    ```
    ::::

    You can run the following commands to set default dynamic UI
    configurations, create front-end plugin assets, and to generate a
    configuration schema for a front-end plugin:

    :::: formalpara
    ::: title
    Export the front-end plugin
    :::

    ``` terminal
    $ cd ../todo
    $ npx @janus-idp/cli@latest package export-dynamic-plugin
    ```
    ::::

    :::: formalpara
    ::: title
    Output of exporting the front-end plugin commands
    :::

    ``` terminal
    No scalprum config. Using default dynamic UI configuration:
    {
      "name": "backstage-community.plugin-todo",
      "exposedModules": {
        "PluginRoot": "./src/index.ts"
      }
    }
    If you wish to change the defaults, add "scalprum" configuration to plugin "package.json" file, or use the '--scalprum-config' option to specify an external config.
    Packing main package to dist-dynamic/package.json
    Customizing main package in dist-dynamic/package.json for dynamic loading
    Generating dynamic frontend plugin assets in /Users/user/Code/community-plugins/workspaces/todo/plugins/todo/dist-dynamic/dist-scalprum
      263.46 kB  dist-scalprum/static/1417.d5271413.chunk.js
    ...
    ...
    ...
      250 B      dist-scalprum/static/react-syntax-highlighter_languages_highlight_plaintext.0b7d6592.chunk.js
    Saving self-contained config schema in /Users/user/Code/community-plugins/workspaces/todo/plugins/todo/dist-dynamic/dist-scalprum/configSchema.json
    ```
    ::::

3.  **Package and publish a third-party plugin**: Run the following
    commands to navigate to the workspace directory and package the
    dynamic plugin to build the OCI image:

    :::: formalpara
    ::: title
    Build an OCI image
    :::

    ``` terminal
    $ cd ../..
    $ npx @janus-idp/cli@latest package package-dynamic-plugins --tag quay.io/user/backstage-community-plugin-todo:v0.1.1
    ```
    ::::

    :::: formalpara
    ::: title
    Output of building an OCI image commands
    :::

    ``` terminal
      executing     podman --version ✔
    Using existing 'dist-dynamic' directory at plugins/todo
    Using existing 'dist-dynamic' directory at plugins/todo-backend
    Copying 'plugins/todo/dist-dynamic' to '/var/folders/5c/67drc33d0018j6qgtzqpcsbw0000gn/T/package-dynamic-pluginsmcP4mU/backstage-community-plugin-todo
    No plugin configuration found at undefined create this file as needed if this plugin requires configuration
    Copying 'plugins/todo-backend/dist-dynamic' to '/var/folders/5c/67drc33d0018j6qgtzqpcsbw0000gn/T/package-dynamic-pluginsmcP4mU/backstage-community-plugin-todo-backend-dynamic
    No plugin configuration found at undefined create this file as needed if this plugin requires configuration
    Writing plugin registry metadata to '/var/folders/5c/67drc33d0018j6qgtzqpcsbw0000gn/T/package-dynamic-pluginsmcP4mU/index.json'
    Creating image using podman
      executing     echo "from scratch
    COPY . .
    " | podman build --annotation com.redhat.rhdh.plugins='[{"backstage-community-plugin-todo":{"name":"@backstage-community/plugin-todo","version":"0.2.40","description":"A Backstage plugin that lets you browse TODO comments in your source code","backstage":{"role":"frontend-plugin","pluginId":"todo","pluginPackages":["@backstage-community/plugin-todo","@backstage-community/plugin-todo-backend"]},"homepage":"https://backstage.io","repository":{"type":"git","url":"https://github.com/backstage/community-plugins","directory":"workspaces/todo/plugins/todo"},"license":"Apache-2.0"}},{"backstage-community-plugin-todo-backend-dynamic":{"name":"@backstage-community/plugin-todo-backend","version":"0.3.19","description":"A Backstage backend plugin that lets you browse TODO comments in your source code","backstage":{"role":"backend-plugin","pluginId":"todo","pluginPackages":["@backstage-community/plugin-todo","@backstage-community/plugin-todo-backend"]},"homepage":"https://backstage.io","repository":{"type":"git","url":"https://github.com/backstage/community-plugins","directory":"workspaces/todo/plugins/todo-backend"},"license":"Apache-2.0"}}]' -t 'quay.io/user/backstage-community-plugin-todo:v0.1.1' -f - .
        ✔
    Successfully built image quay.io/user/backstage-community-plugin-todo:v0.1.1 with following plugins:
      backstage-community-plugin-todo
      backstage-community-plugin-todo-backend-dynamic

    Here is an example dynamic-plugins.yaml for these plugins:

    plugins:
      - package: oci://quay.io/user/backstage-community-plugin-todo:v0.1.1!backstage-community-plugin-todo
        disabled: false
      - package: oci://quay.io/user/backstage-community-plugin-todo:v0.1.1!backstage-community-plugin-todo-backend-dynamic
        disabled: false
    ```
    ::::

    :::: formalpara
    ::: title
    Push the OCI image to a container registry:
    :::

    ``` terminal
    $ podman push quay.io/user/backstage-community-plugin-todo:v0.1.1
    ```
    ::::

    :::: formalpara
    ::: title
    Output of pushing the OCI image command
    :::

    ``` terminal
    Getting image source signatures
    Copying blob sha256:86a372c456ae6a7a305cd464d194aaf03660932efd53691998ab3403f87cacb5
    Copying config sha256:3b7f074856ecfbba95a77fa87cfad341e8a30c7069447de8144aea0edfcb603e
    Writing manifest to image destination
    ```
    ::::

4.  **Install and configure the third-party plugin**: Add the following
    plugin definitions to your `dynamic-plugins.yaml` file:

    :::: formalpara
    ::: title
    Plugin definitions in `dynamic-plugins.yaml` file
    :::

    ``` yaml
    packages:
     - package: oci://quay.io/user/backstage-community-plugin-todo:v0.1.1!backstage-community-plugin-todo
       pluginConfig:
         dynamicPlugins:
           frontend:
             backstage-community.plugin-todo:
               mountPoints:
                 - mountPoint: entity.page.todo/cards
                   importName: EntityTodoContent
               entityTabs:
                 - path: /todo
                   title: Todo
                   mountPoint: entity.page.todo
     - package: oci://quay.io/user/backstage-community-plugin-todo:v0.1.1!backstage-community-plugin-todo-backend-dynamic
       disabled: false
    ```
    ::::

## Enabling plugins added in the RHDH container image {#proc-enable-plugins-rhdh-container-image_assembly-install-third-party-plugins-rhdh}

In the RHDH container image, a set of dynamic plugins is preloaded to
enhance functionality. However, due to mandatory configuration
requirements, most of the plugins are disabled.

You can enable and configure the plugins in the RHDH container image,
including how to manage the default configuration, set necessary
environment variables, and ensure the proper functionality of the
plugins within your application.

<div>

::: title
Prerequisites
:::

- You have access to the
  [`dynamic-plugins.default.yaml`](https://github.com/janus-idp/backstage-showcase/blob/main/dynamic-plugins.default.yaml)
  file, which lists all preloaded plugins and their default
  configuration.

- You have deployed the RHDH application, and have access to the logs of
  the `install-dynamic-plugins` init container.

- You have the necessary permissions to modify plugin configurations and
  access the application environment.

- You have identified and set the required environment variables
  referenced by the plugin's default configuration. These environment
  variables must be defined in the Helm Chart or Operator configuration.

</div>

<div>

::: title
Procedure
:::

1.  Start your RHDH application and access the logs of the
    `install-dynamic-plugins` init container within the RHDH pod.

2.  Identify the [Red Hat supported
    plugins](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/dynamic_plugins_reference/index#red-hat-supported-plugins)
    that are disabled by default.

3.  Copy the package configuration from the
    [`dynamic-plugins.default.yaml`](https://github.com/janus-idp/backstage-showcase/blob/main/dynamic-plugins.default.yaml)
    file.

4.  Open the plugin configuration file and locate the plugin entry you
    want to enable.

    The location of the plugin configuration file varies based on the
    deployment method. For more details, see [Installing dynamic plugins
    with the Red Hat Developer Hub
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_and_viewing_plugins_in_red_hat_developer_hub/index#proc-config-dynamic-plugins-rhdh-operator_rhdh-installing-rhdh-plugins)
    and [Installing dynamic plugins using the Helm
    chart](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_and_viewing_plugins_in_red_hat_developer_hub/index#con-install-dynamic-plugin-helm_rhdh-installing-rhdh-plugins).

5.  Modify the `disabled` field to `false` and add the package name as
    follows:

    :::: formalpara
    ::: title
    Example plugin configuration
    :::

    ``` yaml
    plugins:
      - disabled: false
        package: ./dynamic-plugins/dist/backstage-plugin-catalog-backend-module-github-dynamic
    ```
    ::::

    For more information about how to configure dynamic plugins in
    Developer Hub, see [Installing dynamic plugins in Red Hat Developer
    Hub](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_and_viewing_plugins_in_red_hat_developer_hub/rhdh-installing-rhdh-plugins_title-plugins-rhdh-about).

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

## Extensions in Red Hat Developer Hub {#rhdh-extensions-plugins_assembly-install-third-party-plugins-rhdh}

:::: important
::: title
:::

These features are for Technology Preview only. Technology Preview
features are not supported with Red Hat production service level
agreements (SLAs), might not be functionally complete, and Red Hat does
not recommend using them for production. These features provide early
access to upcoming product features, enabling customers to test
functionality and provide feedback during the development process.

For more information on Red Hat Technology Preview features, see
[Technology Preview Features
Scope](https://access.redhat.com/support/offerings/techpreview/).
::::

Red Hat Developer Hub (RHDH) includes the Extensions feature which is
preinstalled and enabled by default. Extensions provides users with a
centralized interface to browse and manage available plugins

You can use Extensions to discover plugins that extend RHDH
functionality, streamline development workflows, and improve the
developer experience.

### Viewing available plugins {#rhdh-extensions-plugins-viewing_rhdh-extensions-plugins}

You can view plugins available for your Red Hat Developer Hub
application on the **Extensions** page.

<div>

::: title
Procedure
:::

1.  Open your Developer Hub application and click **Administration** \>
    **Extensions**.

2.  Go to the **Catalog** tab to view a list of available plugins and
    related information.

    ![Extensions
    Catalog](images/rhdh-plugins-reference/extensions-catalog.png)

</div>

### Viewing installed plugins {#proc-viewing-installed-plugins_rhdh-extensions-plugins}

Using the Dynamic Plugins Info front-end plugin, you can view plugins
that are currently installed in your Red Hat Developer Hub application.
This plugin is enabled by default.

<div>

::: title
Procedure
:::

1.  Open your Developer Hub application and click **Administration** \>
    **Extensions**.

2.  Go to the **Installed** tab to view a list of installed plugins and
    related information.

</div>

### Search and filter the plugins {#_search-and-filter-the-plugins}

#### Search by plugin name {#_search-by-plugin-name}

You can use the search bar in the header to filter the Extensions plugin
cards by name. For example, if you type "A" into the search bar,
Extensions shows only the plugins that contain the letter "A" in the
Name field.

![Extensions catalog with a Dynatrace
search](images/rhdh-plugins-reference/dynatrace-certified-and-verified.png)

Optionally, you can use the search bar in conjunction with a filter to
filter only plugins of the selected filter by name. For example, you can
apply the **Category** filter and then type a character into the search
bar to view only Openshift plugins that contain the typed character in
the name.

The following filters are available:

- Category

- Author

- Support type

#### Plugin cards {#_plugin-cards}

For each plugin card, the following details are displayed:

Badge

:   The following badges are defined:

    - Certified by Red Hat: Plugins that are produced and supported by
      Red Hat's partners.

    - Verified by Red Hat: Production ready plugins that are supported
      by Red Hat

    - Custom plugin: Plugins are created and added by the customer.

      :::: note
      ::: title
      :::

      No badge is displayed if a plugin does not match any of these
      definitions.
      ::::

Icon

:   The plugin icon (base64).

Name

:   The plugin name.

Author(s)

:   A single author name or multiple author names if a plugin is
    developed by multiple authors.

Category

:   The categories that are displayed in the filter and labels. Only one
    category is shown on the card but any other categories that you
    select will apply when you use the category filter.

Short description

:   Short description that is shown on the cards (text).

Read more link

:   Clickable link to open the plugin details page.

#### Plugin details {#_plugin-details}

When you click on the **Read more** link on a plugin card, the following
details are displayed:

Icon

:   The plugin icon (base64).

Name

:   The plugin name.

Author(s)

:   A single author name or multiple author names if a plugin is
    developed by multiple authors.

Highlights

:   A list of plugin features.

Install button

:   Button to install the plugin (disabled).

Long description

:   Full description of the plugin (Markdown).

Links

:   Clickable links providing additional information about the plugin.

Versions

:   Displays the plugin's name, version, role, supported version, and
    installation status based on the plugin's package name.

For example:

![Extensions Catalog
sidebar](images/rhdh-plugins-reference/extensions-catalog-sidebar.png)

### Removing Extensions {#rhdh-extensions-plugins-disabling_rhdh-extensions-plugins}

The Extensions feature plugins are preinstalled in Red Hat Developer Hub
(RHDH) and enabled by default. If you want to remove Extensions from
your RHDH instance, you can disable the relevant plugins.

<div>

::: title
Procedure
:::

1.  To disable the the Extensions feature plugins, edit your
    `dynamic-plugins.yaml` with the following content.

    :::: formalpara
    ::: title
    `dynamic-plugins.yaml` fragment
    :::

    ``` yaml
    plugins:
      - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-marketplace
        disabled: true
      - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-catalog-backend-module-marketplace-dynamic
        disabled: true
      - package: ./dynamic-plugins/dist/red-hat-developer-hub-backstage-plugin-marketplace-backend-dynamic
        disabled: true
    ```
    ::::

</div>

:::: note
::: title
:::

If you disable the Extensions feature plugins, the **Catalog** and
**Installed** tabs will also be removed. You can still view installed
plugins by clicking on **Administration** \> **Extensions**.
::::
