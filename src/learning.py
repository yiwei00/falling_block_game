from env import BlockGameEnv
from stable_baselines3 import DQN
import gymnasium

env = gymnasium.make('BlockGame-v0', rand_board=True, n_holes=1, set_speed=4)

model = DQN('MlpPolicy', env, verbose=1, device="cuda")
model.learn(total_timesteps=100_000)
model.save("dqn_blockgame")

obs, _ = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, _reward, terminated, _trunc, _info = env.step(action)
    if terminated:
        break
    env.render()