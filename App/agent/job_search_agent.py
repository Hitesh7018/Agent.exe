import os
from typing import Any
from dotenv import load_dotenv

import requests
import time
import re
from groq import RateLimitError
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

load_dotenv()


def normalize_job_results(data: Any) -> str:
    """Convert raw Adzuna search payload into a clean, readable job list."""
    if not isinstance(data, dict):
        return str(data)

    results = data.get("results") or []
    if not results:
        return "No jobs found for the selected criteria."

    lines = []
    for index, job in enumerate(results, start=1):
        title = job.get("title") or "N/A"
        company = (job.get("company") or {}).get("display_name") or "N/A"
        location = (job.get("location") or {}).get("display_name") or "N/A"
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        contract = job.get("contract_time") or "N/A"
        url = job.get("redirect_url") or job.get("url") or "N/A"

        if salary_min and salary_max and salary_min != 0:
            salary_text = f"₹{salary_min:,.0f} - ₹{salary_max:,.0f}"
        elif salary_min and salary_min != 0:
            salary_text = f"₹{salary_min:,.0f}"
        elif salary_max and salary_max != 0:
            salary_text = f"₹{salary_max:,.0f}"
        else:
            salary_text = "Salary not disclosed"

        description = job.get("description") or "No description provided."
        short_desc = description.replace("\n", " ").strip()
        if len(short_desc) > 200:
            short_desc = short_desc[:197].rstrip() + "..."

        lines.append(
            f"{index}. {title}\n"
            f"   Company: {company}\n"
            f"   Location: {location}\n"
            f"   Type: {contract}\n"
            f"   Salary: {salary_text}\n"
            f"   URL: {url}\n"
            f"   Description: {short_desc}\n"
        )

    return "\n".join(lines)


@tool
def job_search_tool(keyword: str,min_salary: int, max_salary: int):
    """
    This is job search tool, which analyzes the resume data of the user and suggests the best suitable job based
    on user's profile.
    Arguments:
    keyword -> the role the user looking for (e.g. "software", "data", "IT","networking")
    min_salary -> the minimum salary the user is looking for (e.g. 30000)
    max_salary -> the maximum salary the user is looking for (e.g. 200000)
    """
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1/"
    
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 3,
        "what": keyword,
        "salary_min": min_salary,
        "salary_max": max_salary,
    }
    
    try:
        response = requests.get(url, params=params, headers={"Accept": "application/json"})
        response.raise_for_status()
        return normalize_job_results(response.json())
    except Exception as e:
        return f"Failed to fetch job data: {str(e)}"
    
class JobSearchAgent:
    def __init__(self):
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=1000,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        self.tools_list = [job_search_tool]
        self.tools_by_name = {tool.name: tool for tool in self.tools_list}
        
        self.llm_with_tools = llm.bind_tools(self.tools_list)
        
    def agent_node(self, state: dict):
        messages = state["messages"]
        llm_input =[SystemMessage(content=f"""
         You are an expert job search agent whose task is to analyze the user career evaluation repoortand find best 
         fit job for the user 
        
         You have access to 'job_search tool'. use the tool to find relavent oppoetunities online. the toll featch job titels,
         discription and URLs.
         
         The tool takes three arguments, which are:
         keyword -> the role the user looking for (e.g. "software", "data", "IT","networking")
         min_salary -> the minimum salary the user is looking for (e.g. 30000)
         max_salary -> the maximum salary the user is looking for (e.g. 200000)
         
         Based on the user career evaluation report, decide the keyword, min_salary and max_salary.
          """)]
        
        llm_input.extend(messages)
        llm_input.append(HumanMessage(content="please search best job for me"))
        
        response =self.llm_with_tools.invoke(llm_input)
        # print("\n\n\n",response)
        return {"messages":[response]}
    
    def tool_node(self, state: dict) -> dict:
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_output = []
        
        tool_calls =getattr(last_message, "tool_calls", None) or getattr(last_message, "tool_call", None)
        if tool_calls:
            for tool_call in tool_calls:
                tool_name=tool_call["name"]
                tool_args=tool_call["args"]
                tool_id=tool_call["id"]
                tool_function = self.tools_by_name.get(tool_name)
                
                if tool_function:
                    tool_result = tool_function.invoke(tool_args)
                else:
                    tool_result = f"Error: Tool '{tool_name}' not found."
                    
                tool_output.append(
                    ToolMessage(
                        content=f"{tool_name}_OUTPUT: {str(tool_result)}",
                        tool_call_id=tool_id,
                        name=tool_name,
                    )
                )
        # print("\n\n\n", repr(tool_output))
        return {"messages": tool_output}
    
if __name__ == "__main__":
    response = job_search_tool.invoke({"keyword": "software", "min_salary": 30000, "max_salary": 200000})
    print(response)