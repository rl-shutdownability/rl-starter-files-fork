from __future__ import annotations

from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Door, Goal, Key
from minigrid.minigrid_env import MiniGridEnv

import matplotlib.pyplot as plt

class PhasicDoorKeyEnv(MiniGridEnv):

    """
    ## Description

    This environment has a key that the agent must pick up in order to unlock a
    goal and then get to the green goal square. This environment is difficult,
    because of the sparse reward, to solve using classical RL algorithms. It is
    useful to experiment with curiosity or curriculum learning.

    ## Mission Space

    "use the key to open the door and then get to the goal"

    ## Action Space

    | Num | Name         | Action                    |
    |-----|--------------|---------------------------|
    | 0   | left         | Turn left                 |
    | 1   | right        | Turn right                |
    | 2   | forward      | Move forward              |
    | 3   | pickup       | Pick up an object         |
    | 4   | drop         | Unused                    |
    | 5   | toggle       | Toggle/activate an object |
    | 6   | done         | Unused                    |

    ## Observation Encoding

    - Each tile is encoded as a 3 dimensional tuple:
        `(OBJECT_IDX, COLOR_IDX, STATE)`
    - `OBJECT_TO_IDX` and `COLOR_TO_IDX` mapping can be found in
        [minigrid/minigrid.py](minigrid/minigrid.py)
    - `STATE` refers to the door state with 0=open, 1=closed and 2=locked

    ## Rewards

    A reward of '1' is given for success, and '0' for failure.

    ## Termination

    The episode ends if any one of the following conditions is met:

    1. The agent reaches the goal.
    2. Timeout (see `max_steps`).

    ## Registered Configurations

    - `MiniGrid-PhasicDoorKey-5x5-v0`
    - `MiniGrid-PhasicDoorKey-6x6-v0`
    - `MiniGrid-PhasicDoorKey-8x8-v0`
    - `MiniGrid-PhasicDoorKey-16x16-v0`

    """
    def __init__(self, phase, door_locked, size=8, max_steps: int | None = None, **kwargs):
        # self.size = size
        self.phase = phase
        self.door_locked = door_locked
        # if phase == 1:
        #     self.has_goal = 

        if max_steps is None:
            max_steps = 10 * size**2
        mission_space = MissionSpace(mission_func=self._gen_mission)
        super().__init__(
            mission_space=mission_space, grid_size=size, max_steps=max_steps, **kwargs
        )

    @staticmethod
    def _gen_mission():
        return "use the key to open the door and then get to the goal"

    def _gen_grid(self, width, height):
        # Create an empty grid
        self.grid = Grid(width, height)

        # select if it has a goal or not (alternatively it has a key)
        # has_goal = self._rand_bool()
        has_goal = False if self.phase == 1 else True

        # Generate the surrounding walls
        self.grid.wall_rect(0, 0, width, height)

        # Place a goal in the bottom-right corner
        if has_goal:
            self.put_obj(Goal(), width - 2, height - 2)

        # wall opening idx
        wallOpeningIdx = self._rand_int(1, height - 2)

        # Create a vertical splitting wall
        splitIdx = self._rand_int(2, width - 2)
        self.grid.vert_wall(splitIdx, 0, length=wallOpeningIdx)
        self.grid.vert_wall(splitIdx, wallOpeningIdx + 1, length=height - wallOpeningIdx - 1)

        # Place the agent at a random position and orientation
        # on the left side of the splitting wall
        self.place_agent(size=(splitIdx, height))

        # Place a door in the wall
        doorIdx = self._rand_int(1, width - 2)
        self.put_obj(Door("yellow", is_locked=True), splitIdx, doorIdx)

        # Place a yellow key on the left side
        # if not has_goal:
        if self.phase==1 or self.phase==3:
            self.place_obj(obj=Key("yellow"), top=(0, 0), size=(splitIdx, height))

        self.mission = "use the key to open the door and then get to the goal"




env_p1_l = PhasicDoorKeyEnv(phase=1, door_locked=True, size=7, max_steps=100, render_mode="rgb_array")
env_p1_u = PhasicDoorKeyEnv(phase=1, door_locked=False, size=7, max_steps=100, render_mode="rgb_array")
env_p2_l = PhasicDoorKeyEnv(phase=2, door_locked=True, size=7, max_steps=100, render_mode="rgb_array")
env_p2_u = PhasicDoorKeyEnv(phase=2, door_locked=False, size=7, max_steps=100, render_mode="rgb_array")
env_p3_l = PhasicDoorKeyEnv(phase=3, door_locked=True, size=7, max_steps=100, render_mode="rgb_array")
env_p3_u = PhasicDoorKeyEnv(phase=3, door_locked=False, size=7, max_steps=100, render_mode="rgb_array")

envs = [env_p1_l, env_p1_u, env_p2_l, env_p2_u, env_p3_l, env_p3_u]
names = ["Phase 1 locked", "Phase 1 unlocked", "Phase 2 locked", "Phase 2 unlocked", "Phase 3 locked", "Phase 3 unlocked"]


for name, env in zip(names, envs):
    env.reset()
    img = env.render()

    # Plot the rendered image
    plt.imshow(img)
    plt.title(name)
    plt.show()