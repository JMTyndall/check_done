from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, field_validator


class NodesTypeName(StrEnum):
    CustomField = "CustomField"
    MultiUserIssueCustomField = "MultiUserIssueCustomField"
    PeriodProjectCustomField = "PeriodProjectCustomField"
    PeriodIssueCustomField = "PeriodIssueCustomField"
    ProjectTimeTrackingSettings = "ProjectTimeTrackingSettings"
    SingleUserIssueCustomField = "SingleUserIssueCustomField"


class ProjectItemState(StrEnum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"


class GithubContentType(StrEnum):
    ISSUE = "ISSUE"
    PULL_REQUEST = "PULL_REQUEST"


class _EmptyDict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PageInfo(BaseModel):
    endCursor: str
    hasNextPage: bool


class PaginatedQueryInfo(BaseModel):
    nodes: list[Any]
    page_info: PageInfo = Field(alias="pageInfo")

    @field_validator("nodes", mode="after", check_fields=True)
    def validate_each_node(cls, nodes: list[Any]):
        validated_nodes = []
        for node in nodes:
            node_type = node.get("__typename")
            if node.get("__typename") in _NODE_TYPE_NAME_TO_INFO_CLASS_MAP:
                node_model = _NODE_TYPE_NAME_TO_INFO_CLASS_MAP.get(node_type)
                validated_nodes.append(node_model(**node))
        return validated_nodes


class ProjectV2NodeInfo(BaseModel):
    id: str
    number: NonNegativeInt
    typename: str = Field(alias="__typename")
    fields: PaginatedQueryInfo | None = None
    items: PaginatedQueryInfo | None = None


class ProjectV2Options(BaseModel):
    id: str
    name: str


class ProjectV2SingleSelectFieldNodeInfo(BaseModel):
    id: str
    name: str
    typename: str = Field(alias="__typename")
    options: list[ProjectV2Options]


class ProjectV2ItemProjectStatusInfo(BaseModel):
    status: str
    option_id: str = Field(alias="optionId")


class RepositoryInfo(BaseModel):
    name: str


class AssigneesInfo(BaseModel):
    total_count: NonNegativeInt = Field(alias="totalCount")


class MilestoneInfo(BaseModel):
    id: str


class ProjectItemInfo(BaseModel):
    assignees: AssigneesInfo
    closed: bool
    number: NonNegativeInt
    repository: RepositoryInfo
    milestone: MilestoneInfo | None
    title: str


class ProjectV2ItemNodeInfo(BaseModel):
    type: GithubContentType
    # TODO#4: When including pull requests, implement their info model
    #  See: https://docs.github.com/en/graphql/reference/unions#projectv2itemcontent
    content: ProjectItemInfo | _EmptyDict = None
    field_value_by_name: ProjectV2ItemProjectStatusInfo | None = Field(alias="fieldValueByName", default=None)


class NodeByIdInfo(BaseModel):
    node: ProjectV2NodeInfo


class _ProjectsV2Info(BaseModel):
    projects_v2: PaginatedQueryInfo = Field(alias="projectsV2")


class OrganizationInfo(BaseModel):
    organization: _ProjectsV2Info


class _NodeTypeName(StrEnum):
    ProjectV2 = "ProjectV2"
    ProjectV2SingleSelectField = "ProjectV2SingleSelectField"
    ProjectV2Item = "ProjectV2Item"


_NODE_TYPE_NAME_TO_INFO_CLASS_MAP = {
    _NodeTypeName.ProjectV2.value: ProjectV2NodeInfo,
    _NodeTypeName.ProjectV2SingleSelectField.value: ProjectV2SingleSelectFieldNodeInfo,
    _NodeTypeName.ProjectV2SingleSelectField.ProjectV2Item: ProjectV2ItemNodeInfo,
}
