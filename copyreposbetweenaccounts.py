import boto3

source_profile        = 'NWPDESA-RolesIAM'  # Perfil de AWS para la cuenta de origen
destination_profile   = 'ARQ-ADMIN'  # Perfil de AWS para la cuenta de destino
source_registry      = "495242821145.dkr.ecr.us-east-1.amazonaws.com"
destination_registry = "279527989600.dkr.ecr.us-east-1.amazonaws.com"



def create_repository_if_not_exists(repository_name):
    # Configurar el perfil y cliente de AWS
    profile = 'perfil_destino'  # Perfil de AWS para la cuenta de destino
    ecr_client = boto3.Session(profile_name=profile).client('ecr')

    # Verificar si el repositorio ya existe
    try:
        ecr_client.describe_repositories(repositoryNames=[repository_name])
        print(f"El repositorio {repository_name} ya existe.")
    except ecr_client.exceptions.RepositoryNotFoundException:
        # Si el repositorio no existe, crearlo
        ecr_client.create_repository(repositoryName=repository_name)
        print(f"Se ha creado el repositorio {repository_name}.")

def migrate_last_image(repository_name):
    # Configurar los perfiles y clientes de AWS

    source_ecr_client = boto3.Session(profile_name=source_profile).client('ecr')
    destination_ecr_client = boto3.Session(profile_name=destination_profile).client('ecr')

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
    source_image = f"{source_repository}@{image_digest}"

    # Etiquetar la imagen con los mismos tags en el repositorio de destino
    image_tag_input = [{'imageTag': tag} for tag in image_tags]

    # Verificar si el repositorio de destino existe y crearlo si no
    create_repository_if_not_exists(destination_repository)

    # Copiar la imagen al repositorio de destino
    source_ecr_client.batch_get_image(repositoryName=source_repository, imageIds=[{'imageDigest': image_digest}])
    destination_ecr_client.put_image(repositoryName=destination_repository, imageManifest=source_image, imageTagInput=image_tag_input)

    print(f"Migración de la última imagen del repositorio {source_repository} al repositorio {destination_repository} completada.")

# Obtener la lista de repositorios del archivo
repositories_file = 'microservicios.txt'

with open(repositories_file, 'r') as file:
    repositories = file.read().splitlines()

# Uso del script
for repository_name in repositories:
    migrate_last_image(repository_name)
