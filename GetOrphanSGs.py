import boto3
ec2client = boto3.client("ec2")
# Obtiene un dict con todos los SG
SGs=ec2client.describe_security_groups()
# Para cada SG
for sg in SGs["SecurityGroups"]:
    # el Default SG no se puede borrar, lo ignoramos
    if(sg["GroupName"]!="default"):
        # obtengo los Network Interfaces que usen el Security Group
        filters= [{'Name':'group-id', 'Values': [sg["GroupId"]]}]
        NIs=ec2client.describe_network_interfaces(Filters=filters)
        # Nº de NIs asociadas al SG
        Nis_x_SG = len(NIs["NetworkInterfaces"])
        # Si este valor es cero el SG no está en uso
        if(Nis_x_SG==0):
            print(sg["GroupId"] + " - " + sg["GroupName"])
