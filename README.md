# directional

Dockerfile
- 쿠버네티스 환경에서 네트워크, DB 접근 같은 테스트를 할 때 사용하려고 만든 이미지

ecs_task_stop_alert.py
- ECS TASK 상태에 따른 Slack 알람을 Lambda 함수로 작성

set_harbor_credentials.sh
- Harbor 레포지토리에 접근할 수 있는 Robot Account에 대한 액세스 키, 시크릿 키를 쿠버네티스 Secret 리소스로 만드는 스크립트 

set_keyclaok_credentials.sh
- kube-apiserver 접근을 keycloak oidc로 구성하고, keycloak 계정을 통해서 kubectl config 설정을 해주는 스크립트

springboot_build_and_run.sh
- Local 환경이나 인스턴스 내부에서 Spring Boot 프로젝트를 pull 받아서 작업하는 경우, 빌드와 실행을 해주는 스크립트