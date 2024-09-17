from crewai import Crew, Agent, Task
from config import Config
from app.models import Article, AgentTask
from app import db

def initialize_crew():
    # Initialize agents
    strategic_planner = Agent(
        role="Strategic Planner",
        goal="Develop content strategy",
        backstory="Experienced in content planning"
    )
    research_analyst = Agent(
        role="Research Analyst",
        goal="Analyze trends",
        backstory="Expert in data analysis"
    )
    content_architect = Agent(
        role="Content Architect",
        goal="Create engaging content",
        backstory="Skilled writer and editor"
    )
    content_curator = Agent(
        role="Content Curator",
        goal="Maintain content relevance",
        backstory="Experienced in content management"
    )

    # Create tasks
    create_strategy_task = Task(
        description="Create content strategy",
        agent=strategic_planner,
        expected_output="A detailed content strategy document"
    )
    research_task = Task(
        description="Research current trends",
        agent=research_analyst,
        expected_output="A comprehensive trend analysis report"
    )
    create_content_task = Task(
        description="Write article content",
        agent=content_architect,
        expected_output="A well-structured article draft"
    )
    curate_task = Task(
        description="Review and update content",
        agent=content_curator,
        expected_output="An updated and polished article"
    )

    # Initialize CrewAI
    crew = Crew(
        agents=[strategic_planner, research_analyst, content_architect, content_curator],
        tasks=[create_strategy_task, research_task, create_content_task, curate_task],
        verbose=True
    )

    return crew

def process_user_input(user_input):
    crew = initialize_crew()
    
    # Create a new article
    new_article = Article(title=f"Article about: {user_input}", status='in_progress')
    db.session.add(new_article)
    db.session.commit()

    # Process user input and generate response using CrewAI agents
    response = f"Processing user input: {user_input}\n\n"

    # Update the tasks with the user input
    for task in crew.tasks:
        task.description += f" based on: {user_input}"

    # Kickoff the crew to process all tasks
    results = crew.kickoff()

    for task, result in zip(crew.tasks, results):
        agent_task = AgentTask(agent_type=task.agent.role, task_description=task.description, status='completed', article_id=new_article.id)
        db.session.add(agent_task)
        response += f"Task: {task.description}\nResult: {result}\n\n"

    db.session.commit()

    new_article.content = response
    new_article.status = 'completed'
    db.session.commit()

    return response
