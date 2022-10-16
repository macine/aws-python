import boto3
import json

dns_record_name = 'macine-api.multiregion.local'
print ("DNS Record Name: " + dns_record_name)

# Obtiene todas las hosted Zones 
dns_record_names = dns_record_name.split('.')
route53 = boto3.client('route53', region_name='us-east-1')
zones_res = route53.list_hosted_zones()
all_zones = zones_res['HostedZones']
if (zones_res['IsTruncated']):
    while zones_res and (not zones_res['IsTruncated']):
        zones_res = route53.list_hosted_zones(Marker=zones_res['NextMarker'])
        all_zones = all_zones + zones_res['HostedZones']

# Busca la Zone asociada al registro que se obtiene como parámetro
zone_id = None
for i in range(1, len(dns_record_names)-1):
    cur_zone_name = '.'.join(dns_record_names[i:len(dns_record_names)+1]) + '.'
    cur_zone_matches = [zone for zone in all_zones if (zone['Name']==cur_zone_name)]
    if (len(cur_zone_matches) > 0):
        zone_id = cur_zone_matches[0]['Id']
        break
if (not zone_id):
    raise RuntimeError('Route53 zone is not found. DNS name: ' + dns_record_name) from error

# Se obtienen todos los registros de la zona 
RecordSet = route53.list_resource_record_sets(HostedZoneId=zone_id)
str = '{"Changes": ['
i=0
for record in RecordSet["ResourceRecordSets"]:
    if (record["Name"] == dns_record_name + '.'):
        i+=1
        # Si el registro tiene peso los invierte. asumo que existen 2 entradas unicamente.
        match record["Weight"]:
            case 0:
                record["Weight"]=255
            case 255:
                record["Weight"]=0
        if(i>=2): str+=','
        str+='{"Action": "UPSERT","ResourceRecordSet":' + json.dumps(record) + '}'
str += ']}'

result = route53.change_resource_record_sets(HostedZoneId=zone_id,ChangeBatch=json.loads(str))

print(result)
