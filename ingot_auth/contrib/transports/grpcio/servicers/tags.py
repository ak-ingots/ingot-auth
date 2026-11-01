"""The servicer of the tags."""

__all__ = ("AuthGrpcTagsServicer",)

import typing as t

from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.tags import AuthTag

from ..proto.ingot_auth.v1 import tags_pb2, tags_pb2_grpc
from .base import BaseAuthGrpcServicer, Context


class AuthGrpcTagsServicer(BaseAuthGrpcServicer, tags_pb2_grpc.TagsServicer):
    """
    The tags for their administrator: its permissions come from
    :meth:`_get_caller`, which a subclass overrides, so an application serves
    this only to those it can tell apart.
    """

    @t.override
    async def Create(
        self, request: tags_pb2.CreateTagRequest, context: Context
    ) -> tags_pb2.CreateTagResponse:
        tag = AuthTag(id=request.tag.id, name=request.tag.name)
        factory = self.project.auth.tags.op_create
        created = await self.run_operation(factory, tag, context)
        return tags_pb2.CreateTagResponse(tag=build_tag_message(created))

    @t.override
    async def List(
        self, request: tags_pb2.ListTagsRequest, context: Context
    ) -> tags_pb2.ListTagsResponse:
        tags = await self.run_operation(self.project.auth.tags.op_list, None, context)
        return tags_pb2.ListTagsResponse(tags=map(build_tag_message, tags))

    @t.override
    async def Rename(
        self, request: tags_pb2.RenameTagRequest, context: Context
    ) -> tags_pb2.RenameTagResponse:
        parameters = AuthRenameItemParameters(id=request.id, name=request.name)
        factory = self.project.auth.tags.op_rename
        renamed = await self.run_operation(factory, parameters, context)
        return tags_pb2.RenameTagResponse(tag=build_tag_message(renamed))

    @t.override
    async def Delete(
        self, request: tags_pb2.DeleteTagRequest, context: Context
    ) -> tags_pb2.DeleteTagResponse:
        parameters = AuthDeleteItemParameters(id=request.id)
        factory = self.project.auth.tags.op_delete
        await self.run_operation(factory, parameters, context)
        return tags_pb2.DeleteTagResponse()


def build_tag_message(tag: AuthTag) -> tags_pb2.Tag:
    """Internal: the message of a tag."""
    return tags_pb2.Tag(id=tag.id, name=tag.name)
