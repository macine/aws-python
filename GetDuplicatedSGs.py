import boto3
ec2client = boto3.client("ec2")
# Obtiene un dict con todos los SG
SGs=ec2client.describe_security_groups()
# Para cada SG
for sg in SGs["SecurityGroups"]:
    print(sg["GroupId"] + " - " + sg["GroupName"])
    print(sg["IpPermissions"])