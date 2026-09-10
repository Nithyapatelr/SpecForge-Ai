"""
MAST (Multi-Agent System Failure Taxonomy) definitions.
Source: Cemri et al., "Why Do Multi-Agent LLM Systems Fail?" (UC Berkeley, 2025, arXiv:2503.13657).
"""

MAST_FAILURE_MODES = [
    # Category: Specification Issues
    {
        "failure_mode_id": "FM-1.1",
        "category": "Specification Issues",
        "mode_name": "Disobey Task Specification",
        "mode_definition": "Failure to adhere to the specified constraints or requirements of a given task, leading to suboptimal or incorrect outcomes."
    },
    {
        "failure_mode_id": "FM-1.2",
        "category": "Specification Issues",
        "mode_name": "Disobey Role Specification",
        "mode_definition": "Failure to adhere to the defined responsibilities and constraints of an assigned role, potentially leading to an agent behaving like another."
    },
    {
        "failure_mode_id": "FM-1.3",
        "category": "Specification Issues",
        "mode_name": "Step Repetition",
        "mode_definition": "Unnecessary reiteration of previously completed steps in a process, potentially causing delays or errors in task completion."
    },
    {
        "failure_mode_id": "FM-1.4",
        "category": "Specification Issues",
        "mode_name": "Loss of Conversation History",
        "mode_definition": "Unexpected context truncation, disregarding recent interaction history and reverting to an antecedent conversational state."
    },
    {
        "failure_mode_id": "FM-1.5",
        "category": "Specification Issues",
        "mode_name": "Unaware of Termination Conditions",
        "mode_definition": "Lack of recognition or understanding of the criteria that should trigger the termination of the agents' interaction, potentially leading to unnecessary continuation."
    },

    # Category: Inter-Agent Misalignment
    {
        "failure_mode_id": "FM-2.1",
        "category": "Inter-Agent Misalignment",
        "mode_name": "Conversation Reset",
        "mode_definition": "Unexpected or unwarranted restarting of a dialogue, potentially losing context and progress made in the interaction."
    },
    {
        "failure_mode_id": "FM-2.2",
        "category": "Inter-Agent Misalignment",
        "mode_name": "Fail to Ask for Clarification",
        "mode_definition": "Inability to request additional information when faced with unclear or incomplete data, potentially resulting in incorrect actions."
    },
    {
        "failure_mode_id": "FM-2.3",
        "category": "Inter-Agent Misalignment",
        "mode_name": "Task Derailment",
        "mode_definition": "Deviation from the intended objective or focus of a given task, potentially resulting in irrelevant or unproductive actions."
    },
    {
        "failure_mode_id": "FM-2.4",
        "category": "Inter-Agent Misalignment",
        "mode_name": "Information Withholding",
        "mode_definition": "Failure to share or communicate important data or insights that an agent possesses and that could impact decision-making of other agents if shared."
    },
    {
        "failure_mode_id": "FM-2.5",
        "category": "Inter-Agent Misalignment",
        "mode_name": "Ignored Other Agent's Input",
        "mode_definition": "Disregarding or failing to adequately consider input or recommendations provided by other agents in the system."
    },
    {
        "failure_mode_id": "FM-2.6",
        "category": "Inter-Agent Misalignment",
        "mode_name": "Reasoning-Action Mismatch",
        "mode_definition": "Discrepancy between the logical reasoning process and the actual actions taken by the agent."
    },

    # Category: Task Verification
    {
        "failure_mode_id": "FM-3.1",
        "category": "Task Verification",
        "mode_name": "Premature Termination",
        "mode_definition": "Ending a dialogue, interaction, or task before all necessary information has been exchanged or objectives have been met."
    },
    {
        "failure_mode_id": "FM-3.2",
        "category": "Task Verification",
        "mode_name": "No or Incomplete Verification",
        "mode_definition": "(Partial) omission of proper checking or confirmation of task outcomes or system outputs, potentially allowing errors or inconsistencies to propagate undetected."
    },
    {
        "failure_mode_id": "FM-3.3",
        "category": "Task Verification",
        "mode_name": "Incorrect Verification",
        "mode_definition": "Failure to adequately validate or cross-check crucial information or decisions during the iterations."
    }
]
