# Copyright 2022 Fabrica Software, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI


def get_main_window():
    """
    Return the Maya main window instance.
    """
    main_window_ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    if sys.version_info[0] < 3:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def ensure_window_shown(window):
    """
    Helper function to ensure that the given window is brought to the front
    and shown. Also activates the parent window if a parent exists.
    """
    if window.parent():
        window.parent().show()
        window.parent().activateWindow()

    window.show()
    window.activateWindow()
    window.raise_()
