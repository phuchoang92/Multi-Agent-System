import time

from Agents.Agent_Cleaner import Agent_Vacuum, Mode
from Agents.Env_Cleaner import Env

env = Env(obstacle_num=10, agent_position=[[1, 9], [10, 30]])
agent1 = Agent_Vacuum(env, (0, 0))
agent2 = Agent_Vacuum(env, (21, -9))
group_agent = [agent1, agent2]
perceive = env.step()

while True:
    # time.sleep(0.1)
    env.render()
    actions = []
    for i, agent in enumerate(group_agent):
        agent.perceive = perceive[i]
        agent.process_perceive()
        if agent.check_message():
            agent.send(group_agent[i - 1])
        if agent.mode == Mode.AVOIDING:
            agent
        action = agent.select_action()
        actions.append(action)

    perceive = env.step(actions)
