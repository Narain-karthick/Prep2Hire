"""
Job Description Parser Module
Extracts required skills and role expectations from job descriptions
"""

import re
from typing import Dict, List, Set


class JDParser:
    """Parses job descriptions to extract requirements and expectations"""
    
    def __init__(self):
        # Tech skills database
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
        
        # Keywords indicating required vs preferred
        self.required_keywords = ['required', 'must have', 'mandatory', 'essential']
        self.preferred_keywords = ['preferred', 'nice to have', 'plus', 'bonus']
    
    def extract_required_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract required technical skills from JD"""
        text_lower = text.lower()
        required_skills = {}
        
        for category, skills in self.tech_skills.items():
            found_skills = []
            for skill in skills:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill.title())
            
            if found_skills:
                required_skills[category] = found_skills
        
        return required_skills
    
    def extract_experience_required(self, text: str) -> int:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'minimum\s+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*experience\s*required',
            r'at least\s+(\d+)\+?\s*years?'
        ]
        
        max_years = 0
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                max_years = max(max_years, int(match))
        
        return max_years if max_years > 0 else 2  # Default to 2 years
    
    def extract_role_level(self, text: str) -> str:
        """Determine the seniority level of the role"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['senior', 'lead', 'principal', 'staff', 'architect']):
            return 'senior'
        elif any(word in text_lower for word in ['junior', 'entry', 'graduate', 'fresher']):
            return 'junior'
        else:
            return 'mid'
    
    def extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities from JD"""
        responsibilities = []
        
        # Look for responsibilities section
        resp_section = re.search(
            r'(responsibilities?|duties|what you.?ll do)(.*?)(requirements?|qualifications?|skills?|$)',
            text.lower(),
            re.DOTALL
        )
        
        if resp_section:
            section_text = resp_section.group(2)
            # Split by bullet points or newlines
            lines = re.split(r'[•\-\n]', section_text)
            for line in lines:
                line = line.strip()
                if len(line) > 20 and len(line) < 200:
                    responsibilities.append(line[:150])
                if len(responsibilities) >= 5:
                    break
        
        return responsibilities
    
    def categorize_skills(self, text: str) -> Dict[str, List[str]]:
        """Categorize skills into required and preferred"""
        text_lower = text.lower()
        
        # Try to find requirements section
        req_section = re.search(
            r'(requirements?|qualifications?|must have)(.*?)(preferred|nice to have|bonus|$)',
            text_lower,
            re.DOTALL
        )
        
        pref_section = re.search(
            r'(preferred|nice to have|bonus)(.*?)$',
            text_lower,
            re.DOTALL
        )
        
        required_text = req_section.group(2) if req_section else text_lower
        preferred_text = pref_section.group(2) if pref_section else ""
        
        return {
            'required_section': required_text[:500],
            'preferred_section': preferred_text[:500]
        }
    
    def parse(self, jd_text: str) -> Dict:
        """
        Main parsing function for job description
        
        Args:
            jd_text: Job description text
        
        Returns:
            Dictionary containing extracted JD information
        """
        required_skills = self.extract_required_skills(jd_text)
        experience_required = self.extract_experience_required(jd_text)
        role_level = self.extract_role_level(jd_text)
        responsibilities = self.extract_responsibilities(jd_text)
        skill_categories = self.categorize_skills(jd_text)
        
        # Count total required skills
        total_required_skills = sum(len(skill_list) for skill_list in required_skills.values())
        
        return {
            'required_skills': required_skills,
            'total_required_skills': total_required_skills,
            'experience_required': experience_required,
            'role_level': role_level,
            'responsibilities': responsibilities,
            'skill_categories': skill_categories
        }
    
    def compute_skill_match(self, resume_skills: Dict[str, List[str]], 
                           jd_skills: Dict[str, List[str]]) -> Dict:
        """
        Compute skill match percentage between resume and JD
        
        Args:
            resume_skills: Skills extracted from resume
            jd_skills: Skills extracted from job description
        
        Returns:
            Dictionary with match percentage and details
        """
        # Flatten skills to sets for comparison
        resume_skill_set = set()
        for skills in resume_skills.values():
            resume_skill_set.update([s.lower() for s in skills])
        
        jd_skill_set = set()
        for skills in jd_skills.values():
            jd_skill_set.update([s.lower() for s in skills])
        
        # Calculate matches
        matched_skills = resume_skill_set.intersection(jd_skill_set)
        missing_skills = jd_skill_set - resume_skill_set
        
        # Calculate match percentage
        if len(jd_skill_set) == 0:
            match_percentage = 0
        else:
            match_percentage = (len(matched_skills) / len(jd_skill_set)) * 100
        
        return {
            'match_percentage': round(match_percentage, 2),
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'total_jd_skills': len(jd_skill_set),
            'total_matched': len(matched_skills)
        }