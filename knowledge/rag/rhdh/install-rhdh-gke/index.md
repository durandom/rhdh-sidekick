You can install Red Hat Developer Hub on Google Kubernetes Engine (GKE)
using one of the following methods:

- The Red Hat Developer Hub Operator

- The Red Hat Developer Hub Helm chart

## Installing the Developer Hub Operator with the OLM framework {#proc-rhdh-deploy-gke-operator.adoc_title-install-rhdh-gke}

You can install the Developer Hub Operator on GKE using the [Operator
Lifecycle Manager (OLM) framework](https://olm.operatorframework.io).
Following that, you can proceed to deploy your Developer Hub instance in
GKE.

For information about the OLM, see [Operator Lifecycle
Manager(OLM)](https://olm.operatorframework.io/docs/) documentation.

<div>

::: title
Prerequisites
:::

- You have subscribed to `registry.redhat.io`. For more information, see
  [Red Hat Container Registry
  Authentication](https://access.redhat.com/RegistryAuthentication).

- You have installed the Operator Lifecycle Manager (OLM). For more
  information about installation and troubleshooting, see [How do I get
  Operator Lifecycle
  Manager?](https://operatorhub.io/how-to-install-an-operator#How-do-I-get-Operator-Lifecycle-Manager?)

- You have installed `kubectl`. For more information, see [Install
  kubetl](https://kubernetes.io/docs/tasks/tools/#kubectl).

- You have installed the Google Cloud CLI. For more information, see
  [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install).

- You have logged in to your Google account and created a [GKE
  Autopilot](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-an-autopilot-cluster)
  or [GKE
  Standard](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-zonal-cluster)
  cluster.

</div>

<div>

::: title
Procedure
:::

1.  Connect to your GKE cluster using the following command:

    ``` terminal
    gcloud container clusters get-credentials <cluster-name> \
        --location=<cluster-location>
    ```

    - Enter your GKE cluster name.

    - Enter your GKE cluster location.

    This command configures your Kubernetes client to point to your GKE
    cluster.

2.  Run the following command in your terminal to create the
    `rhdh-operator` namespace where the Operator is installed:

    ``` terminal
    kubectl create namespace rhdh-operator
    ```

3.  Create a pull secret using the following command:

    ``` terminal
    kubectl -n rhdh-operator create secret docker-registry rhdh-pull-secret \
        --docker-server=registry.redhat.io \
        --docker-username=<user_name> \
        --docker-password=<password> \
        --docker-email=<email>
    ```

    - Enter your username in the command.

    - Enter your password in the command.

    - Enter your email address in the command.

    The created pull secret is used to pull the Developer Hub images
    from the Red Hat Ecosystem.

4.  Create a `CatalogSource` resource that contains the Operator from
    the Red Hat Ecosystem:

    :::: formalpara
    ::: title
    Example `CatalogSource` resource
    :::

    ``` terminal
    cat <<EOF | kubectl -n rhdh-operator apply -f -
    apiVersion: operators.coreos.com/v1alpha1
    kind: CatalogSource
    metadata:
      name: redhat-catalog
    spec:
      sourceType: grpc
      image: registry.redhat.io/redhat/redhat-operator-index:v4.18
      secrets:
      - "rhdh-pull-secret"
      displayName: Red Hat Operators
    EOF
    ```
    ::::

5.  Create an `OperatorGroup` resource as follows:

    :::: formalpara
    ::: title
    Example `OperatorGroup` resource
    :::

    ``` terminal
    cat <<EOF | kubectl apply -n rhdh-operator -f -
    apiVersion: operators.coreos.com/v1
    kind: OperatorGroup
    metadata:
      name: rhdh-operator-group
    EOF
    ```
    ::::

6.  Create a `Subscription` resource using the following code:

    :::: formalpara
    ::: title
    Example `Subscription` resource
    :::

    ``` terminal
    cat <<EOF | kubectl apply -n rhdh-operator -f -
    apiVersion: operators.coreos.com/v1alpha1
    kind: Subscription
    metadata:
      name: rhdh
      namespace: rhdh-operator
    spec:
      channel: fast
      installPlanApproval: Automatic
      name: rhdh
      source: redhat-catalog
      sourceNamespace: rhdh-operator
      startingCSV: rhdh-operator.v1.6.0
    EOF
    ```
    ::::

7.  Run the following command to verify that the created Operator is
    running:

    ``` terminal
    kubectl -n rhdh-operator get pods -w
    ```

    If the Operator pod shows `ImagePullBackOff` status, you might need
    permission to pull the image directly within the Operator
    deployment's manifest.

    :::: tip
    ::: title
    :::

    You can include the required secret name in the
    `deployment.spec.template.spec.imagePullSecrets` list and verify the
    deployment name using `kubectl get deployment -n rhdh-operator`
    command. For example:

    ``` terminal
    kubectl -n rhdh-operator patch deployment \
        rhdh.fast --patch '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"rhdh-pull-secret"}]}}}}' \
        --type=merge
    ```
    ::::

8.  Update the default configuration of the Operator to ensure that
    Developer Hub resources can start correctly in GKE using the
    following steps:

    a.  Edit the `backstage-default-config` ConfigMap in the
        `rhdh-operator` namespace using the following command:

        ``` terminal
        kubectl -n rhdh-operator edit configmap backstage-default-config
        ```

    b.  Locate the `db-statefulset.yaml` string and add the `fsGroup` to
        its `spec.template.spec.securityContext`, as shown in the
        following example:

        :::: formalpara
        ::: title
        `db-statefulset.yaml` fragment
        :::

        ``` yaml
          db-statefulset.yaml: |
            apiVersion: apps/v1
            kind: StatefulSet
        --- TRUNCATED ---
            spec:
            --- TRUNCATED ---
              restartPolicy: Always
              securityContext:
              # You can assign any random value as fsGroup
                fsGroup: 2000
              serviceAccount: default
              serviceAccountName: default
        --- TRUNCATED ---
        ```
        ::::

    c.  Locate the `deployment.yaml` string and add the `fsGroup` to its
        specification, as shown in the following example:

        :::: formalpara
        ::: title
        `deployment.yaml` fragment
        :::

        ``` yaml
          deployment.yaml: |
            apiVersion: apps/v1
            kind: Deployment
        --- TRUNCATED ---
            spec:
              securityContext:
                # You can assign any random value as fsGroup
                fsGroup: 3000
              automountServiceAccountToken: false
        --- TRUNCATED ---
        ```
        ::::

    d.  Locate the `service.yaml` string and change the `type` to
        `NodePort` as follows:

        :::: formalpara
        ::: title
        `service.yaml` fragment
        :::

        ``` yaml
          service.yaml: |
            apiVersion: v1
            kind: Service
            spec:
             # NodePort is required for the ALB to route to the Service
              type: NodePort
        --- TRUNCATED ---
        ```
        ::::

    e.  Save and exit.

        Wait until the changes are automatically applied to the Operator
        pods.

</div>

### Deploying the Developer Hub instance on GKE with the Operator {#proc-deploy-rhdh-instance-gke.adoc_title-install-rhdh-gke}

You can deploy your Developer Hub instance in GKE using the Operator.

<div>

::: title
Prerequisites
:::

- A cluster administrator has installed the Red Hat Developer Hub
  Operator.

- You have subscribed to `registry.redhat.io`. For more information, see
  [Red Hat Container Registry
  Authentication](https://access.redhat.com/RegistryAuthentication).

- You have installed `kubectl`. For more information, see [Install
  kubetl](https://kubernetes.io/docs/tasks/tools/#kubectl).

- You have configured a domain name for your Developer Hub instance.

- You have reserved a static external Premium IPv4 Global IP address
  that is not attached to any virtual machine (VM). For more information
  see [Reserve a new static external IP
  address](https://cloud.google.com/vpc/docs/reserve-static-external-ip-address#reserve_new_static)

- You have configured the DNS records for your domain name to point to
  the IP address that has been reserved.

  :::: note
  ::: title
  :::

  You need to create an `A` record with the value equal to the IP
  address. This process can take up to one hour to propagate.
  ::::

</div>

<div>

::: title
Procedure
:::

1.  Create a `app-config.yaml` config map containing the
    `app-config.yaml` Developer Hub configuration file by using the
    following template:

    :::: formalpara
    ::: title
    `app-config.yaml` fragment
    :::

    ``` yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: my-rhdh-app-config
    data:
      "app-config.yaml": |
        app:
          title: Red Hat Developer Hub
          baseUrl: https://<rhdh_domain_name>
        backend:
          auth:
            externalAccess:
                - type: legacy
                  options:
                    subject: legacy-default-config
                    secret: "${BACKEND_SECRET}"
          baseUrl: https://<rhdh_domain_name>
          cors:
            origin: https://<rhdh_domain_name>
    ```
    ::::

2.  Create a `<my_product_secrets>` secret and add a key named
    `BACKEND_SECRET` with a `Base64-encoded` string value as shown in
    the following example:

    ``` yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: <my_product_secrets>
    stringData:
      # TODO: See https://backstage.io/docs/auth/service-to-service-auth/#setup
      BACKEND_SECRET: "xxx"
    ```

    - `<my_product_secrets>` is your preferred Developer Hub secret
      name, where `<my_product_secrets>` specifies the identifier for
      your secret configuration within Developer Hub.

    :::: important
    ::: title
    :::

    Ensure that you use a unique value of `BACKEND_SECRET` for each
    Developer Hub instance.
    ::::

    You can use the following command to generate a key:

    ``` terminal
    node-p'require("crypto").randomBytes(24).toString("base64")'
    ```

3.  To enable pulling the PostgreSQL image from the Red Hat Ecosystem
    Catalog, add the image pull secret in the default service account
    within the namespace where the Developer Hub instance is being
    deployed:

    ``` terminal
    kubectl patch serviceaccount default \
        -p '{"imagePullSecrets": [{"name": "rhdh-pull-secret"}]}' \
        -n <your_namespace>
    ```

4.  Create your `Backstage` custom resource (CR) file using the
    following template:

    :::: formalpara
    ::: title
    Custom resource fragment
    :::

    ``` yaml
    apiVersion: rhdh.redhat.com/v1alpha3
    kind: Backstage
    metadata:
      # This is the name of your Developer Hub instance
      name: my-rhdh
    spec:
      application:
        imagePullSecrets:
        - "rhdh-pull-secret"
        route:
          enabled: false
        appConfig:
          configMaps:
            - name: my-rhdh-app-config
        extraEnvs:
          secrets:
            - name: <my_product_secrets>
    ```
    ::::

    - `<my_product_secrets>` is your preferred Developer Hub secret
      name, where `<my_product_secrets>` specifies the identifier for
      your secret configuration within Developer Hub.

5.  Set up a Google-managed certificate by creating a
    `ManagedCertificate` object which you must attach to the Ingress as
    shown in the following example:

    ``` yaml
    apiVersion: networking.gke.io/v1
    kind: ManagedCertificate
    metadata:
      name: <rhdh_certificate_name>
    spec:
      domains:
        - <rhdh_domain_name>
    ```

    For more information about setting up a Google-managed certificate,
    see [Setting up a Google-managed
    certificate](https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs?hl=en#setting_up_a_google-managed_certificate).

6.  Create a `FrontendConfig` object to set a policy for redirecting to
    HTTPS. You must attach this policy to the Ingress.

    :::: formalpara
    ::: title
    Example of a `FrontendConfig` object
    :::

    ``` yaml
    apiVersion: networking.gke.io/v1beta1
    kind: FrontendConfig
    metadata:
      name: <ingress_security_config>
    spec:
      sslPolicy: gke-ingress-ssl-policy-https
      redirectToHttps:
        enabled: true
    ```
    ::::

    For more information about setting a policy to redirect to HTTPS,
    see [HTTP to HTTPS
    redirects](https://cloud.google.com/kubernetes-engine/docs/how-to/ingress-configuration?hl=en#https_redirect).

7.  Create an ingress resource using the following template, customizing
    the names as needed:

    :::: formalpara
    ::: title
    Example of an ingress resource configuration
    :::

    ``` yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      # TODO: this the name of your Developer Hub Ingress
      name: my-rhdh
      annotations:
        # If the class annotation is not specified it defaults to "gce".
        kubernetes.io/ingress.class: "gce"
        kubernetes.io/ingress.global-static-ip-name: <ADDRESS_NAME>
        networking.gke.io/managed-certificates: <rhdh_certificate_name>
        networking.gke.io/v1beta1.FrontendConfig: <ingress_security_config>
    spec:
      ingressClassName: gce
      rules:
        # TODO: Set your application domain name.
        - host: <rhdh_domain_name>
          http:
            paths:
            - path: /
              pathType: Prefix
              backend:
                service:
                  # TODO: my-rhdh is the name of your `Backstage` custom resource.
                  # Adjust if you changed it!
                  name: backstage-my-rhdh
                  port:
                    name: http-backend
    ```
    ::::

</div>

<div>

::: title
Verification
:::

- Wait for the `ManagedCertificate` to be provisioned. This process can
  take a couple of hours.

- Access RHDH with `https://rhdh_domain_name;`

</div>

:::: formalpara
::: title
Additional information
:::

For more information on setting up GKE using Ingress with TLS, see
[Secure GKE
Ingress](https://github.com/GoogleCloudPlatform/gke-networking-recipes/tree/main/ingress/single-cluster/ingress-https).
::::

## Installing Developer Hub on GKE with the Helm chart {#proc-rhdh-deploy-gke-helm_title-install-rhdh-gke}

When you install the Developer Hub Helm chart in Google Kubernetes
Engine (GKE), it orchestrates the deployment of a Developer Hub
instance, which provides a robust developer platform within the GKE
ecosystem.

<div>

::: title
Prerequisites
:::

- You have subscribed to `registry.redhat.io`. For more information, see
  [Red Hat Container Registry
  Authentication](https://access.redhat.com/RegistryAuthentication).

- You have installed `kubectl`. For more information, see [Install
  kubetl](https://kubernetes.io/docs/tasks/tools/#kubectl).

- You have installed the Google Cloud CLI. For more information, see
  [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install).

- You have logged in to your Google account and created a [GKE
  Autopilot](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-an-autopilot-cluster)
  or [GKE
  Standard](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-zonal-cluster)
  cluster.

- You have configured a domain name for your Developer Hub instance.

- You have reserved a static external Premium IPv4 Global IP address
  that is not attached to any VM. For more information see [Reserve a
  new static external IP
  address](https://cloud.google.com/vpc/docs/reserve-static-external-ip-address#reserve_new_static)

- You have configured the DNS records for your domain name to point to
  the IP address that has been reserved.

  :::: note
  ::: title
  :::

  You need to create an `A` record with the value equal to the IP
  address. This process can take up to one hour to propagate.
  ::::

- You have installed Helm 3 or the latest. For more information, see
  [Installing Helm](https://helm.sh/docs/intro/install).

</div>

<div>

::: title
Procedure
:::

1.  Go to your terminal and run the following command to add the Helm
    chart repository containing the Developer Hub chart to your local
    Helm registry:

    ``` terminal
    helm repo add openshift-helm-charts https://charts.openshift.io/
    ```

2.  Create a pull secret using the following command:

    ``` terminal
    kubectl -n your-namespace create secret docker-registry rhdh-pull-secret \
        --docker-server=registry.redhat.io \
        --docker-username=user_name \
        --docker-password=password \
        --docker-email=email
    ```

    - Enter your GKE namespace in the command.

    - Enter your username in the command.

    - Enter your password in the command.

    - Enter your email address in the command.

    The created pull secret is used to pull the Developer Hub images
    from the Red Hat Ecosystem.

3.  Set up a Google-managed certificate by creating a
    `ManagedCertificate` object that you must attach to the ingress.

    :::: formalpara
    ::: title
    Example of attaching a `ManagedCertificate` object to the ingress
    :::

    ``` yaml
    apiVersion: networking.gke.io/v1
    kind: ManagedCertificate
    metadata:
      name: rhdh_certificate_name
    spec:
      domains:
        - rhdh_domain_name
    ```
    ::::

    For more information about setting up a Google-managed certificate,
    see [Setting up a Google-managed
    certificate](https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs?hl=en#setting_up_a_google-managed_certificate).

4.  Create a `FrontendConfig` object to set a policy for redirecting to
    HTTPS. You must attach this policy to the ingress.

    :::: formalpara
    ::: title
    Example of attaching a `FrontendConfig` object to the ingress
    :::

    ``` yaml
    apiVersion: networking.gke.io/v1beta1
    kind: FrontendConfig
    metadata:
      name: ingress_security_config
    spec:
      sslPolicy: gke-ingress-ssl-policy-https
      redirectToHttps:
        enabled: true
    ```
    ::::

    For more information about setting a policy to redirect to HTTPS,
    see [HTTP to HTTPS
    redirects](https://cloud.google.com/kubernetes-engine/docs/how-to/ingress-configuration?hl=en#https_redirect).

5.  Create a file named `values.yaml` using the following template:

    :::: formalpara
    ::: title
    Example `values.yaml` file
    :::

    ``` yaml
    global:
      host: rhdh_domain_name
    route:
      enabled: false
    upstream:
      service:
        type: NodePort
      ingress:
        enabled: true
        annotations:
          kubernetes.io/ingress.class: gce
          kubernetes.io/ingress.global-static-ip-name: ADDRESS_NAME
          networking.gke.io/managed-certificates: rhdh_certificate_name
          networking.gke.io/v1beta1.FrontendConfig: ingress_security_config
        className: gce
      backstage:
        image:
          pullSecrets:
          - rhdh-pull-secret
        podSecurityContext:
          fsGroup: 2000
      postgresql:
        image:
          pullSecrets:
          - rhdh-pull-secret
        primary:
          podSecurityContext:
            enabled: true
            fsGroup: 3000
      volumePermissions:
        enabled: true
    ```
    ::::

6.  Run the following command in your terminal to deploy Developer Hub
    using the latest version of Helm Chart and using the `values.yaml`
    file:

    ``` terminal
    helm -n your_namespace install -f values.yaml your_deploy_name \
      openshift-helm-charts/redhat-developer-hub \
      --version 1.6.0
    ```

    For the latest Helm Chart version, see this [Helm
    Charts](https://github.com/openshift-helm-charts/charts/tree/main/charts/redhat/redhat/redhat-developer-hub)
    repository.

</div>

<div>

::: title
Verification
:::

- Confirm that the deployment is complete.

  ``` terminal
  kubectl get deploy you_deploy_name-developer-hub -n your_namespace
  ```

- Verify that the service and ingress were created.

  ``` terminal
  kubectl get service -n your_namespace
  kubectl get ingress -n your_namespace
  ```

  :::: note
  ::: title
  :::

  Wait for the `ManagedCertificate` to be provisioned. This process can
  take a couple of hours.
  ::::

- Access RHDH with `https://rhdh_domain_name;`

- To upgrade your deployment, use the following command:

  ``` terminal
  helm -n your_namespace upgrade -f values.yaml your_deploy_name openshift-helm-charts/redhat-developer-hub --version UPGRADE_CHART_VERSION
  ```

- To delete your deployment, use the following command:

  ``` terminal
  helm -n your_namespace delete your_deploy_name
  ```

</div>
