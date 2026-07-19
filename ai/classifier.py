import json
import boto3

def classify_complaint(description, category_hint=None):
    """
    Classify a complaint using AWS Bedrock LLM via boto3.
    Uses standard AWS credentials from environment or IAM role.
    
    Args:
        description: Complaint description text
        category_hint: Optional hint about the category
    
    Returns:
        dict with keys: issue_type, severity, assigned_authority
    """
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    system_prompt = "You are a civic complaint classifier. Given a description, return strict JSON with keys: issue_type (one of: pothole, streetlight, garbage, illegal_dumping, blocked_drain, waterlogging, exposed_wire, unsafe_area, encroachment, road_damage), severity (routine or life_threatening - mark life_threatening ONLY for exposed_wire, gas leak, open manhole, live wire in water), assigned_authority (one of: BMC Roads Department, BMC Electrical Department, BMC Solid Waste Management, BMC Storm Water Drainage, Local Police - Traffic & Safety). No explanation, JSON only."
    
    user_message = f"Classify this complaint: {description}"
    if category_hint:
        user_message += f"\nCategory hint: {category_hint}"
    
    response = client.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        contentType='application/json',
        accept='application/json',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-06-01',
            'max_tokens': 1024,
            'system': system_prompt,
            'messages': [
                {
                    'role': 'user',
                    'content': user_message
                }
            ]
        })
    )
    
    response_body = json.loads(response['body'].read().decode('utf-8'))
    response_text = response_body['content'][0]['text'].strip()
    result = json.loads(response_text)
    
    return result
