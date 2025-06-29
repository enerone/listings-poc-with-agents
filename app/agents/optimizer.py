import json
from typing import Dict, Any, List
from app.services.ollama_client import OllamaClient
from app.core.config import settings

class OptimizerAgent:
    def __init__(self):
        self.ollama = OllamaClient()
        self.model = settings.ollama_model
        
        # Amazon best practices rules
        self.amazon_rules = {
            "title_max_length": 200,
            "bullet_max_length": 255,
            "description_max_length": 2000,
            "forbidden_words": [
                "best", "mejor", "#1", "garantizado", "gratis", "free",
                "regalo", "oferta limitada", "promoción", "descuento"
            ],
            "required_elements": [
                "marca", "material", "color", "tamaño", "uso"
            ]
        }
    
    async def optimize(self, title: str, description: str, bullets: List[str], keywords: List[str]) -> Dict[str, Any]:
        """Optimize listing based on Amazon best practices"""
        
        system_prompt = f"""You are an Amazon listing optimization expert. Your job is to improve an existing listing following Amazon best practices and output everything in SPANISH.

IMPORTANT: Respond ONLY with valid JSON. Do not include any thinking, explanations, or additional text.

AMAZON RULES TO FOLLOW:
- Title max {self.amazon_rules['title_max_length']} characters
- Each bullet point max {self.amazon_rules['bullet_max_length']} characters  
- Description max {self.amazon_rules['description_max_length']} characters
- DO NOT use forbidden words: {', '.join(self.amazon_rules['forbidden_words'])}
- Include important elements: {', '.join(self.amazon_rules['required_elements'])}

BEST PRACTICES:
- Use keywords naturally
- Focus on benefits, not just features
- Use specific numbers and data when possible
- Create urgency without forbidden words
- Optimize for mobile searches
- Include specific use cases

CRITICAL LANGUAGE RULES - FOLLOW STRICTLY:
- ALL OUTPUT MUST BE IN PERFECT SPANISH ONLY
- NO English words allowed (no "briefcase", "mejor", "perfect", etc.)
- NO invented Spanish words (no "coaterna", "manejeros", etc.)
- NO mixed languages or Spanglish
- Use ONLY real Spanish vocabulary
- Professional e-commerce Spanish terminology
- If input has mixed languages, clean it up to pure Spanish

Always respond in valid JSON format with this structure:
{{
    "title": "Spanish optimized title here",
    "description": "Spanish optimized description here", 
    "bullets": ["Spanish bullet 1", "Spanish bullet 2", "Spanish bullet 3", "Spanish bullet 4", "Spanish bullet 5"],
    "improvements": ["Spanish improvement 1", "Spanish improvement 2", "Spanish improvement 3"],
    "compliance_score": 95
}}"""

        prompt = f"""
Optimize this Amazon listing to maximize conversions and comply with rules. OUTPUT EVERYTHING IN SPANISH:

CURRENT TITLE: {title}
CURRENT DESCRIPTION: {description}
CURRENT BULLETS: {bullets}
AVAILABLE KEYWORDS: {keywords}

Optimize considering:
1. Amazon rules compliance
2. SEO and ranking
3. Conversion rate
4. User experience
5. Competitiveness

Generate an optimized version that:
- Improves CTR (Click Through Rate)
- Increases conversion
- 100% complies with Amazon rules
- Uses keywords strategically
- Appeals to target audience
- CRITICAL: Clean up any mixed languages in input
- Convert everything to natural, fluent Spanish
- DO NOT use invented words or Spanglish
- Use proper Spanish grammar and vocabulary

LANGUAGE CLEANING REQUIRED:
- If input contains mixed languages, translate everything to Spanish
- Remove any English words completely
- Fix any invented Spanish words
- Create natural Spanish content

Respond in valid JSON format with PURE Spanish content only.
"""
        
        try:
            result = await self.ollama.generate(
                model=self.model,
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "message": f"Error del modelo: {result.get('error', 'Unknown error')}",
                    "data": None
                }
            
            # Parse JSON response
            response_text = result["response"].strip()
            
            # Remove thinking tags if present (more aggressive cleaning)
            if "<think>" in response_text or "thinking" in response_text.lower():
                # Try multiple patterns for thinking tags
                patterns_to_remove = [
                    (r"<think>.*?</think>", ""),
                    (r"<thinking>.*?</thinking>", ""),
                    (r"thinking:.*?(?=\{)", ""),
                    (r".*?(?=\{)", "")  # Remove everything before first {
                ]
                
                import re
                for pattern, replacement in patterns_to_remove:
                    response_text = re.sub(pattern, replacement, response_text, flags=re.DOTALL | re.IGNORECASE)
                    response_text = response_text.strip()
                    if response_text.startswith("{"):
                        break
                
                # If still no valid start, try to find JSON boundaries
                if not response_text.startswith("{"):
                    json_start = response_text.find("{")
                    if json_start >= 0:
                        response_text = response_text[json_start:].strip()
                    else:
                        return {
                            "success": False,
                            "message": "No se encontró JSON válido en la respuesta del modelo",
                            "data": None
                        }
            
            # Try to extract JSON if it's wrapped in markdown
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Find JSON object boundaries
            if response_text.find("{") >= 0:
                start_brace = response_text.find("{")
                # Find matching closing brace
                brace_count = 0
                end_brace = start_brace
                for i, char in enumerate(response_text[start_brace:], start_brace):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            end_brace = i
                            break
                
                if brace_count == 0:
                    response_text = response_text[start_brace:end_brace + 1]
            
            try:
                parsed_data = json.loads(response_text)
                
                # Validate required fields
                required_fields = ["title", "description", "bullets"]
                if not all(field in parsed_data for field in required_fields):
                    return {
                        "success": False,
                        "message": "Respuesta incompleta del modelo",
                        "data": None
                    }
                
                # Validate Amazon compliance
                compliance_issues = self._validate_compliance(parsed_data)
                
                if compliance_issues:
                    parsed_data["compliance_issues"] = compliance_issues
                    parsed_data["compliance_score"] = max(0, 100 - len(compliance_issues) * 10)
                else:
                    parsed_data["compliance_score"] = 100
                
                return {
                    "success": True,
                    "message": "Optimización completada exitosamente",
                    "data": parsed_data
                }
                
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "message": f"Error parsing JSON: {str(e)}. Response: {response_text[:200]}...",
                    "data": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "data": None
            }
    
    def _validate_compliance(self, data: Dict[str, Any]) -> List[str]:
        """Validate Amazon compliance rules"""
        issues = []
        
        # Check title length
        title = data.get("title", "")
        if len(title) > self.amazon_rules["title_max_length"]:
            issues.append(f"Título excede {self.amazon_rules['title_max_length']} caracteres")
        
        # Check bullet points length
        bullets = data.get("bullets", [])
        for i, bullet in enumerate(bullets):
            if len(bullet) > self.amazon_rules["bullet_max_length"]:
                issues.append(f"Bullet point {i+1} excede {self.amazon_rules['bullet_max_length']} caracteres")
        
        # Check description length
        description = data.get("description", "")
        if len(description) > self.amazon_rules["description_max_length"]:
            issues.append(f"Descripción excede {self.amazon_rules['description_max_length']} caracteres")
        
        # Check forbidden words
        full_text = f"{title} {description} {' '.join(bullets)}".lower()
        for forbidden_word in self.amazon_rules["forbidden_words"]:
            if forbidden_word.lower() in full_text:
                issues.append(f"Contiene palabra prohibida: '{forbidden_word}'")
        
        return issues