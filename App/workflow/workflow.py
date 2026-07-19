import os
import sys
from langchain_core.messages import HumanMessage

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict,Annotated,Literal
from langgraph.graph import START,END,StateGraph
from langgraph.graph.message import add_messages
from App.agent.career_assestment_agent import CareerAssessmentAgent
from langchain_core.messages import HumanMessage,SystemMessage,ToolMessage
from App.agent.job_serch_agent import JobSearchAgent
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    career_report: str

def route_assessment_agent(state: AgentState) -> Literal["_assessment_agent","__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message,"tool_calls")and last_message.tool_calls:
        return "_assessment_tools"
    
    state["career_report"] = last_message.content
    print(f"\n\nCAREER REPORT: {state['career_report']}\n\n")
    return "__end__"
  
def route_job_search(state: AgentState) -> Literal["_job_search_agent","__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message,"tool_calls"):
        return "_job_search_tools"
    return "__end__"
class ExecuteWorkflow:
    def __init__(self):
        assessment_agent = CareerAssessmentAgent()
        job_search_agent = JobSearchAgent()
        
        workflow_builder = StateGraph(AgentState)
       
        workflow_builder.add_node("assessment_agent", assessment_agent.agent_node)
        workflow_builder.add_node("assessment_tools", assessment_agent.tool_node)
        workflow_builder.add_node("job_search", job_search_agent.agent_node)
        workflow_builder.add_node("job_search_tools", job_search_agent.tool_node)
        
        workflow_builder.add_edge(START,"career_assessment")
        workflow_builder.add_conditional_edges(
            "career_assessment",
            route_assessment,
            {
                "assessment_tools": "assessment_tools",
                "__end__": END
            }
        )
        
        workflow_builder.add_edge("assessment_tools","career_assessment")
        
       # workflow_builder.add_conditional_edges(
        #   "job_search",
        #   route_job_search,
         #   {
          #      "job_search_tools": "job_search_tools",
           #     "__end__": END
            #}
        #)
        
        #workflow_builder.add_edge("job_search_tools","job_search")
        
        self.workflow = workflow_builder.compile()
        
    def run_workflow(self) -> dict:
        input_data = {
            "messages":[HumanMessage(content="Assess my profile and generate an evaluation report")]
        }
        
        result = self.workflow.invoke(input_data)
        return result
        
        
if __name__ == "__main__":
    input_data = {
        "messages":[HumanMessage(content="Assess my profile and generate an evaluation report")]
        }