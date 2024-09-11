from kubernetes import client, config

# config.load_kube_config(config_file="~/cluster-config.yaml")
# v1 = client.CoreV1Api()

def create_pod(app):
    name = app.name
    id = app.id
    size = app.size
    db_user = app.user.username #TODO
    db_password = app.user.password
    db_name = name

    # def load_kube_config_with_token(token):
    #     configuration = client.Configuration()
    #     configuration.host = "https://188.121.121.38:6443"
    #     configuration.ssl_ca_cert = "./ca.crt"
    #     configuration.verify_ssl = True
    #     configuration.api_key = {"authorization": f"Bearer {token}"}

    #     client.Configuration.set_default(configuration)

    # token = "4b8d5c3dbc87283bed1bb43fc30b08efaca7ee8a0349d232f538cc2d9d3186cc"
    # load_kube_config_with_token(token)

    # config.load_kube_config(config_file="~/cluster-config.yaml")
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    pvc = client.V1PersistentVolumeClaim(
        metadata=client.V1ObjectMeta(name=f"{name}-{id}-pvc", namespace="django-app"),
        spec=client.V1PersistentVolumeClaimSpec(
            storage_class_name="rawfile-localpv",
            access_modes=["ReadWriteOnce"],
            resources=client.V1ResourceRequirements(
                requests={"storage": f"{size}Gi"}
            )
        )
    )

    statefulset = client.V1StatefulSet(
        metadata=client.V1ObjectMeta(name=f"{name}-{id}", namespace="django-app"),
        spec=client.V1StatefulSetSpec(
            service_name=name,
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={"app": name}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": name}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="postgres",
                            image="hub.hamdocker.ir/postgres",
                            ports=[client.V1ContainerPort(container_port=5432)],
                            volume_mounts=[client.V1VolumeMount(
                                mount_path="/var/lib/postgresql/data",
                                name="data-volume"
                            )],
                            env=[
                                client.V1EnvVar(name="POSTGRES_USER", value=db_user),
                                client.V1EnvVar(name="POSTGRES_PASSWORD", value=db_password),
                                client.V1EnvVar(name="POSTGRES_DB", value=db_name),
                                client.V1EnvVar(name="PGDATA", value="/var/lib/postgresql/data/db-files/")
                            ]
                        )
                    ],
                    volumes=[
                        client.V1Volume(
                            name="data-volume",
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                claim_name=f"{name}-{id}-pvc"
                            )
                        )
                    ]
                )
            )
        )
    )


    try:
        v1.create_namespaced_persistent_volume_claim(namespace="django-app", body=pvc)
        print(f"PVC {name}-{id}-pvc created.")
    except client.exceptions as e:
        print(f"Error creating PVC: {e}")

    try:
        apps_v1.create_namespaced_stateful_set(namespace="django-app", body=statefulset)
        print(f"StatefulSet {name}-{id} created.")
    except client.exceptions as e:
        print(f"Error creating StatefulSet: {e}")