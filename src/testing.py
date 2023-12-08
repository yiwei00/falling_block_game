from env import BlockGameEnv
from stable_baselines3 import DQN
import gymnasium

env = gymnasium.make('BlockGame-v0')

model = DQN('MlpPolicy', env, verbose=1)
model.load("dqn_blockgame")

obs, _ = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, _reward, dones, _trunc, _info = env.step(action)
    if dones:
        break
    env.render()