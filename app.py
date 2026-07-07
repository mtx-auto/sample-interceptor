from aidial_sdk import DIALApp
from aidial_sdk.telemetry.types import TelemetryConfig

from aidial_interceptors_sdk.chat_completion import interceptor_to_chat_completion
from aidial_interceptors_sdk.utils._env import get_env
from aidial_interceptors_sdk.utils._http_client import get_http_client

from sample_interceptor import SampleInterceptor

dial_url = get_env("DIAL_URL")


async def client_factory():
    return get_http_client()


app = DIALApp(
    description="Sample interceptor scaffold",
    dial_url=dial_url,
    telemetry_config=TelemetryConfig(),
    add_healthcheck=True,
    propagate_auth_headers=True,
    allow_extra_request_fields=True,
)

app.add_chat_completion(
    "sample-interceptor",
    interceptor_to_chat_completion(SampleInterceptor, dial_url, client_factory),
)
