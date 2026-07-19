import os
from dotenv import load_dotenv

import requests

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool

load_dotenv() # loads the .env file

@tool
def job_search_tool(keyword: str,min_salary: int):
    """"
    This is a job search tool, which fetchs job links for the user based on their profile.
    
    Arguments:
    keyword -> the role the user is looking for (e.g. "Software","Data", "Network")
    min_salary -> the minimum salary the user is looking for (e.g. 100000, 200000)   
    """

    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1/"
    
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 5,
       # "what": keyword,
       #"salary_min": min_salary,
       # "max_day_old": 30
    }
    try:
        response = requests.get(url, params=params, headers={"Accept": "application/json"})
        response.raise_for_status()# Raise an error for bad responses
        return response.json()
    except Exception as e:
        return f"Failed to fetch job data: {str(e)}"
    
class JobSearchAgent:
    def __init__(self):
        llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0.1,
            max_tokens=1024,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        self.tools_list = [job_search_tool]
        self.tools_by_name = {t.name: t for t in self.tools_list}
        
        self.llm_with_tools = llm.bind_tools(self.tools_list)
        
        
    def agent_node(self, state: dict):
        messages = state["messages"][-1]
        llm_input = [SystemMessage(content=f"""
         you are an expert job search agent whose task is to analyze the user career evaluation report and find best
         fit job for the user
         
         You have access to 'job_search_tool'. Use the tool to find relevent opportunities online. The toll wikk fetch job titles,
         decription and URLs.
         
         The tool takes two arguments, which are:
          keyword: the role the user is looking for (e.g. "Software", "Data", "Network")
          min_salary: the minimum salary the user is looking for (e.g. 100000, 200000)
         
         Based on the career report, decide the keyword and minimum salary.
         """)]
        
        llm_input.extend([HumanMessage(content="""Please search job for me based on my career report""")])
        llm_input.extend(messages)
        
        response = self.llm_with_tools.generate(llm_input)
        print("\n\n\n",response)
        return {"messages": [response]} 

def tool_node(self,state: dict)->dict:
    messages = state["messages"]
    last_message = messages[-1]
    
    tool_outputs = []
    
    if hasattr(last_message, "tool_call"):
        for tool_call in last_message.tool_call:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            #tool_id = tool_call["id"]
            tool_function =self.tools_by_name.get(tool_name)
            
            if tool_function:
                tool_result = tool_function(**tool_args)
            else:
                tool_result = f"Error: Tool {tool_name} not found."
                
            tool_outputs.append(
                ToolMessage(content=f"{tool_name}_OUTOUTS: {str(tool_result)}",
                            tool_name=tool_name)
            
            )
    print("\n\n\n",tool_outputs)
    return {"messages": tool_outputs}

if __name__ == "__main__":
    response = job_search_tool.invoke({"keyword":"softeware","min_salary":100000})
    print(response)

