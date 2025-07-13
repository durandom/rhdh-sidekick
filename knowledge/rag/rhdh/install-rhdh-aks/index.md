You can install Red Hat Developer Hub on Microsoft Azure Kubernetes
Service (AKS) using one of the following methods:

- The Red Hat Developer Hub Operator

- The Red Hat Developer Hub Helm chart

## Deploying Developer Hub on AKS with the Operator {#proc-rhdh-deploy-aks-operator_title-install-rhdh-aks}

You can deploy your Developer Hub on AKS using the Red Hat Developer Hub
Operator.

<div>

::: title
Procedure
:::

1.  Obtain the Red Hat Developer Hub Operator manifest file, named
    `rhdh-operator-<VERSION>.yaml`, and modify the default configuration
    of `db-statefulset.yaml` and `deployment.yaml` by adding the
    following fragment:

    ``` yaml
    securityContext:
      fsGroup: 300
    ```

    Following is the specified locations in the manifests:

    ``` yaml
    db-statefulset.yaml: | spec.template.spec
    deployment.yaml: | spec.template.spec
    ```

2.  Apply the modified Operator manifest to your Kubernetes cluster:

    ``` bash
    kubectl apply -f rhdh-operator-<VERSION>.yaml
    ```

    :::: note
    ::: title
    :::

    Execution of the previous command is cluster-scoped and requires
    appropriate cluster privileges.
    ::::

3.  Create an `ImagePull Secret` named `rhdh-pull-secret` using your Red
    Hat credentials to access images from the protected
    `registry.redhat.io` as shown in the following example:

    ``` bash
    kubectl -n <your_namespace> create secret docker-registry rhdh-pull-secret \
        --docker-server=registry.redhat.io \
        --docker-username=<redhat_user_name> \
        --docker-password=<redhat_password> \
        --docker-email=<email>
    ```

4.  Create an Ingress manifest file, named `rhdh-ingress.yaml`,
    specifying your Developer Hub service name as follows:

    ``` yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: rhdh-ingress
      namespace: my-rhdh-project
    spec:
      ingressClassName: webapprouting.kubernetes.azure.com
      rules:
        - http:
            paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: backstage-<your-CR-name>
                    port:
                      name: http-backend
    ```

5.  To deploy the created Ingress, run the following command:

    ``` terminal
    kubectl -n <your_namespace> apply -f rhdh-ingress.yaml
    ```

6.  Create a `my-rhdh-app-config` config map containing the
    `app-config.yaml` Developer Hub configuration file by using the
    following example:

    ``` yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: my-rhdh-app-config
    data:
      "app-config.yaml": |
        app:
          title: Red Hat Developer Hub
          baseUrl: https://<app_address>
        backend:
          auth:
            externalAccess:
                - type: legacy
                  options:
                    subject: legacy-default-config
                    secret: "${BACKEND_SECRET}"
          baseUrl: https://<app_address>
          cors:
            origin: https://<app_address>
    ```

7.  Create a `<my_product_secrets>` secret and add a key named
    `BACKEND_SECRET` with a `Base64-encoded` string value as shown in
    the following example:

    ``` yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: <my_product_secrets>
    stringData:
      BACKEND_SECRET: "xxx"
    ```

    - `<my_product_secrets>` is your preferred Developer Hub secret
      name, where `<my_product_secrets>` specifies the identifier for
      your secret configuration within Developer Hub.

8.  Create your `Backstage` custom resource (CR) manifest file named
    `<your-rhdh-cr>` and include the previously created
    `rhdh-pull-secret` as follows:

    ``` yaml
    apiVersion: rhdh.redhat.com/v1alpha3
    kind: Backstage
    metadata:
      name: <your-rhdh-cr>
    spec:
      application:
        imagePullSecrets:
          - rhdh-pull-secret
        appConfig:
          configMaps:
            - name: my-rhdh-app-config
        extraEnvs:
          secrets:
            - name: <my_product_secrets>
    ```

    - `<my_product_secrets>` is your preferred Developer Hub secret
      name, where `<my_product_secrets>` specifies the identifier for
      your secret configuration within Developer Hub.

9.  Apply the CR manifest to your namespace:

    ``` terminal
    kubectl -n my-rhdh-project apply -f rhdh.yaml
    ```

10. Access the deployed Developer Hub using the URL:
    `https://app_address;`, where app_address is the Ingress address
    obtained earlier (for example, `https://108.141.70.228`).

11. Optional: To delete the CR, run the following command:

    ``` terminal
    kubectl -n my-rhdh-project delete -f rhdh.yaml
    ```

</div>

## Deploying Developer Hub on AKS with the Helm chart {#proc-rhdh-deploy-aks-helm_title-install-rhdh-aks}

You can deploy your Developer Hub application on Azure Kubernetes
Service (AKS) to access a comprehensive solution for building, testing,
and deploying applications.

<div>

::: title
Prerequisites
:::

- You have a Microsoft Azure account with active subscription.

- You have installed the [Azure
  CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).

