from time import sleep
from kubernetes import client, config

config.load_kube_config(config_file="~/cluster-config.yaml")
v1 = client.CoreV1Api()

def create_pod(app):
    name = app.name
    id = app.id
    size = app.size
    db_user = app.user.username
    db_password = app.user.password
    db_name = name

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

    v1.create_namespaced_persistent_volume_claim(namespace="django-app", body=pvc)
    print(f"PVC {name}-{id}-pvc created.")

    container = client.V1Container(
        name="postgres",
        image="hub.hamdocker.ir/postgres:latest",
        ports=[client.V1ContainerPort(container_port=5432)],
        volume_mounts=[client.V1VolumeMount(mount_path="/var/lib/postgresql/data", name="data-volume")],
        env=[
            client.V1EnvVar(name="POSTGRES_USER", value=db_user),
            client.V1EnvVar(name="POSTGRES_PASSWORD", value=db_password),
            client.V1EnvVar(name="POSTGRES_DB", value=db_name),
            client.V1EnvVar(name="PGDATA", value="/var/lib/postgresql/data/db-files/")
        ]
    )

    volume = client.V1Volume(
        name="data-volume",
        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=f"{name}-{id}-pvc")
    )

    pod_spec = client.V1PodSpec(
        containers=[container],
        volumes=[volume]
    )

    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=f"{name}-{id}", namespace="django-app", labels={"app": f"{name}-{id}"}),
        spec=pod_spec
    )

    v1.create_namespaced_pod(namespace="django-app", body=pod)
    print(f"Pod {name}-{id} created.")

    return pod