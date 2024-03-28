# Minecraft Agent with Goal-Oriented Perception and Memory

This repository contains an intelligent agent for Minecraft. The agent is designed to autonomously navigate and interact with the Minecraft environment while working towards specific goals. It utilizes a modular architecture that includes perception, memory, action, and goal+plan modules.

## Workflow

1. **Update Goal+Plan**: The agent observes the previous goal and the sequence of actions and outcomes, producing key lessons learned. It then queries the perception module for the next best goal and plan.

2. **Action**: The agent debates the next best action based on previous actions, outcomes, and current goal progress. It performs the chosen action, summarizes the changes in the environment with respect to goal progress, and updates the current goal progress.

3. **Memory**: The agent stores and retrieves information from a Vector DB, including goal lessons learned, perceptions, and the locations of important objects like chests, beds, and crafting tables.

4. **Perception**: The agent implements a Google Self-Discover QA paradigm. Given a query, it can either answer it directly or engage in deep thinking to come up with an answer.

The agent maintains a scratchpad and global variables to keep track of its current goal, plan, action+outcome pairs, goal progress, and previous goals and outcomes.

## Key Features

- Goal-oriented decision making
- Modular architecture for perception, memory, action, and goal+plan management
- Vector DB for efficient storage and retrieval of memories
- Self-Discover QA paradigm for intelligent perception and query answering
- Continuous learning and adaptation based on previous experiences

This Minecraft agent demonstrates the integration of techniques to create an autonomous, goal-driven agent capable of navigating and interacting with a complex environment.
