from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI


@CrewBase
class CarAnsweringCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="gpt-4o-mini")
    process = Process.hierarchical

    @agent
    def answer_writing_agent(self) -> Agent:
        search_tool = FetchDocsTool()
        return Agent(
            config=self.agents_config["answer_writing_agent"],
            llm=self.llm,
            allow_delegation=True,
        )  # type: ignore

    @agent
    def fact_checking_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["fact_checking_agent"],
            llm=self.llm,
        )  # type: ignore

    @agent
    def docs_fetcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["docs_fetcher_agent"],
            llm=self.llm,
        )  # type: ignore
