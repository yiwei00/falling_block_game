from env import BlockGameEnv
from stable_baselines3 import DQN
import gymnasium

env = gymnasium.make('BlockGame-v0', set_speed=1, dot_game=True)

model = DQN(
    'MlpPolicy', env, verbose=1, device="cuda",
    exploration_initial_eps=.9,
    exploration_final_eps=0.05,
    exploration_fraction=0.98
)
model.learn(total_timesteps=100_000)

obs, _ = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, _reward, terminated, _trunc, _info = env.step(action)
    if terminated:
        break
    env.render()