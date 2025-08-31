from typing import Dict, Generic, List, TypeVar, Union

from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Type générique pour les données
T = TypeVar("T")

# Documentation: https://jsonapi.org/examples/


class JSONAPIResource(BaseModel, Generic[T]):
    """Individual resource in JSON:API format"""

    type: str
    id: str
    attributes: T


class JSONAPISuccessResponse(BaseModel, Generic[T]):
    """Success response following JSON:API spec"""

    data: Union[JSONAPIResource[T], List[JSONAPIResource[T]]]


class JSONAPIErrorResponse(BaseModel):
    """Error response following JSON:API spec"""

    error: Dict[str, str]


def create_success_response(
    resource_type: str, resource_id: str, attributes: dict
) -> JSONResponse:
    """Create a success response for a single resource"""

    def serialize_value(value):
        """Convert datetime objects to ISO strings for JSON serialization"""
        if hasattr(value, "isoformat"):  # datetime objects
            return value.isoformat()
        return value

    # Serialize all attributes
    serialized_attributes = {k: serialize_value(v) for k, v in attributes.items()}

    return JSONResponse(
        content={
            "data": {
                "type": resource_type,
                "id": resource_id,
                "attributes": serialized_attributes,
            }
        },
        media_type="application/json",
    )


def create_success_response_list(
    resource_type: str, resources: List[dict]
) -> JSONResponse:
    """Create a success response for multiple resources"""

    def _serialize_value(value):
        """Convert datetime objects to ISO strings for JSON serialization"""
        if hasattr(value, "isoformat"):  # datetime objects
            return value.isoformat()
        return value

    data = []
    for resource in resources:
        # Check if resource is already in JSON:API format
        if "type" in resource and "attributes" in resource:
            # Resource is already formatted, just serialize it
            serialized_resource = {
                "type": resource["type"],
                "attributes": {
                    k: _serialize_value(v) for k, v in resource["attributes"].items()
                },
            }

            if "id" in resource:
                serialized_resource["id"] = str(resource["id"])

            data.append(serialized_resource)
        else:
            # Resource is raw data, format it
            resource_id = str(resource.get("id", ""))

            # Serialize each resource's attributes
            serialized_attributes = {
                k: _serialize_value(v) for k, v in resource.items() if k != "id"
            }

            res = {
                "type": resource_type,
                "attributes": serialized_attributes,
            }

            if resource_id:
                res.update(id=resource_id)

            data.append(res)

    return JSONResponse(content={"data": data}, media_type="application/json")


def create_error_response(
    status: str, title: str, detail: str | list[str], status_code: int = 400
) -> JSONResponse:
    """Create an error response conforming to JSON:API (array of errors)"""
    # Ensure detail is a list of strings
    if isinstance(detail, str):
        detail = [detail]

    response = {
        "errors": [{"status": status, "title": title, "detail": d} for d in detail]
    }

    return JSONResponse(
        content=response,
        media_type="application/json",
        status_code=status_code,
    )
