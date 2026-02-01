"""
Resume Parser Module
Extracts skills, experience, and projects from uploaded resumes
"""

import re
from typing import Dict, List
import PyPDF2
from io import BytesIO


class ResumeParser:
    """Parses resume files to extract candidate information"""
    
    def __init__(self):
        # Common tech skills dictionary for matching
        self.tech_skills = {
            'languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 
                         'go', 'rust', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 
                          'express', 'node.js', 'nodejs', '.net', 'laravel', 'rails'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 
                         'dynamodb', 'oracle', 'sql server', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'kubernetes', 'docker', 
                     'terraform', 'jenkins', 'ci/cd'],
            'ml_ai': ['tensorflow', 'pytorch', 'scikit-learn', 'keras', 'pandas', 
                     'numpy', 'machine learning', 'deep learning', 'nlp', 'computer vision'],
            'tools': ['git', 'jira', 'confluence', 'agile', 'scrum', 'rest api', 
                     'graphql', 'microservices']
        }
    
    def parse_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical skills from resume text"""
        text_lower = text.lower()
        extracted_skills = {}
        
        for category, skills in self.tech_skills.items():
            found_skills = []
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill.title())
            
            if found_skills:
                extracted_skills[category] = found_skills
        
        return extracted_skills
    
    def extract_experience(self, text: str) -> Dict:
        """Extract years of experience and work history"""
        # Look for experience patterns
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s*experience'
        ]
        
        years_of_experience = 0
        for pattern in exp_patterns:
            match = re.search(pattern, text.lower())
            if match:
                years_of_experience = max(years_of_experience, int(match.group(1)))
        
        # Extract company names (basic heuristic)
        companies = []
        # Look for common section headers
        experience_section = re.search(
            r'(experience|work history|employment)(.*?)(education|skills|projects|$)',
            text.lower(),
            re.DOTALL
        )
        
        if experience_section:
            section_text = experience_section.group(2)
            # Look for capitalized phrases that might be company names
            potential_companies = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b', section_text)
            companies = list(set(potential_companies[:5]))  # Limit to 5 unique
        
        return {
            'years': years_of_experience,
            'companies': companies
        }
    
    def extract_projects(self, text: str) -> List[str]:
        """Extract project names and descriptions"""
        projects = []
        
        # Look for project section
        project_section = re.search(
            r'(projects?|portfolio)(.*?)(education|skills|experience|certification|$)',
            text.lower(),
            re.DOTALL
        )
        
        if project_section:
            section_text = project_section.group(2)
            # Split by bullet points or newlines
            lines = re.split(r'[•\-\n]', section_text)
            for line in lines:
                line = line.strip()
                # Keep lines that are substantial (likely project descriptions)
                if len(line) > 20 and len(line) < 200:
                    projects.append(line[:150])  # Truncate long descriptions
                if len(projects) >= 5:  # Limit to 5 projects
                    break
        
        return projects
    
    def parse(self, file_content: bytes, is_pdf: bool = True) -> Dict:
        """
        Main parsing function
        
        Args:
            file_content: Resume file content as bytes
            is_pdf: Whether the file is PDF (True) or text (False)
        
        Returns:
            Dictionary containing extracted resume information
        """
        # Extract text
        if is_pdf:
            text = self.parse_pdf(file_content)
        else:
            text = file_content.decode('utf-8')
        
        # Extract all components
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        projects = self.extract_projects(text)
        
        # Count total skills
        total_skills = sum(len(skill_list) for skill_list in skills.values())
        
        return {
            'raw_text': text[:1000],  # Store first 1000 chars for reference
            'skills': skills,
            'total_skills': total_skills,
            'experience': experience,
            'projects': projects
        }