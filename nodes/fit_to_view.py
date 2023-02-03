# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class FitToView(iograft.Node):
    """
    Fit the requested camera to frame items in the scene. If `all_objects`
    is True, fit all objects in the scene. Otherwise, only fit selected
    objects.
    """
    camera = iograft.InputDefinition("camera", iobasictypes.String(),
                                     default_value="")
    all_objects = iograft.InputDefinition("all_objects", iobasictypes.Bool(),
                                          default_value=True)
    fit_factor = iograft.InputDefinition("fit_factor", iobasictypes.Double(),
                                         default_value=1.0)
    center_only = iograft.InputDefinition("center_only", iobasictypes.Bool(),
                                          default_value=False)

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("fit_to_view")
        node.SetMenuPath("Maya")
        node.AddInput(cls.camera)
        node.AddInput(cls.all_objects)
        node.AddInput(cls.fit_factor)
        node.AddInput(cls.center_only)
        return node

    @staticmethod
    def Create():
        return FitToView()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        camera = iograft.GetInput(self.camera, data)
        all_objects = iograft.GetInput(self.all_objects, data)
        fit_factor = iograft.GetInput(self.fit_factor, data)
        center_only = iograft.GetInput(self.center_only, data)

        # If the camera input is empty, the current view is used, so don't
        # pass the camera arg to viewFit.
        fit_args = []
        if camera:
            fit_args.append(camera)

        # Set the additional args to the viewFit command.
        fit_kwargs = {
            "fitFactor": fit_factor,
            "center": center_only,
            "allObjects": all_objects
        }

        # Run the fit command.
        maya.cmds.viewFit(*fit_args, **fit_kwargs)


def LoadPlugin(plugin):
    node = FitToView.GetDefinition()
    plugin.RegisterNode(node, FitToView.Create)
