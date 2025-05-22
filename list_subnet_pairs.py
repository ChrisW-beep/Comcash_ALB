import boto3
import json

REGION = "us-east-1"

# Initialize Boto3 EC2 client
ec2 = boto3.client("ec2", region_name=REGION)
subnets = ec2.describe_subnets()["Subnets"]

# Group subnet IDs by Availability Zone
az_map = {}
for subnet in subnets:
    az = subnet["AvailabilityZone"]
    subnet_id = subnet["SubnetId"]
    az_map.setdefault(az, []).append(subnet_id)

# Sort AZs for consistency
az_list = sorted(az_map.keys())

# Build labeled subnet pairs
labeled_pairs = []

# Handle pairs across AZs
for i in range(0, len(az_list) - 1, 2):
    az1, az2 = az_list[i], az_list[i + 1]
    s1, s2 = az_map[az1][0], az_map[az2][0]
    label = f'["{s1}", "{s2}"] ({az1} + {az2})'
    labeled_pairs.append(label)

# Optionally handle the last unpaired AZ
if len(az_list) % 2 != 0:
    last_az = az_list[-1]
    if len(az_map[last_az]) >= 2:
        s1, s2 = az_map[last_az][:2]
        label = f'["{s1}", "{s2}"] ({last_az} + {last_az})'
        labeled_pairs.append(label)

# Output JSON list of labeled strings
print(json.dumps(labeled_pairs))
