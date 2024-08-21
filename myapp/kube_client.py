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

    config.load_kube_config(config_file="~/cluster-config.yaml")

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
    except client.exceptions.ApiException as e:
        print(f"Error creating PVC: {e}")

    try:
        apps_v1.create_namespaced_stateful_set(namespace="django-app", body=statefulset)
        print(f"StatefulSet {name}-{id} created.")
    except client.exceptions.ApiException as e:
        print(f"Error creating StatefulSet: {e}")