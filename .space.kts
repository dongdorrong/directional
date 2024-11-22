import circlet.pipelines.script.ScriptApi

fun String.parseVersion(): String? =
    """(\d+\.\d+\.\d+)"""
        .toRegex()
        .findAll(this)
        .lastOrNull()
        ?.value

suspend fun ScriptApi.getVersion(): String? =
    space()
        .projects.repositories
        .commits(
            project = projectIdentifier(),
            repository = gitRepositoryName(),
            query = gitRevision(),
        ).data
        .first()
        .message
        .split("\n")
        .first()
        .parseVersion()

job("Test") {
    startOn {
        gitPush {
            anyRefMatching {
                +"refs/heads/feature/*"
            }
        }
    }

    container(image = "bellsoft/liberica-openjdk-alpine:21") {
        kotlinScript { api ->
            api.gradlew("test")
        }
    }
}

job("Release") {
    startOn {
        gitPush {
            anyRefMatching {
                +"refs/heads/main"
            }
        }
    }

    container(image = "bellsoft/liberica-openjdk-alpine:21") {
        env["HARBOR_REGISTRY"] = "{{ project:HARBOR_REGISTRY }}"
        env["HARBOR_USERNAME"] = "{{ project:HARBOR_ROBOT_ACCOUNT_USERNAME }}"
        env["HARBOR_TOKEN"] = "{{ project:HARBOR_ROBOT_ACCOUNT_TOKEN }}"

        kotlinScript { api ->
            val version = api.getVersion() ?: return@kotlinScript

            api.space().projects.automation.deployments.start(
                project = api.projectIdentifier(),
                targetIdentifier = TargetIdentifier.Key(api.gitRepositoryName()),
                version = version,
                syncWithAutomationJob = true,
            )

            api.gradlew("bootBuildImage")
        }
    }
}