- You have installed the [`kubectl`
  CLI](https://kubernetes.io/docs/reference/kubectl/).

- You are logged into your cluster using `kubectl`, and have `developer`
  or `admin` permissions.

- You have installed Helm 3 or the latest.

</div>

<div>

::: title
Comparison of AKS specifics with the base Developer Hub deployment
:::

- **Permissions issue**: Developer Hub containers might encounter
  permission-related errors, such as `Permission denied` when attempting
  certain operations. This error can be addressed by adjusting the
  `fsGroup` in the `PodSpec.securityContext`.

- **Ingress configuration**: In AKS, configuring ingress is essential
  for accessing the installed Developer Hub instance. Accessing the
  Developer Hub instance requires enabling the Routing add-on, an
  NGINX-based Ingress Controller, using the following command:

  ``` terminal
  az aks approuting enable --resource-group your_ResourceGroup --name your_ClusterName
  ```

  :::: tip
  ::: title
  :::

  You might need to install the Azure CLI extension `aks-preview`. If
  the extension is not installed automatically, you might need to
  install it manually using the following command:

  ``` terminal
  az extension add --upgrade -n aks-preview --allow-preview true
  ```
  ::::

  :::: note
  ::: title
  :::

  After you install the Ingress Controller, the `app-routing-system`
  namespace with the Ingress Controller will be deployed in your
  cluster. Note the address of your Developer Hub application from the
  installed Ingress Controller (for example, 108.141.70.228) for later
  access to the Developer Hub application, later referenced as
  `app_address`.

  ``` terminal
  kubectl get svc nginx --namespace app-routing-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
  ```
  ::::

- **Namespace management**: You can create a dedicated namespace for
  Developer Hub deployment in AKS using the following command:

  ``` terminal
  kubectl create namespace your_namespace
  ```

</div>

<div>

::: title
Procedure
:::

1.  Log in to AKS by running the following command:

    ``` terminal
    az login [--tenant=optional_directory_name]
    ```

2.  Create a resource group by running the following command:

    ``` terminal
    az group create --name resource_group_name --location location
    ```

    :::: tip
    ::: title
    :::

    You can list available regions by running the following command:

    ``` terminal
    az account list-locations -o table
    ```
    ::::

3.  Create an AKS cluster by running the following command:

    ``` terminal
    az aks create \
    --resource-group resource_group_name \
    --name cluster_name \
    --enable-managed-identity \
    --generate-ssh-keys
    ```

    You can refer to `--help` for additional options.

4.  Connect to your cluster by running the following command:

    ``` terminal
    az aks get-credentials --resource-group resource_group_name --name cluster_name
    ```

    The previous command configures the Kubernetes client and sets the
    current context in the `kubeconfig` to point to your AKS cluster.

5.  Open terminal and run the following command to add the Helm chart
    repository:

    ``` terminal
    helm repo add openshift-helm-charts https://charts.openshift.io/
    ```

6.  Create and activate the *my-rhdh-project* namespace:

    ``` terminal
    DEPLOYMENT_NAME=redhat-developer-hub
    NAMESPACE=rhdh
    kubectl create namespace ${NAMESPACE}
    kubectl config set-context --current --namespace=${NAMESPACE}
    ```

7.  Create a pull secret, which is used to pull the Developer Hub images
    from the Red Hat Ecosystem, by running the following command:

    ``` terminal
    kubectl -n $NAMESPACE create secret docker-registry rhdh-pull-secret \
        --docker-server=registry.redhat.io \
        --docker-username=redhat_user_name \
        --docker-password=redhat_password \
        --docker-email=email
    ```

8.  Create a file named `values.yaml` using the following template:

    ``` yaml
    global:
      host: app_address
    route:
      enabled: false
    upstream:
      ingress:
        enabled: true
        className: webapprouting.kubernetes.azure.com
        host:
      backstage:
        image:
          pullSecrets:
            - rhdh-pull-secret
        podSecurityContext:
          fsGroup: 3000
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

9.  To install Developer Hub by using the Helm chart, run the following
    command:

    ``` terminal
    helm -n $NAMESPACE install -f values.yaml $DEPLOYMENT_NAME openshift-helm-charts/redhat-developer-hub --version 1.6.0
    ```

10. Verify the deployment status:

    ``` terminal
    kubectl get deploy $DEPLOYMENT_NAME -n $NAMESPACE
    ```

11. Configure your Developer Hub Helm chart instance with the Developer
    Hub database password and router base URL values from your cluster:

    ``` terminal
    PASSWORD=$(kubectl get secret redhat-developer-hub-postgresql -o jsonpath="{.data.password}" | base64 -d)
    CLUSTER_ROUTER_BASE=$(kubectl get route console -n openshift-console -o=jsonpath='{.spec.host}' | sed 's/^[^.]*\.//')
    helm upgrade $DEPLOYMENT_NAME -i "https://github.com/openshift-helm-charts/charts/releases/download/redhat-redhat-developer-hub-1.6.0/redhat-developer-hub-1.6.0.tgz" \
        --set global.clusterRouterBase="$CLUSTER_ROUTER_BASE" \
        --set global.postgresql.auth.password="$PASSWORD"
    ```

12. Display the running Developer Hub instance URL, by running the
    following command:

    ``` terminal
    echo "https://$DEPLOYMENT_NAME-$NAMESPACE.$CLUSTER_ROUTER_BASE"
    ```

</div>

<div>

::: title
Verification
:::

- Open the running Developer Hub instance URL in your browser to use
  Developer Hub.

</div>

<div>

::: title
Upgrade
:::

- To upgrade the deployment, run the following command:

  ``` terminal
  helm upgrade $DEPLOYMENT_NAME -i https://github.com/openshift-helm-charts/charts/releases/download/redhat-redhat-developer-hub-1.6.0/redhat-developer-hub-1.6.0.tgz
  ```

</div>

<div>

::: title
Delete
:::

- To delete the deployment, run the following command:

  ``` terminal
  helm -n $NAMESPACE delete $DEPLOYMENT_NAME
  ```

</div>
