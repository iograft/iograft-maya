# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class ParentObjects(iograft.Node):
    """
    Parent the given objects to the object provided. The default behavior
    is to do an "absolute" parenting to preserve the existing world object
    transformations. If the `parent` input is an empty string, all objects
    will be unparented (i.e. parented to world).
    """
    objects = iograft.InputDefinition("objects", iobasictypes.StringList())
    parent = iograft.InputDefinition("parent", iobasictypes.String())
    preserve_position = iograft.InputDefinition("preserve_position",
                                                iobasictypes.Bool(),
                                                default_value=True)

    # Output a list of objects since the input objects might
    # be renamed by the parenting operation.
    objects_out = iograft.OutputDefinition("objects", iobasictypes.StringList())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("parent_objects")
        node.SetNamespace("maya")
        node.SetMenuPath("Maya")
        node.AddInput(cls.objects)
        node.AddInput(cls.parent)
        node.AddInput(cls.preserve_position)
        node.AddOutput(cls.objects_out)
        return node

    @staticmethod
    def Create():
        return ParentObjects()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        objects = iograft.GetInput(self.objects, data)
        parent = iograft.GetInput(self.parent, data)
        preserve_position = iograft.GetInput(self.preserve_position, data)

        # Don't do anything if the input list of objects is empty. The `parent`
        # command by default will use selected objects in that case, but in
        # the context of nodes, we don't want to rely on selection state.
        if not objects:
            iograft.SetOutput(self.objects_out, data, objects)

        # Build the args to the command.
        args = [objects]
        kwargs = {}
        if parent:
            args.append(parent)
        else:
            # If there is no parent, then this should be considered an
            # unparenting operation.
            kwargs["world"] = True

        if not preserve_position:
            kwargs["relative"] = True

        # Do the parenting operation. Store the output object names because
        # some of them might have been renamed by this operation (i.e. if
        # there was already an object with the same name under the new
        # parent).
        objects_out = maya.cmds.parent(*args, **kwargs)

        # The parent command modifies the selection state, so clear that
        # state here.
        # TODO: Should we save the previous selection and restore it here?
        maya.cmds.select(clear=True)

        # Set the output object list. Use the full paths to the objects.
        objects_out = maya.cmds.ls(objects_out, long=True)
        iograft.SetOutput(self.objects_out, data, objects_out)


def LoadPlugin(plugin):
    node = ParentObjects.GetDefinition()
    plugin.RegisterNode(node, ParentObjects.Create)
