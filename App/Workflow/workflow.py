import os
import sys
from langchain_core.messages import HumanMessage

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict, Annotated, Literal
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from App.agent.career_agent import CareerAssessmentAgent
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from App.agent.job_search_agent import JobSearchAgent


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    career_report: str


def route_assessment_agent(state: AgentState) -> Literal["career_tools", "job_search"]:
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "career_tools"

    state["career_report"] = last_message.content
    try:
        print(f"\n\nCAREER REPORT: {state['career_report']}\n\n")
    except UnicodeEncodeError:
        print(f"\n\nCAREER REPORT: {state['career_report'].encode('ascii', errors='replace').decode('ascii')}\n\n")
    return "job_search"


def route_job_search(state: AgentState) -> Literal["job_search_tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "job_search_tools"
    return "__end__"


class ExecuteWorkflow:
    def __init__(self):
        assessment_agent = CareerAssessmentAgent()
        job_search_agent = JobSearchAgent()

        workflow_builder = StateGraph(AgentState)

        workflow_builder.add_node("career_agent", assessment_agent.agent_node)
        workflow_builder.add_node("career_tools", assessment_agent.tool_node)
        workflow_builder.add_node("job_search", job_search_agent.agent_node)
        workflow_builder.add_node("job_search_tools", job_search_agent.tool_node)

        workflow_builder.add_edge(START, "career_agent")
        workflow_builder.add_conditional_edges(
            "career_agent",
            route_assessment_agent,
            {
                "career_tools": "career_tools",
                "job_search": "job_search"
            }
        )

        workflow_builder.add_edge("career_tools", "career_agent")

        workflow_builder.add_conditional_edges(
            "job_search",
            route_job_search,
            {
                "job_search_tools": "job_search_tools",
                "__end__": END
            }
        )

        workflow_builder.add_edge("job_search_tools", "job_search")

        self.workflow = workflow_builder.compile()

    def run_workflow(self) -> dict:
        input_data = {
            "messages": [HumanMessage(content="Assess my profile and generate an evaluation report")]
        }

        result = self.workflow.invoke(input_data)
        return result


if __name__ == "__main__":
    workflow = ExecuteWorkflow()
    result = workflow.run_workflow()
    print("Workflow Result:", result)