import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict,Annotated,Literal
from langgraph.graph import START,END,StateGraph
from langgraph.graph.message import add_messages
from App.agent.career_assestment_agent import CareerAssessmentAgent

class AgentState(TypedDict):
    messages: Annotated[list,add_messages]
    career_report:str

def rout_assessment(start:AgentState) -> Literal["career_assessment","end"]:
    messages= state["messages"]
    last_message= messages[-1]    
    
    if hasattr(last_message,"tool_calls"):
        return"job_search_tool"

    return "__end__"

assessment_agent=CareerAssessmentAgent()
job_search_agent=JobSearchAgent()

workflow_builder = StateGraph(AgentState)
workflow_builder.add_node("assessment_agent",assessment_agent.agent_node)
workflow_builder.add_node("assessment_tool",assessment_agent.tool_node)
workflow_builder.add_node("job_search",job_search_agent.agent_node)
workflow_builder.add_node("job_search_tool",job_search_agent.tool_node)

workflow_builder.add_edge(START,"career_assessment")
workflow_builder.add_conditional_edges(
    "career_assessment",
    rout_assessment,
    {
        "assessment_tool":"assessment_tool",
        "__end__":"job_search"
    }
)

workflow_builder.add_edge("assessment_tool","assessment_agent")

workflow_builder.add_conditional_edges(
    "job_search",
    route_job_search,
    {
        "job_search_tool":"job_search_tool",
        "__end__":END
    }
)
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    input={
        "messages":[HumanMessage(content="Assess my profile and generate an evaluation report")]
    }

    print("\n\n--------------OUTPUT STARTS HERE--------------\n\n")
    outpu=workflow.invoke(input)
    print(outpu["messages"][-1].content)

    print("\n\n--------------OUTPUT ENDS HERE--------------\n\n")

    print("\n\n-------------------------START DEBUGGING HERE---------------\n\n")

    print(output)

    print("\n\n-------------------------END DEBUGGING HERE---------------\n\n")