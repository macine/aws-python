import boto3
import json

source_profile        = 'NWPDESA-RolesIAM'  # Perfil de AWS para la cuenta de origen
destination_profile   = 'ARQ-ADMIN'  # Perfil de AWS para la cuenta de destino
source_ecr_client = boto3.Session(profile_name=source_profile).client('ecr')
destination_ecr_client = boto3.Session(profile_name=destination_profile).client('ecr')


def create_repository_if_not_exists(ecr_client, repository_name):
    # Verificar si el repositorio ya existe
    try:
        ecr_client.describe_repositories(repositoryNames=[repository_name])
        print(f"El repositorio {repository_name} ya existe.")
    except ecr_client.exceptions.RepositoryNotFoundException:
        # Si el repositorio no existe, crearlo
        ecr_client.create_repository(repositoryName=repository_name)
        print(f"Se ha creado el repositorio {repository_name}.")

def build_image_manifest(image_digest):
    manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {
            "digest": image_digest,
            "mediaType": "application/vnd.docker.container.image.v1+json"
        },
        "layers": [
            {
                "digest": "sha256:XXXXXXXXX",
                "size": 12345,
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip"
            },
        ]
    }
    return json.dumps(manifest)

def migrate_last_image(source_repository, destination_repository):
    # Obtener la lista de imágenes en el repositorio fuente
    response = source_ecr_client.describe_images(repositoryName=source_repository)
    image_details = response['imageDetails']

    if not image_details:
        print(f"No hay imágenes en el repositorio {source_repository}.")
        return

    # Obtener la última imagen del repositorio fuente
    latest_image = max(image_details, key=lambda x: x['imagePushedAt'])
    image_digest = latest_image['imageDigest']
    image_tags = latest_image['imageTags'] if 'imageTags' in latest_image else []
    # Obtener la imagen del repositorio fuente
    ImageManifest = build_image_manifest(image_digest)
    print (ImageManifest)
    # Etiquetar la imagen con los mismos tags en el repositorio de destino
    image_tag_input = image_tags[0]

    # Verificar si el repositorio de destino existe y crearlo si no
    create_repository_if_not_exists(destination_ecr_client, destination_repository)

    # Copiar la imagen al repositorio de destino
    source_ecr_client.batch_get_image(repositoryName=source_repository, imageIds=[{'imageDigest': image_digest}])
    destination_ecr_client.put_image(repositoryName=destination_repository, imageManifest=ImageManifest, imageTag=image_tag_input)

    print(f"Migración de la última imagen del repositorio {source_repository} al repositorio {destination_repository} completada.")

# Obtener la lista de repositorios del archivo
repositories_file = 'microservicios.txt'

with open(repositories_file, 'r') as file:
    repositories = file.read().splitlines()

for repository_name in repositories:
     migrate_last_image(repository_name, 'nwm/' + repository_name)

