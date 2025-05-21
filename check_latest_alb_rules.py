import boto3
import os
from botocore.exceptions import ClientError

MAX_RULES_PER_ALB = 100
WARN_THRESHOLD = 90  # Change this as needed

def get_latest_alb(elbv2):
    lbs = elbv2.describe_load_balancers()["LoadBalancers"]
    if not lbs:
        raise Exception("No ALBs found.")

    # Sort by creation time
    latest_lb = sorted(lbs, key=lambda lb: lb["CreatedTime"], reverse=True)[0]
    return latest_lb["LoadBalancerArn"], latest_lb["DNSName"]

def count_rules_for_alb(elbv2, alb_arn):
    listeners = elbv2.describe_listeners(LoadBalancerArn=alb_arn)["Listeners"]
    total_rules = 0

    for listener in listeners:
        rules = elbv2.describe_rules(ListenerArn=listener["ListenerArn"])["Rules"]
        total_rules += len(rules)

    return total_rules

def main():
    region = os.getenv("AWS_REGION", "us-east-1")

    session = boto3.Session()
    elbv2 = session.client("elbv2", region_name=region)

    try:
        alb_arn, alb_dns = get_latest_alb(elbv2)
        rule_count = count_rules_for_alb(elbv2, alb_arn)
        rules_left = MAX_RULES_PER_ALB - rule_count

        print(f"📊 Latest ALB: {alb_dns}")
        print(f"✅ Rule count: {rule_count} / {MAX_RULES_PER_ALB}")
        print(f"🧮 Rules remaining: {rules_left}")

        if rule_count >= MAX_RULES_PER_ALB:
            print("❌ Rule limit reached!")
            exit(2)
        elif rule_count >= WARN_THRESHOLD:
            print("⚠️ Approaching rule limit.")
            exit(1)
        else:
            print("✅ Rule usage is healthy.")
            exit(0)

    except ClientError as e:
        print(f"AWS Error: {e}")
        exit(3)
    except Exception as e:
        print(f"Error: {e}")
        exit(4)

if __name__ == "__main__":
    main()
