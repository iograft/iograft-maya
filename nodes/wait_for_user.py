# Copyright 2022 Fabrica Software, LLC

# This file contains an example of a node that makes use of Maya's Qt
# framework to display a dialog to the user asking if she/he would like to
# continue or cancel execution. Using Maya's executeInMainThreadWithResult
# function, this node is non-blocking, allowing the user to continue to
# interact with both Maya and iograft while the dialog is being shown. The
# dialog also passes back the result of the dialog (cancelled or not) to
# the node so execution can be cancelled if requested.

import iograft
import iobasictypes
import iogmaya_ui

from PySide2 import QtCore, QtWidgets


class WaitForUserDialog(QtWidgets.QDialog):
    """
    A simple Qt Dialog asking the user if they would like to continue.
    """
    def __init__(self,
                 parent=None,
                 title="Waiting for user confirmation",
                 message="Please click continue when ready.",
                 ok_button_text="Continue",
                 cancel_button_text="Cancel"):
        super(WaitForUserDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.Tool)
        self.setMinimumWidth(250)

        # Build the layout for the dialog.
        self.layout = QtWidgets.QVBoxLayout()
        self.message_label = QtWidgets.QLabel(message)
        self.layout.addWidget(self.message_label)

        # Create the action buttons to control the user interactions with
        # the dialog.
        buttons = \
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.button_box = QtWidgets.QDialogButtonBox(buttons)
        self.button_box.button(
                QtWidgets.QDialogButtonBox.Ok).setText(ok_button_text)
        self.button_box.button(
                QtWidgets.QDialogButtonBox.Cancel).setText(cancel_button_text)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)


class DialogFinishedHook(QtCore.QObject):
    """
    The DialogFinishedHook coordinates the data passing and state between
    the node's processing thread and Maya's UI thread. In this example
    the hook signals when the UI is finished as well as whether the dialog
    was cancelled. Additional data could be added to this class to pass that
    data back to the node.
    """
    finished = QtCore.Signal()

    def __init__(self):
        super(DialogFinishedHook, self).__init__()
        self.cancelled = False

    def cancel(self):
        self.cancelled = True
        self.finished.emit()


def display_dialog(hook, **kwargs):
    """
    Create the dialog, make the necessary connections to the hook, and show
    the dialog. This is the main entry point to show the dialog and is
    called by the executeInMainThreadWithResult function.
    """
    dialog = WaitForUserDialog(iogmaya_ui.get_main_window(), **kwargs)
    dialog.accepted.connect(hook.finished)
    dialog.rejected.connect(hook.cancel)

    # Show the dialog.
    iogmaya_ui.ensure_window_shown(dialog)


class WaitForUser(iograft.Node):
    """
    Pop up a Qt dialog within Maya prompting the user if they would like
    to continue. When processing non-interactively, this node has no effect.
    """
    title = iograft.InputDefinition("title", iobasictypes.String(),
                                    default_value="Waiting for confirmation")
    message = iograft.InputDefinition("message", iobasictypes.String(),
                default_value="Please click continue when ready to proceed.")
    ok_button_text = iograft.InputDefinition("ok_button_text",
                                             iobasictypes.String(),
                                             default_value="Continue")
    cancel_button_text = iograft.InputDefinition("cancel_button_text",
                                                 iobasictypes.String(),
                                                 default_value="Cancel")

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("wait_for_user")
        node.AddInput(cls.title)
        node.AddInput(cls.message)
        node.AddInput(cls.ok_button_text)
        node.AddInput(cls.cancel_button_text)
        return node

    @staticmethod
    def Create():
        return WaitForUser()

    def Process(self, data):
        import maya.cmds

        # If we are executing Maya in batch mode, we cannot prompt the
        # user with a Qt window, so return immediately.
        if maya.cmds.about(batch=1):
            return

        # Get the input values containing the desired content of the dialog.
        dialog_content = {
            "title": iograft.GetInput(self.title, data),
            "message": iograft.GetInput(self.message, data),
            "ok_button_text": iograft.GetInput(self.ok_button_text, data),
            "cancel_button_text": iograft.GetInput(self.cancel_button_text, data)
        }

        # Create an event loop so we can wait for the dialog to be closed,
        # signaling that the node should be complete. This is the main concept
        # behind how this node can leave both iograft and Maya in a
        # non-blocking state. Notice that the Process() function does not
        # have the usual "maya_main_thread" decorator. We want this node to
        # execute in a secondary thread. It then launches the dialog in the
        # main thread using Maya's "executeInMainThreadWithResult" function
        # and uses Qt signals to know when then dialog has been closed.
        event_loop = QtCore.QEventLoop()

        # Create a "hook" to be used to signal when the dialog is closed.
        # The dialog must trigger the hook's "finished" signal in order to
        # exit the event loop.
        hook = DialogFinishedHook()
        hook.finished.connect(event_loop.quit)

        # Launch the dialog in the main thread, and wait for the hook to
        # be signaled.
        import maya.utils
        maya.utils.executeInMainThreadWithResult(display_dialog,
                                                 hook,
                                                 **dialog_content)
        event_loop.exec_()

        # In this case, if the dialog was cancelled, we want to raise
        # an exception to stop the iograft processing.
        if hook.cancelled:
            raise Exception("User cancelled the execution.")


def LoadPlugin(plugin):
    node = WaitForUser.GetDefinition()
    plugin.RegisterNode(node, WaitForUser.Create)
