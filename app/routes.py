from flask import Blueprint, render_template, jsonify, request
from app.models import Article, AgentTask
from app import db, api
from flask_restful import Resource
from crew import initialize_crew, process_user_input

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    articles = Article.query.all()
    crew = initialize_crew()
    agents = {agent.role: agent for agent in crew.agents}
    return render_template('dashboard.html', articles=articles, agents=agents)

@bp.route('/article/<int:id>')
def article(id):
    article = Article.query.get_or_404(id)
    tasks = AgentTask.query.filter_by(article_id=id).all()
    return render_template('article.html', article=article, tasks=tasks)

@bp.route('/api/interact', methods=['POST'])
def interact_with_agents():
    data = request.get_json()
    if not data or 'user_input' not in data:
        return jsonify({'error': 'No input provided'}), 400
    
    user_input = data['user_input']
    
    # Use CrewAI to process the user input
    result = process_user_input(user_input)
    
    # Find the newly created article
    new_article = Article.query.filter_by(title=f"Article about: {user_input}").order_by(Article.id.desc()).first()
    
    return jsonify({'response': result, 'article_id': new_article.id if new_article else None})

class ArticleAPI(Resource):
    def get(self, id):
        article = Article.query.get_or_404(id)
        return jsonify({
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'status': article.status
        })

    def put(self, id):
        article = Article.query.get_or_404(id)
        data = request.get_json()
        article.title = data.get('title', article.title)
        article.content = data.get('content', article.content)
        article.status = data.get('status', article.status)
        db.session.commit()
        return jsonify({'message': 'Article updated successfully'}), 200

    def delete(self, id):
        article = Article.query.get_or_404(id)
        db.session.delete(article)
        db.session.commit()
        return jsonify({'message': 'Article deleted successfully'}), 200

api.add_resource(ArticleAPI, '/api/article/<int:id>')

@bp.route('/api/article/<int:id>/tasks')
def article_tasks(id):
    tasks = AgentTask.query.filter_by(article_id=id).all()
    return jsonify([{
        'id': task.id,
        'agent_type': task.agent_type,
        'task_description': task.task_description,
        'status': task.status
    } for task in tasks])

@bp.route('/api/crew/status')
def crew_status():
    return jsonify({
        'status': 'active',
        'current_task': 'Processing user input',
        'progress': '50%'
    })
