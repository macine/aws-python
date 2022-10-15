import boto3

dns_record_name = 'macine-api.multiregion.local'
dns_record_names = dns_record_name.split('.')


route53 = boto3.client('route53', region_name='us-east-1')
zones_res = route53.list_hosted_zones()
all_zones = zones_res['HostedZones']
if (zones_res['IsTruncated']):
    while zones_res and (not zones_res['IsTruncated']):
        zones_res = route53.list_hosted_zones(Marker=zones_res['NextMarker'])
        all_zones = all_zones + zones_res['HostedZones']
print (all_zones)

zone_id = None
for i in range(1, len(dns_record_names)-1):
    cur_zone_name = '.'.join(dns_record_names[i:len(dns_record_names)+1]) + '.'
    cur_zone_matches = [zone for zone in all_zones if (zone['Name']==cur_zone_name)]
    if (len(cur_zone_matches) > 0):
        zone_id = cur_zone_matches[0]['Id']
        break
if (not zone_id):
    raise RuntimeError('Route53 zone is not found. DNS name: ' + dns_record_name) from error
else:
    print (zone_id)
