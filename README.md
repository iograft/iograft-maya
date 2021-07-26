# iograft-maya

This repository contains a scripts and nodes for running iograft within Autodesk Maya. It includes a Maya Subcore command, an iograft Plugin for Maya, and a few example iograft Maya nodes.

## Maya Subcore for iograft

The Maya Subcore for iograft (`iogmaya_subcore`) defines an iograft Subcore for executing nodes in the Maya environment.

The main components of the Maya Subcore are:
- Calls `maya.standalone.initialize()` to initialize the Maya environment prior to listening for node processing requests,
- Calls `maya.standalone.uninitialize()` prior to exiting, and
- Adds a custom node executor function so all nodes are processed in the main thread. See "Threading in Maya" below for more details.


## iograft Plugin for Maya

The iograft Plugin for Maya (iograftmaya.py) allows iograft to be run from inside an interactive Maya session. The plugin registers 3 MEL commands:

1. `startiograft` -
Used to initialize a local iograft session within Maya. Starts an iograft Core using the builtin Maya Python interpreter. A UI session can be connected to this iograft Core for graph authoring and monitoring.

2. `stopiograft` -
Used to shutdown the iograft session within Maya.

3. `iograft_ui` -
Launch the iograft UI as a subprocess and connect to the iograft Core running inside of Maya. Note: The UI runs in a completely separate process and not internally in Maya. Only the iograft Core runs inside of Maya.


## iograft Environment settings for Maya

When defining the Maya environment in iograft's Environment Manager, we have to provide a few settings specific to Maya

- The *Plugin Path* is where iograft will look for nodes. This should contain the directory where the Maya nodes exist.
- The *Path* environment variable. This should include at least the directory containing `iogmaya_subcore`, Maya's 'bin' directory, and the iograft 'bin' directory.
- The *Python Path* environment variable. This should point to the iograft python folder corresponding to Maya's Python version (python27 for Maya 2020). The `iogmaya_threading` library from this repository should also be made available to this environment's PYTHONPATH if any nodes use the `maya_main_thread` decorator.
- Any additional *Environment Variables* such as `MAYA_PLUG_IN_PATH`.


## Launching Maya with an iograft Environment Set

To launch Maya and set the environment so iograft can run, we need to let iograft know which environment we are in. This can be done by launching Maya using `iograft_env`:

`iograft_env -e maya2020 -c maya`

The iograft_env command first initializes environment variables based on the settings from the iograft environment named "maya2020", and then launches Maya.

Note: iograft_env does not have to be used to start Maya, but it is quick way to ensure that the environment you are running in matches one of your defined iograft environments. If you prefer, you could setup the environment manually and simply set the IOGRAFT_ENV environment variable to the name of the iograft environment you set. The important thing is that we tell iograft which environment we are currently in.


## Threading in Maya

Some of the available Maya Python commands are expected to be run in the main thread (or else there is the possibility for errors and undefined behavior). As a result, iograft's default threaded node execution is not ideal.

To get around any threading issues, there are a couple of additions we can make to the Maya scripts and nodes. The cool thing about these additions is they require NO changes to iograft's code. All of the required modifications can happen in the user's node and subcore code:

1. Nodes that execute Maya commands that may be unsafe in a threaded environment must apply the `@maya_main_thread` decorator to their `Process` function. When running iograft interactively in Maya, this decorator makes use of Maya's `executeInMainThreadWithResult` function to process the node in Maya's main thread.

2. When processing Maya nodes in batch (i.e. when using the Maya Subcore), the `iogmaya_subcore` executes all nodes in the main thread. To do this, it creates a work queue of nodes to be processed and launches the normal `iograft.Subcore` object in a new thread. When node processing requests are received from the iograft Core (on the secondary thread), they are added to the work queue. Meanwhile, the main thread is simply looping through the work queue and processing any items that come in.

Note: In practice, not all nodes need to be executed in the main thread, so hypothetically it would be possible to only execute certain nodes in the main thread, but for simplicity we execute all nodes in the main thread for now.
