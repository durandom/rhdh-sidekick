## Air-gapped environment {#con-airgapped-environment_title-install-rhdh-air-grapped}

An air-gapped environment, also known as an air-gapped network or
isolated network, ensures security by physically segregating the system
or network. This isolation is established to prevent unauthorized
access, data transfer, or communication between the air-gapped system
and external sources.

You can install the Red Hat Developer Hub in an air-gapped environment
to ensure security and meet specific regulatory requirements.

## Installing Red Hat Developer Hub in an air-gapped environment with the Operator {#assembly-install-rhdh-airgapped-environment-ocp-operator_title-install-rhdh-air-grapped}

You can install Red Hat Developer Hub in a fully disconnected or
partially disconnected environment using the Red Hat Developer Hub
Operator. For a list of supported platforms, see the [Red Hat Developer
Hub Life Cycle
page](https://access.redhat.com/support/policy/updates/developerhub).

### Installing Red Hat Developer Hub in a fully disconnected environment with the Operator {#proc-install-rhdh-operator-airgapped-full.adoc_title-install-rhdh-air-grapped}

In environments without internet access --- whether for security,
compliance, or operational reasons --- a fully disconnected installation
ensures that Red Hat Developer Hub can run reliably without external
dependencies.

If your network has access to the registry through a bastion host, you
can use the helper script to install Red Hat Developer Hub by mirroring
the Operator-related images to disk and transferring them to your
air-gapped environment without any connection to the internet.

<div>

::: title
Prerequisites
:::

- You have installed Podman 5.3 or later. For more information, see
  [Podman Installation
  Instructions](https://podman.io/docs/installation).

- You have installed Skopeo 1.17 or later.

- You have installed `yq` 4.44 or later.

- You have installed the GNU `sed` command line text editor.

- You have installed `umoci` CLI tool.

- You have an active `oc registry`, `podman`, or `skopeo` session to the
  `registry.redhat.io` Red Hat Ecosystem Catalog. For more information,
  see [Red Hat Container Registry
  Authentication](https://access.redhat.com/RegistryAuthentication).

- You have installed the `opm` CLI tool. For more information, see
  [Installing the opm
  CLI](https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/cli_tools/opm-cli#olm-about-opm_cli-opm-install).

</div>

<div>

::: title
Procedure
:::

1.  Download the mirroring script to disk by running the following
    command:

    ``` terminal
    curl -sSLO https://raw.githubusercontent.com/redhat-developer/rhdh-operator/refs/heads/release-1.6/.rhdh/scripts/prepare-restricted-environment.sh
    ```

2.  Run the mirroring script by using the `bash` command with the
    appropriate set of options:

    ``` terminal
    bash prepare-restricted-environment.sh
     --filter-versions "1.6"
     --to-dir _<my_pulled_image_location>_
     [--use-oc-mirror true]
    ```

    - Specifies the absolute path to a directory where you want to pull
      all of the necessary images with the `--to-dir` option, for
      example, `/home/user/rhdh-operator-mirror-dir`.

    - (Optional) Uses the `oc-mirror` OpenShift Container Platform CLI
      plugin to mirror images.

      :::: note
      ::: title
      :::

      The script can take several minutes to complete as it copies
      multiple images to the mirror registry.
      ::::

3.  Transfer the directory specified by the `--to-dir` option to your
    disconnected environment.

4.  From a machine in your disconnected environment that has access to
    both the cluster and the target mirror registry, run the mirroring
    script by using the `bash` command with the appropriate set of
    options:

    ``` terminal
    bash <my_pulled_image_location>/install.sh
        --from-dir <my_pulled_image_location>
        [--to-registry <my.registry.example.com>]
        [--use-oc-mirror true]
    ```

    - The downloaded image and the absolute path to the directory where
      it is stored on your system.

    - Specifies the directory where you want to pull all of the
      necessary images with the `--to-dir` option.

    - Specifies the URL for the target mirror registry where you want to
      mirror the images.

    - (Optional) Uses the `oc-mirror` OpenShift Container Platform CLI
      plugin to mirror images.

      :::: important
      ::: title
      :::

      If you used `oc-mirror` to mirror the images to disk, you must
      also use `oc-mirror` to mirror the images from disk due to the
      folder layout that `oc-mirror` uses.
      ::::

      :::: note
      ::: title
      :::

      The script can take several minutes to complete as it
      automatically installs the Red Hat Developer Hub Operator.
      ::::

</div>

<div>

::: title
Verification
:::

- If you are using Red Hat OpenShift Container Platform, the Red Hat
  Developer Hub Operator is in the **Installed Operators** list in the
  web console.

- If you are using a supported Kubernetes platform, you can check the
  list of pods running in the `rhdh-operator` namespace by running the
  following command in your terminal:

  ``` terminal
  kubectl -n rhdh-operator get pods
  ```

</div>

<div>

::: title
Next steps
:::

- Use the Operator to create a Red Hat Developer Hub instance on a
  supported platform. For more information, see the following
  documentation for the platform that you want to use:

  - [Installing Red Hat Developer Hub on OpenShift Container Platform
    with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_openshift_container_platform/assembly-install-rhdh-ocp-operator)

  - [Installing Developer Hub on EKS with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_amazon_elastic_kubernetes_service/proc-rhdh-deploy-eks-operator_title-install-rhdh-eks)

  - [Installing Developer Hub on AKS with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_microsoft_azure_kubernetes_service/proc-rhdh-deploy-aks-operator_title-install-rhdh-aks)

  - [Installing Developer Hub on GCP with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_openshift_dedicated_on_google_cloud_platform/proc-install-rhdh-osd-gcp-operator_title-install-rhdh-osd-gcp)

  - [Deploying Developer Hub on GKE with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_google_kubernetes_engine/proc-rhdh-deploy-gke-operator.adoc_title-install-rhdh-gke#proc-deploy-rhdh-instance-gke.adoc_title-install-rhdh-gke)

</div>

### Installing Red Hat Developer Hub in a partially disconnected environment with the Operator {#proc-install-rhdh-operator-airgapped-partial.adoc_title-install-rhdh-air-grapped}

On an OpenShift Container Platform cluster operating on a restricted
network, public resources are not available. However, deploying the Red
Hat Developer Hub Operator and running Developer Hub requires the
following public resources:

- Operator images (bundle, operator, catalog)

- Operands images (RHDH, PostgreSQL)

To make these resources available, replace them with their equivalent
resources in a mirror registry accessible to your cluster.

You can use a helper script that mirrors the necessary images and
provides the necessary configuration to ensure those images are used
when installing the Red Hat Developer Hub Operator and creating
Developer Hub instances. This script requires a target mirror registry.
You likely have a target mirror registry if your cluster is already
operating on a disconnected network. If you do not already have a target
registry, and if you have an OpenShift Container Platform cluster, you
might want to expose and leverage the internal cluster registry.

When connected to a OpenShift Container Platform cluster, the helper
script detects it and automatically exposes the cluster registry. If
connected to a Kubernetes cluster, you can manually specify the target
registry to mirror the images.

<div>

::: title
Prerequisites
:::

- You have installed Podman 5.3 or later. For more information, see
  [Podman Installation
  Instructions](https://podman.io/docs/installation).

- You have installed Skopeo 1.17 or later.

- You have installed `yq` 4.44 or later.

- You have installed the GNU `sed` command line text editor.

- You have installed `umoci` CLI tool.

- You have an active `oc registry`, `podman`, or `skopeo` session to the
  `registry.redhat.io` Red Hat Ecosystem Catalog. For more information,
  see [Red Hat Container Registry
  Authentication](https://access.redhat.com/RegistryAuthentication).

- You have an active `skopeo` session with administrative access to the
  target mirror registry. For more information, see [Authenticating to a
  registry](https://github.com/containers/skopeo#authenticating-to-a-registry).

- You have installed the `opm` CLI tool. For more information, see
  [Installing the opm
  CLI](https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/cli_tools/opm-cli#olm-about-opm_cli-opm-install).

- If you are using an OpenShift Container Platform cluster, you have the
  following prerequisites:

  - (Optional) You have installed the `oc-mirror` OpenShift Container
    Platform CLI plugin if you want to use it to mirror images.

- If you are using a supported Kubernetes cluster, you have the
  following prerequisites:

  - You have installed the Operator Lifecycle Manager (OLM) on the
    disconnected cluster.

  - You have a mirror registry that is reachable from the disconnected
    cluster.

</div>

<div>

::: title
Procedure
:::

1.  In your terminal, navigate to the directory where you want to save
    the mirroring script.

2.  Download the mirroring script by running the following command:

    ``` terminal
    curl -sSLO https://raw.githubusercontent.com/redhat-developer/rhdh-operator/refs/heads/release-1.6/.rhdh/scripts/prepare-restricted-environment.sh
    ```

3.  Run the mirroring script by using the `bash` command with the
    appropriate set of options:

    ``` terminal
    bash prepare-restricted-environment.sh \
     --filter-versions "1.6" \
      [--to-registry <my.registry.example.com>] \
      [--use-oc-mirror true]
    ```

    - Specifies the URL for the target mirror registry where you want to
      mirror the images.

    - (Optional) Uses the `oc-mirror` OpenShift Container Platform CLI
      plugin to mirror images.

      :::: note
      ::: title
      :::

      The script can take several minutes to complete as it copies
      multiple images to the mirror registry.
      ::::

</div>

<div>

::: title
Verification
:::

- If you are using Red Hat OpenShift Container Platform, the Red Hat
  Developer Hub Operator is in the **Installed Operators** list in the
  web console.

- If you are using a supported Kubernetes platform, you can check the
  list of pods running in the `rhdh-operator` namespace by running the
  following command in your terminal:

  ``` terminal
  kubectl -n rhdh-operator get pods
  ```

</div>

<div>

::: title
Next steps
:::

- Use the Operator to create a Red Hat Developer Hub instance on a
  supported platform. For more information, see the following
  documentation for the platform that you want to use:

  - [Installing Red Hat Developer Hub on OpenShift Container Platform
    with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_openshift_container_platform/assembly-install-rhdh-ocp-operator)

  - [Installing Developer Hub on EKS with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_amazon_elastic_kubernetes_service/proc-rhdh-deploy-eks-operator_title-install-rhdh-eks)

  - [Installing Developer Hub on AKS with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_microsoft_azure_kubernetes_service/proc-rhdh-deploy-aks-operator_title-install-rhdh-aks)

  - [Installing Developer Hub on GCP with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_openshift_dedicated_on_google_cloud_platform/proc-install-rhdh-osd-gcp-operator_title-install-rhdh-osd-gcp)

  - [Deploying Developer Hub on GKE with the
    Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.4/html/installing_red_hat_developer_hub_on_google_kubernetes_engine/proc-rhdh-deploy-gke-operator.adoc_title-install-rhdh-gke#proc-deploy-rhdh-instance-gke.adoc_title-install-rhdh-gke)

</div>

## Installing Red Hat Developer Hub on OpenShift Container Platform in an air-gapped environment with the Helm chart {#assembly-install-rhdh-airgapped-environment-ocp-helm_title-install-rhdh-air-grapped}

You can install Red Hat Developer Hub in a fully disconnected or
partially disconnected environment using the Red Hat Developer Hub Helm
chart.

<div>

::: title
Additional resources
:::

- For more information about registry authentication, see [Red Hat
  Container Registry
  Authentication](https://access.redhat.com/RegistryAuthentication).

</div>

### Installing Red Hat Developer Hub on OpenShift Container Platform in a fully disconnected environment with the Helm chart {#proc-install-rhdh-helm-airgapped-full.adoc_title-install-rhdh-air-grapped}

If your network has access to the registry through a bastion host, you
can use the Helm chart to install Red Hat Developer Hub by mirroring
specified resources to disk and transferring them to your air-gapped
environment without any connection to the internet.

<div>

::: title
Prerequisites
:::

- You have set up your workstation.

  - You have access to the registry.redhat.io.

  - You have access to the charts.openshift.io Helm chart repository.

  - You have installed the OpenShift CLI (`oc`) on your workstation.

  - You have installed the oc-mirror OpenShift CLI (`oc`) plugin, for
    more information see [Installing the oc-mirror OpenShift CLI
    plugin](https://docs.openshift.com/container-platform/4.17/disconnected/mirroring/installing-mirroring-disconnected.html#installation-oc-mirror-installing-plugin_installing-mirroring-disconnected).

  - You have an account in [Red Hat
    Developer](https://developers.redhat.com/) portal.

- You have set up your intermediary host.

  - Your host has access to the disconnected cluster and to the target
    mirror registry, for example, the Red Hat OpenShift Container
    Platform image registry. For more information about exposing the
    OpenShift Container Platform image registry, see [Exposing the
    registry](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/registry/index#securing-exposing-registry).

  - You have installed the oc-mirror OpenShift CLI (`oc`) plugin, for
    more information see [Installing the oc-mirror OpenShift CLI
    plugin](https://docs.openshift.com/container-platform/4.17/disconnected/mirroring/installing-mirroring-disconnected.html#installation-oc-mirror-installing-plugin_installing-mirroring-disconnected).

  - You have installed Red Hat OpenShift Container Platform 4.14 or
    later.

  - You have installed the OpenShift CLI (`oc`) on your workstation.

</div>

<div>

::: title
Procedure
:::

1.  Create an `ImageSetConfiguration` file to specify the resources that
    you want to mirror. For example:

    ``` terminal
    apiVersion: mirror.openshift.io/v1alpha2
    kind: ImageSetConfiguration
    mirror:
      helm:
        repositories:
               - name: <repository_name> (1)
            url: <repository_url> (2)
            charts:
              - name: <chart_name> (3)
                version: "<rhdh_version>" (4)
    ```

    - The name of the repository that you want to mirror, for example,
      `openshift-charts`.

    - The URL for the repository that you want to mirror, for example,
      `https://charts.openshift.io`.

    - The name of the Helm chart that you want to mirror, for example,
      `redhat-developer-hub`.

    - The version of Red Hat Developer Hub that you want to use, for
      example, `1.6`

2.  Mirror the resources specified in the `ImageSetConfiguration.yaml`
    file by running the `oc-mirror` command. For example:

    ``` terminal
    oc-mirror --config=<mirror_config_directory>/ImageSetConfiguration.yaml <mirror_archive_directory>/
    ```

    where:

    `<mirror_config_directory>`

    :   Specifies the location of your image set configuration file on
        your system, for example, `.user`.

    `<mirror_configuration_file>`

    :   Specifies the name of your mirror configuration yaml file, for
        example, `mirror-config.yaml`

    `<mirror_archive_directory>`

    :   Specifies the location of your directory where the mirror
        archive will be created, for example,`file://.user`.

    :::: note
    ::: title
    :::

    Running the `oc-mirror` command generates a local workspace
    containing the mirror archive file, the Helm chart, and a
    `ImageContentSourcePolicy` (ICSP) manifest. The ICSP manifest
    contains an `imageContentSourcePolicy.yaml` file that you must apply
    against the cluster in a later step.
    ::::

    :::: formalpara
    ::: title
    Example output
    :::

    ``` terminal
    Creating archive /path/to/mirror-archive/mirror_seq1_000000.tar
    ```
    ::::

3.  Transfer the generated archive file (for example,
    `mirror_seq1_000000.tar`) to the air-gapped environment.

4.  Connect to your air-gapped environment and make sure that you are
    also connected to the following objects:

    - The local target registry

    - The target OpenShift Container Platform cluster

5.  From your air-gapped environment, mirror the resources from the
    archive to the target registry by running the `oc-mirror` command.
    For example:

    ``` terminal
    oc-mirror --from <mirror-archive-file> <target-registry>
    ```

    where:

    `<mirror_archive_file>`

    :   Specifies the name of the file containing the resources that you
        want to mirror, for example,`mirror_seq1_0000.tar`.

    `<target_registry>`

    :   Specifies the name of the target registry that you want to push
        the mirrored images to, for example,
        `docker://registry.localhost:5000`.

    :::: formalpara
    ::: title
    Example output
    :::

    ``` terminal
    Wrote release signatures to oc-mirror-workspace/results-1738075410
    Writing image mapping to oc-mirror-workspace/results-1738075410/mapping.txt
    Writing ICSP manifests to oc-mirror-workspace/results-1738075410
    ```
    ::::

6.  In your workspace, locate the `imageContentSourcePolicy.yaml` file
    by running the `ls` command. For example:

    ``` terminal
    ls <workspace_directory>/<results_directory>
    ```

    where:

    `<workspace_directory>`

    :   Specifies the name of your workspace directory, for example,
        `oc-mirror-workspace`.

    `<results_directory>`

    :   Specifies the name of your results directory, for example,
        `results-1738070846`.

7.  To mirror the Helm chart, deploy the `imageContentSourcePolicy.yaml`
    file in the disconnected cluster by running the `oc apply` command.
    For example:

    ``` terminal
    oc apply -f <workspace_directory>/<results_directory>/ImageContentSourcePolicy.yaml
    ```

    where:

    `<workspace-directory>`

    :   Specifies the name of your workspace directory, for example,
        `oc-mirror-workspace`.

    `<results-directory>`

    :   Specifies the name of your results directory, for example,
        `results-1738070846`.

8.  In your air-gapped environment, deploy the Helm chart to the
    namespace that you want to use by running the `helm install` command
    with `namespace` and `set` options. For example:

    ``` terminal
    CLUSTER_ROUTER_BASE=$(oc get route console -n openshift-console -o=jsonpath='{.spec.host}' | sed 's/[.]*\.//')

    helm install <rhdh_instance> <workspace_directory>/<results_directory>/charts/<archive_file> --namespace <your_namespace> --create-namespace \
      --set global.clusterRouterBase="$CLUSTER_ROUTER_BASE"
    ```

    where:

    `<rhdh_instance>`

    :   Specifies the name of your Red Hat Developer Hub instance, for
        example, `my-rhdh`.

    `<workspace_directory>`

    :   Specifies the name of your workspace directory, for example,
        `oc-mirror-workspace`.

    `<results_directory>`

    :   Specifies the name of your results directory, for example,
        `results-1738070846`.

    `<archive_file>`

    :   Specifies the name of the archive file containing the resources
        that you want to mirror, for example,
        `redhat-developer-hub-1.4.1.tgz`.

    `<your_namespace>`

    :   Specifies the namespace that you want to deploy the Helm chart
        to, for example, `my-rhdh-project`.

</div>

### Installing Red Hat Developer Hub on OpenShift Container Platform in a partially disconnected environment with the Helm chart {#proc-install-rhdh-helm-airgapped-partial.adoc_title-install-rhdh-air-grapped}

If your network has access to the `registry.redhat.io` registry and the
`charts.openshift.io` Helm chart repository, you can deploy your Red Hat
Developer Hub instance in your partially disconnected environment by
mirroring the specified resources directly to the target registry.

<div>

::: title
Prerequisites
:::

- You have installed Red Hat OpenShift Container Platform 4.14 or later.

- You have access to the `charts.openshift.io` Helm chart repository.

- You have access to the `registry.redhat.io`.

- You have access to a mirror registry that can be reached from the
  disconnected cluster, for example, the OpenShift Container Platform
  image registry. For more information about exposing the OpenShift
  Container Platform image registry, see [Exposing the
  registry](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/registry/index#securing-exposing-registry).

- You are logged in to your target mirror registry and have permissions
  to push images to it. For more information, see [Configuring
  credentials that allow images to be
  mirrored](https://docs.openshift.com/container-platform/4.17/disconnected/mirroring/installing-mirroring-disconnected.html#installation-adding-registry-pull-secret_installing-mirroring-disconnected).

- You have installed the OpenShift CLI (`oc`) on your workstation.

- You have installed the oc-mirror OpenShift CLI (`oc`) plugin, for more
  information see [Installing the oc-mirror OpenShift CLI
  plugin](https://docs.openshift.com/container-platform/4.17/disconnected/mirroring/installing-mirroring-disconnected.html#installation-oc-mirror-installing-plugin_installing-mirroring-disconnected).

- You have an account in [Red Hat
  Developer](https://developers.redhat.com/) portal.

</div>

<div>

::: title
Procedure
:::

1.  Log in to your OpenShift Container Platform account using the
    OpenShift CLI (`oc`) by running the following command:

    ``` terminal
    oc login -u <user> -p <password> https://api.<hostname>:6443
    ```

2.  From your disconnected cluster, log in to the image registry that
    you want to mirror, for example, the OpenShift Container Platform
    image registry.

3.  Create an `ImageSetConfiguration.yaml` file.

4.  In your `ImageSetConfiguration.yaml` file, specify the resources
    that you want to mirror. For example:

    ``` terminal
    apiVersion: mirror.openshift.io/v1alpha2
    kind: ImageSetConfiguration
    mirror:
      helm:
        repositories:
          - name: <repository_name> (1)
            url: <repository_url> (2)
            charts:
              - name: <chart_name> (3)
                version: "<rhdh_version>" (4)
    ```

    - The name of the repository containing the Helm chart that you want
      to mirror, for example, `openshift-charts`.

    - The URL for the repository containing the Helm chart that you want
      to mirror, for example, `https://charts.openshift.io`.

    - The name of the Helm chart containing the images that you want to
      mirror, for example, `redhat-developer-hub`.

    - The Red Hat Developer Hub version that you want to use, for
      example, `1.6`

5.  Mirror the resources specified in the image set configuration file
    directly to the target registry by running the `oc-mirror` command.
    For example:

    ``` terminal
    oc-mirror --config=<mirror_config_directory>/ImageSetConfiguration.yaml <target-mirror-registry>
    ```

    where:

    `<mirror_config_directory>`

    :   Specifies the location of your image set configuration file on
        your system, for example, `.user`.

    `<target_mirror_registry>`

    :   Specifies the location and name of your target mirror registry,
        for example,`docker://registry.example:5000`.

    :::: note
    ::: title
    :::

    Running the `oc-mirror` command creates a local workspace containing
    the Helm chart and a `ImageContentSourcePolicy` (ICSP) manifest. The
    ICSP manifest contains an automatically-generated
    `imageContentSourcePolicy.yaml` file that you must apply against the
    cluster in a later step.
    ::::

    :::: formalpara
    ::: title
    Example output
    :::

    ``` terminal
    Writing image mapping to oc-mirror-workspace/results-1738070846/mapping.txt
    Writing ICSP manifests to oc-mirror-workspace/results-1738070846
    ```
    ::::

6.  In your workspace, locate the `imageContentSourcePolicy.yaml` file
    by running the `ls` command. For example:

    ``` terminal
    ls <workspace_directory>/<results_directory>
    ```

    where:

    `<workspace_directory>`

    :   Specifies the name of your workspace directory, for example,
        `oc-mirror-workspace`.

    `<results_directory>`

    :   Specifies the name of your results directory, for example,
        `results-1738070846`.

7.  To mirror the Helm chart, deploy the `imageContentSourcePolicy.yaml`
    file in the disconnected cluster by running the `oc apply` command.
    For example:

    ``` terminal
    oc apply -f <workspace_directory>/<results_directory>/ImageContentSourcePolicy.yaml
    ```

    where:

    `<workspace_directory>`

    :   Specifies the name of your workspace directory, for example,
        `oc-mirror-workspace`.

    `<results_directory>`

    :   Specifies the name of your results directory, for example,
        `results-1738070846`.

8.  In your air-gapped environment, deploy the Helm chart to the
    namespace that you want to use by running the `helm install` command
    with `namespace` and `set` options. For example:

    ``` terminal
    CLUSTER_ROUTER_BASE=$(oc get route console -n openshift-console -o=jsonpath='{.spec.host}' | sed 's/[.]*\.//')

    helm install <rhdh_instance> <workspace_directory>/<results_directory>/charts/<archive_file> --namespace <your_namespace> --create-namespace \
      --set global.clusterRouterBase="$CLUSTER_ROUTER_BASE"
    ```

    where:

    `<rhdh_instance>`

    :   Specifies the name of your Red Hat Developer Hub instance, for
        example, `my-rhdh`.

    `<workspace_directory>`

    :   Specifies the name of your workspace directory, for example,
        `oc-mirror-workspace`.

    `<results_directory>`

    :   Specifies the name of your results directory, for example,
        `results-1738070846`.

    `<archive_file>`

    :   Specifies the name of the archive file containing the resources
        that you want to mirror, for example,
        `redhat-developer-hub-1.4.1.tgz`.

    `<your_namespace>`

    :   Specifies the namespace that you want to deploy the Helm chart
        to, for example, `my-rhdh-project`.

</div>
