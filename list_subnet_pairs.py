import boto3, json

ec2 = boto3.client('ec2', region_name='us-east-1')
subnets = ec2.describe_subnets()['Subnets']

# Group by Availability Zone
az_map = {}
for s in subnets:
    az = s['AvailabilityZone']
    az_map.setdefault(az, []).append(s['SubnetId'])

# Output pairs as JSON list
pairs = []
az_list = sorted(az_map.keys())
for i in range(0, len(az_list) - 1, 2):
    s1 = az_map[az_list[i]][0]
    s2 = az_map[az_list[i+1]][0]
    pairs.append([s1, s2])

print(json.dumps(pairs))
