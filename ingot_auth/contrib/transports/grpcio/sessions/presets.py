"""The servicer of the presets of the sessions."""

__all__ = ("AuthGrpcSessionPresetsServicer",)

import typing as t

from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.sessions.presets import AuthSessionPreset, AuthSessionPresetBinding
from ingot_auth.sessions.presets.operations import AuthUnbindSessionAttrParameters

from ..base import BaseAuthGrpcServicer, Context
from ..proto.ingot_auth.sessions.presets.v1 import presets_pb2, presets_pb2_grpc


class AuthGrpcSessionPresetsServicer(
    BaseAuthGrpcServicer, presets_pb2_grpc.PresetsServicer
):
    """
    The presets of the sessions with their bindings for their administrator:
    its permissions come from :meth:`_get_caller`, which a subclass overrides,
    so an application serves this only to those it can tell apart.
    """

    @t.override
    async def Create(
        self, request: presets_pb2.CreatePresetRequest, context: Context
    ) -> presets_pb2.CreatePresetResponse:
        preset = AuthSessionPreset(id=request.preset.id, name=request.preset.name)
        factory = self.project.auth.sessions.presets.op_create
        created = await self.run_operation(factory, preset, context)
        return presets_pb2.CreatePresetResponse(preset=build_preset_message(created))

    @t.override
    async def List(
        self, request: presets_pb2.ListPresetsRequest, context: Context
    ) -> presets_pb2.ListPresetsResponse:
        factory = self.project.auth.sessions.presets.op_list
        presets = await self.run_operation(factory, None, context)
        return presets_pb2.ListPresetsResponse(
            presets=map(build_preset_message, presets)
        )

    @t.override
    async def Rename(
        self, request: presets_pb2.RenamePresetRequest, context: Context
    ) -> presets_pb2.RenamePresetResponse:
        parameters = AuthRenameItemParameters(id=request.id, name=request.name)
        factory = self.project.auth.sessions.presets.op_rename
        renamed = await self.run_operation(factory, parameters, context)
        return presets_pb2.RenamePresetResponse(preset=build_preset_message(renamed))

    @t.override
    async def Delete(
        self, request: presets_pb2.DeletePresetRequest, context: Context
    ) -> presets_pb2.DeletePresetResponse:
        parameters = AuthDeleteItemParameters(id=request.id)
        factory = self.project.auth.sessions.presets.op_delete
        await self.run_operation(factory, parameters, context)
        return presets_pb2.DeletePresetResponse()

    @t.override
    async def Bind(
        self, request: presets_pb2.BindAttrRequest, context: Context
    ) -> presets_pb2.BindAttrResponse:
        message = request.binding
        binding = AuthSessionPresetBinding(
            preset_id=message.preset_id,
            attr_id=message.attr_id,
            required=message.required,
        )
        factory = self.project.auth.sessions.presets.op_bind
        bound = await self.run_operation(factory, binding, context)
        return presets_pb2.BindAttrResponse(binding=build_binding_message(bound))

    @t.override
    async def Unbind(
        self, request: presets_pb2.UnbindAttrRequest, context: Context
    ) -> presets_pb2.UnbindAttrResponse:
        parameters = AuthUnbindSessionAttrParameters(
            preset_id=request.preset_id, attr_id=request.attr_id
        )
        factory = self.project.auth.sessions.presets.op_unbind
        await self.run_operation(factory, parameters, context)
        return presets_pb2.UnbindAttrResponse()

    @t.override
    async def ListBindings(
        self, request: presets_pb2.ListBindingsRequest, context: Context
    ) -> presets_pb2.ListBindingsResponse:
        factory = self.project.auth.sessions.presets.op_list_bindings
        bindings = await self.run_operation(factory, None, context)
        return presets_pb2.ListBindingsResponse(
            bindings=map(build_binding_message, bindings)
        )


def build_preset_message(preset: AuthSessionPreset) -> presets_pb2.Preset:
    """Internal: the message of a preset."""
    return presets_pb2.Preset(id=preset.id, name=preset.name)


def build_binding_message(
    binding: AuthSessionPresetBinding,
) -> presets_pb2.Binding:
    """Internal: the message of a binding."""
    return presets_pb2.Binding(
        preset_id=binding.preset_id,
        attr_id=binding.attr_id,
        required=binding.required,
    )
