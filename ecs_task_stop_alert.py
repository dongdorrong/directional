import json
import urllib.request
import os

def send_slack_message(slack_webhook_url, message):
    message.update({
        "username": "aws",
        "icon_emoji": ":aws_logo:",
    })
    data = json.dumps(message).encode('utf-8')
    req = urllib.request.Request(slack_webhook_url, data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return response.read()

def lambda_handler(event, context):
    # # event 인자의 값 로깅
    # print("[DevOps] Received event: " + json.dumps(event))

    slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']
    
    # SNS 메시지에서 'Message' 항목 추출 및 파싱
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    detail = sns_message['detail']

    # SNS Message 값 로깅
    print("[DevOps] SNS Message:", sns_message)

    # region 추출
    region_code = sns_message['region']

    try:
        stop_code = detail.get('stopCode', 'N/A')
        task_id = detail.get('taskArn', 'N/A').split('/')[-1]
        task_definition = detail.get('taskDefinitionArn', 'N/A').split('/')[-1]
        cluster_name = detail.get('clusterArn', 'N/A').split('/')[-1]
        ecs_service_name = detail.get('group', 'N/A').split(':')[1]
        container_reason = "N/A"

        # 'EssentialContainerExited'인 경우, 컨테이너의 'reason'을 검사합니다.
        if stop_code == 'EssentialContainerExited':
            found_reason = False  # 컨테이너의 'reason'을 찾았는지 여부
            for container in detail.get('containers', []):
                if 'reason' in container:
                    container_reason = container['reason']
                    found_reason = True
                    break  # 첫 번째 발견된 이유를 사용
            # 컨테이너에서 'reason'을 찾지 못한 경우, 최상위 'stoppedReason'을 사용합니다.
            if not found_reason:
                container_reason = detail.get('stoppedReason', '중단 사유를 알 수 없습니다. Cloudwatch 로그를 확인하세요.')
    except KeyError as e:
        # 필요한 키가 없을 경우 처리
        print(f"Key error: {e}")
        message_text = "Lambda 함수에서 필요한 정보를 추출하는 중 에러가 발생했습니다."

    # 링크 구성
    aws_webconsole_link = f"https://{region_code}.console.aws.amazon.com/ecs/v2/clusters/{cluster_name}/tasks/{task_id}/configuration?region={region_code}#"
    message_link_text   = f"<{aws_webconsole_link}|AWS Web Console로 이동>"
    
    # 기본 메시지 구성
    base_message        = f"Cluster Name: {cluster_name}\nECS Service Name: {ecs_service_name}\nTask Definition: {task_definition}\nTask ID: {task_id}\nStop Code: {stop_code}\n\n"

    if stop_code == 'SpotInterruption':
        # message_subject = ":information_source: *INFORMATION* - Task 종료"
        message_subject = f"<{aws_webconsole_link}|:information_source: *INFORMATION* - Task 종료>"
        message_text    = base_message + "Spot 자원 회수되어 기존 TASK가 중단됩니다.\n"
    elif stop_code == 'ServiceSchedulerInitiated':
        # message_subject = ":information_source: *INFORMATION* - Task 종료"
        message_subject = f"<{aws_webconsole_link}|:information_source: *INFORMATION* - Task 종료>"
        message_text    = base_message + "배포로 인해 기존 TASK가 중단됩니다.\n"
    elif stop_code == 'EssentialContainerExited':
        # message_subject = ":alert: *FATAL* - 컨테이너 종료"
        message_subject = f"<{aws_webconsole_link}|:alert: *FATAL* - 컨테이너 종료>"
        message_text   = base_message + f"종료 이유: {container_reason}."
    else:
        # message_subject = ":warning: *WARNING* - 일반 작업 중단"
        message_subject = f"<{aws_webconsole_link}|:warning: *WARNING* - 일반 작업 중단>"
        message_text   = base_message + f"작업이 중단되었습니다. 상세 정보를 확인하고 적절한 조치를 취하세요.\n"

    message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message_subject
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message_text
                }
            }
        ]
    }
    
    send_slack_message(slack_webhook_url, message)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Slack message sent based on stopCode with detailed information')
    }
