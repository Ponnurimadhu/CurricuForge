def generate_curriculum_mermaid(curriculum_data):
    """Generate Mermaid.js diagram from curriculum data"""
    
    mermaid_code = ["graph TD"]
    
    # Add title
    mermaid_code.append(f"    title[{curriculum_data['course_overview']['title']}]")
    
    # Add course overview node
    mermaid_code.append("    subgraph Course_Overview")
    mermaid_code.append(f"        overview[\"Course: {curriculum_data['course_overview']['title']}<br/>Duration: {curriculum_data['course_overview']['duration']}<br/>Level: {curriculum_data['course_overview']['level']}\"]")
    mermaid_code.append("    end")
    
    # Add prerequisites
    if curriculum_data['prerequisites']:
        mermaid_code.append("    subgraph Prerequisites")
        for i, prereq in enumerate(curriculum_data['prerequisites']):
            mermaid_code.append(f"        prereq{i}[{prereq}]")
        mermaid_code.append("    end")
        mermaid_code.append("    overview --> prereq0")
    
    # Add weekly breakdown
    mermaid_code.append("    subgraph Weekly_Breakdown")
    for week_data in curriculum_data['weekly_breakdown']:
        week_num = week_data['week']
        week_topic = week_data['topic']
        mermaid_code.append(f"        week{week_num}[Week {week_num}: {week_topic}]")
        
        # Add subtopics
        for j, subtopic in enumerate(week_data['subtopics'][:3]):  # Limit to 3 for readability
            mermaid_code.append(f"        subtopic{week_num}_{j}[{subtopic}]")
            mermaid_code.append(f"        week{week_num} --> subtopic{week_num}_{j}")
    mermaid_code.append("    end")
    
    # Connect weeks
    for i in range(1, len(curriculum_data['weekly_breakdown'])):
        mermaid_code.append(f"    week{i} --> week{i+1}")
    
    # Connect overview to first week
    if curriculum_data['weekly_breakdown']:
        mermaid_code.append("    overview --> week1")
    
    # Add assessment methods
    if curriculum_data['assessment_methods']:
        mermaid_code.append("    subgraph Assessment")
        for k, assessment in enumerate(curriculum_data['assessment_methods']):
            mermaid_code.append(f"        assessment{k}[{assessment}]")
        mermaid_code.append("    end")
        mermaid_code.append(f"    week{len(curriculum_data['weekly_breakdown'])} --> assessment0")
    
    # Add learning outcomes
    if curriculum_data['learning_outcomes']:
        mermaid_code.append("    subgraph Learning_Outcomes")
        for l, outcome in enumerate(curriculum_data['learning_outcomes'][:4]):  # Limit to 4
            mermaid_code.append(f"        outcome{l}[{outcome}]")
        mermaid_code.append("    end")
        mermaid_code.append("    assessment0 --> outcome0")
    
    # Add styling
    mermaid_code.append("    classDef default fill:#f9f,stroke:#333,stroke-width:2px;")
    mermaid_code.append("    classDef week fill:#bbf,stroke:#f66,stroke-width:2px;")
    
    for i in range(1, len(curriculum_data['weekly_breakdown']) + 1):
        mermaid_code.append(f"    class week{i} week;")
    
    return "\n".join(mermaid_code)

def generate_learning_path_mermaid(curriculum_data):
    """Generate a learning path flowchart"""
    
    mermaid_code = ["graph LR"]
    mermaid_code.append(f"    Start((Start))")
    
    # Create learning path
    for i, week_data in enumerate(curriculum_data['weekly_breakdown']):
        week_num = week_data['week']
        week_topic = week_data['topic']
        
        if i == 0:
            mermaid_code.append(f"    Start --> Week{week_num}[Week {week_num}<br/>{week_topic}]")
        else:
            mermaid_code.append(f"    Week{i} --> Week{week_num}")
        
        # Add learning milestones
        mermaid_code.append(f"    Week{week_num} --> Milestone{week_num}((Milestone {week_num}))")
    
    final_week = len(curriculum_data['weekly_breakdown'])
    mermaid_code.append(f"    Milestone{final_week} --> Complete((Course Complete))")
    
    return "\n".join(mermaid_code)

def generate_topic_hierarchy_mermaid(topic, subtopics):
    """Generate a topic hierarchy diagram"""
    
    mermaid_code = ["graph TD"]
    mermaid_code.append(f"    {topic}[{topic}]")
    
    for i, subtopic in enumerate(subtopics):
        mermaid_code.append(f"    subtopic{i}[{subtopic}]")
        mermaid_code.append(f"    {topic} --> subtopic{i}")
        
        # Add sub-subtopics (example data)
        for j in range(2):
            mermaid_code.append(f"    detail{i}_{j}[Detail {j+1}]")
            mermaid_code.append(f"    subtopic{i} --> detail{i}_{j}")
    
    return "\n".join(mermaid_code)