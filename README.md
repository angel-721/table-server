# Table Server
A simple [Gymnasium](https://gymnasium.farama.org/) enviroment that can be used to test search algorithms

![tableserver](https://github.com/angel-721/table-server/assets/75283919/00dc2995-8d08-4762-8789-ca51f3bd8bd1)


## Setup
```
pip install gymnasium
git clone https://github.com/angel-721/table-server.git
cd table-server
make
```

### Use
Include these imports in your python file. Look at agents/agent.py for reference
``` python
import gymnasium as gym
import table_server
from table_server.envs import TableServerModel
```

## Actions
| Action         | Index |
|----------------|-------|
| UP             | 0     |
| DOWN           | 1     |
| LEFT           | 2     |
| RIGHT          | 3     |
| PICK_UP_MEAL   | 4     |
| SERVE_MEAL     | 5     |



## Credits for assets
- https://pixelfight.itch.io/birdcat
- https://piiixl.itch.io/mega-pixel-art-32x32-px-icons-sprite-sheet
- https://havran.itch.io/wooden-barrel
- https://joao9396.itch.io/pixel-nature-pack
