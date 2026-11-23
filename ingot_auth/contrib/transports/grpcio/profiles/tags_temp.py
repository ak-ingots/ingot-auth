"""
The servicer of the tags, of :mod:`ingot_auth.api`. Temporary: its names
suffixed ``Temp``, its services bound as ``*_temp`` beside the old ones,
till the old API is removed.
"""

__all__ = ("AuthGrpcTagsServicerTemp",)

import typing as t

from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.storages import AuthTag

from ..base import BaseAuthGrpcServicer, Context
from ingot_auth.api.profiles.tags.v1 import tags_pb2, tags_pb2_grpc


class AuthGrpcTagsServicerTemp(BaseAuthGrpcServicer, tags_pb2_grpc.TagsServicer):
    """
    The tags for their administrator: its permissions are those of the
    session of the token of the call, by :meth:`_get_caller`.
    """

    @t.override
    async def CreateTag(
        self, request: tags_pb2.CreateTagRequest, context: Context
    ) -> tags_pb2.CreateTagResponse:
        tag = AuthTag(uid=request.tag.uid, name=request.tag.name)
        factory = self.project.auth.profiles.tags.op_create
        created = await self.run_operation(factory, tag, context)
        return tags_pb2.CreateTagResponse(tag=build_tag_message(created))

    @t.override
    async def ListTags(
        self, request: tags_pb2.ListTagsRequest, context: Context
    ) -> tags_pb2.ListTagsResponse:
        tags = await self.run_operation(
            self.project.auth.profiles.tags.op_list, None, context
        )
        return tags_pb2.ListTagsResponse(tags=map(build_tag_message, tags))

    @t.override
    async def RenameTag(
        self, request: tags_pb2.RenameTagRequest, context: Context
    ) -> tags_pb2.RenameTagResponse:
        parameters = AuthRenameItemParameters(uid=request.uid, name=request.name)
        factory = self.project.auth.profiles.tags.op_rename
        renamed = await self.run_operation(factory, parameters, context)
        return tags_pb2.RenameTagResponse(tag=build_tag_message(renamed))

    @t.override
    async def DeleteTag(
        self, request: tags_pb2.DeleteTagRequest, context: Context
    ) -> tags_pb2.DeleteTagResponse:
        parameters = AuthDeleteItemParameters(uid=request.uid)
        factory = self.project.auth.profiles.tags.op_delete
        await self.run_operation(factory, parameters, context)
        return tags_pb2.DeleteTagResponse()


def build_tag_message(tag: AuthTag) -> tags_pb2.Tag:
    """Internal: the message of a tag."""
    return tags_pb2.Tag(uid=tag.uid, name=tag.name)
