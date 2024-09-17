from crewai import Crew, Agent, Task
from app.models import AgentTask, Article
from app import db, celery

class CoordinatorAgent:
    def __init__(self, autonomy_level=0.5):
        self.autonomy_level = autonomy_level
        self.agents = self._create_agents()

    def set_autonomy_level(self, level):
        self.autonomy_level = max(0, min(1, level))

    def _create_agents(self):
        strategic_planner = Agent(
            role='Strategic Planner',
            goal='Develop and execute a strategic plan aligning content with organizational objectives',
            backstory='A seasoned strategist in content marketing, focused on creating innovative approaches',
            verbose=True
        )

        research_analyst = Agent(
            role='Research Analyst',
            goal='Analyze the current content landscape to identify gaps and opportunities for innovation',
            backstory='A data-driven analyst providing insights to shape successful content strategies',
            verbose=True
        )

        content_architect = Agent(
            role='Content Architect',
            goal='Develop a base of concise articles on ESG and social topics',
            backstory='Passionate about social issues and content creation, building structured and engaging content',
            verbose=True
        )

        content_curator = Agent(
            role='Content Curator',
            goal='Ensure that published content is up-to-date and aligned with current trends',
            backstory='Expert in identifying content trends and ensuring that articles remain relevant to the target audience',
            verbose=True
        )

        return {
            'strategic_planner': strategic_planner,
            'research_analyst': research_analyst,
            'content_architect': content_architect,
            'content_curator': content_curator
        }

    @celery.task
    def create_article(self, title):
        article = Article(title=title, status='in_progress')
        db.session.add(article)
        db.session.commit()

        # Create tasks for each agent
        for agent_type, agent in self.agents.items():
            task = AgentTask(agent_type=agent_type, task_description=f"Work on article: {title}", status='pending', article_id=article.id)
            db.session.add(task)
        db.session.commit()

        # Start the workflow
        self.execute_workflow.delay(article.id)

    @celery.task
    def execute_workflow(self, article_id):
        article = Article.query.get(article_id)
        tasks = AgentTask.query.filter_by(article_id=article_id).all()

        crew = Crew(
            agents=[agent for agent in self.agents.values()],
            tasks=[
                Task(
                    description=task.task_description,
                    agent=self.agents[task.agent_type]
                ) for task in tasks
            ],
            verbose=True
        )

        result = crew.kickoff()

        for task in tasks:
            task.status = 'completed'
        
        article.content = result
        article.status = 'ready_for_review'
        db.session.commit()

    def get_task_status(self, article_id):
        tasks = AgentTask.query.filter_by(article_id=article_id).all()
        return {task.agent_type: task.status for task in tasks}
