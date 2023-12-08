from env import BlockGameEnv
from stable_baselines3 import A2C
import gymnasium
import pygame as pg

env = gymnasium.make('BlockGame-v0')
model = A2C('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=100_000)
model.save("a2c_blockgame")

obs, _ = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, _reward, dones, _trunc, _info = env.step(action)
    if dones:
        break
    env.render()