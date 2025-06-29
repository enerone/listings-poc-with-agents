"""
SEO Analyzer Service - Advanced SEO analysis for Amazon listings
"""

import json
import re
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
from app.services.ollama_client import OllamaClient
from app.core.config import settings

class SEOAnalyzer:
    """Advanced SEO analysis capabilities for Amazon listings"""
    
    def __init__(self):
        self.ollama = OllamaClient()
        
        # Spanish Amazon SEO keywords by category
        self.high_value_keywords = {
            "mochila": {
                "primary": ["mochila", "backpack", "bolso", "morral"],
                "modifiers": ["impermeable", "resistente", "antirrobo", "ergonómica", "acolchada"],
                "specs": ["laptop", "15 pulgadas", "17 pulgadas", "usb", "compartimentos"],
                "benefits": ["viaje", "trabajo", "escuela", "universitaria", "deportiva"]
            },
            "auriculares": {
                "primary": ["auriculares", "headphones", "cascos", "audífonos"],
                "modifiers": ["inalámbricos", "bluetooth", "noise cancelling", "hi-fi", "premium"],
                "specs": ["40mm", "20hz", "wireless", "micrófono", "plegables"],
                "benefits": ["música", "gaming", "estudio", "profesional", "deportivos"]
            },
            "smartphone": {
                "primary": ["smartphone", "teléfono", "móvil", "celular"],
                "modifiers": ["libre", "dual sim", "resistente", "5g", "android"],
                "specs": ["64gb", "128gb", "cámara", "batería", "pantalla"],
                "benefits": ["fotografía", "gaming", "trabajo", "estudiantes"]
            },
            "laptop": {
                "primary": ["laptop", "portátil", "notebook", "computadora"],
                "modifiers": ["gaming", "ultrabook", "business", "estudiantes", "profesional"],
                "specs": ["intel", "amd", "ssd", "ram", "pantalla"],
                "benefits": ["trabajo", "estudio", "gaming", "diseño", "programación"]
            }
        }
        
        # Spanish search intent patterns
        self.search_intents = {
            "informational": ["qué es", "cómo", "guía", "tutorial", "comparar"],
            "commercial": ["mejor", "top", "reseña", "opinión", "vs", "comparación"],
            "transactional": ["comprar", "precio", "oferta", "descuento", "barato", "amazon"],
            "navigational": ["marca", "modelo", "oficial", "tienda"]
        }
    
    async def analyze_seo_metrics(self, title: str, description: str, keywords: List[str]) -> Dict[str, Any]:
        """Comprehensive SEO analysis for Amazon listings"""
        
        try:
            # Detect product category
            category = self._detect_category(title.lower() + " " + description.lower())
            
            # Generate enhanced keywords
            enhanced_keywords = await self._generate_enhanced_keywords(title, description, category)
            
            # Analyze search intent
            intent_analysis = self._analyze_search_intent(title, description, keywords)
            
            # SEO optimization recommendations
            seo_recommendations = await self._generate_seo_recommendations(title, description, category)
            
            # Keyword density analysis
            density_analysis = self._analyze_keyword_density(title, description, enhanced_keywords["primary"])
            
            # Title optimization analysis
            title_analysis = self._analyze_title_optimization(title, category)
            
            # Content gaps identification
            content_gaps = self._identify_content_gaps(description, category)
            
            # Simulate search volume and difficulty (in real implementation, would use API)
            search_metrics = self._estimate_search_metrics(enhanced_keywords["all_keywords"])
            
            return {
                "success": True,
                "data": {
                    "category": category,
                    "enhanced_keywords": enhanced_keywords,
                    "search_intent": intent_analysis,
                    "seo_recommendations": seo_recommendations,
                    "keyword_density": density_analysis,
                    "title_optimization": title_analysis,
                    "content_gaps": content_gaps,
                    "search_metrics": search_metrics,
                    "seo_score": self._calculate_seo_score(title_analysis, density_analysis, content_gaps),
                    "generated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en análisis SEO: {str(e)}",
                "data": None
            }
    
    def _detect_category(self, text: str) -> str:
        """Detect product category from text"""
        text = text.lower()
        
        for category in self.high_value_keywords:
            if category in text:
                return category
            
            # Check primary keywords
            for keyword in self.high_value_keywords[category]["primary"]:
                if keyword in text:
                    return category
        
        return "generic"
    
    async def _generate_enhanced_keywords(self, title: str, description: str, category: str) -> Dict[str, Any]:
        """Generate enhanced keyword sets using AI"""
        
        category_keywords = self.high_value_keywords.get(category, self.high_value_keywords["generic"] if "generic" in self.high_value_keywords else {})
        
        # Base keywords from category
        primary_keywords = category_keywords.get("primary", [])
        modifier_keywords = category_keywords.get("modifiers", [])
        spec_keywords = category_keywords.get("specs", [])
        benefit_keywords = category_keywords.get("benefits", [])
        
        # Extract keywords from content
        content_keywords = self._extract_keywords_from_content(title + " " + description)
        
        # Generate long-tail keywords
        long_tail = self._generate_long_tail_keywords(primary_keywords, modifier_keywords, spec_keywords)
        
        # Generate semantic keywords using AI
        semantic_keywords = await self._generate_semantic_keywords(title, description)
        
        all_keywords = list(set(
            primary_keywords + modifier_keywords + spec_keywords + 
            benefit_keywords + content_keywords + long_tail + semantic_keywords
        ))
        
        return {
            "primary": primary_keywords,
            "modifiers": modifier_keywords,
            "specifications": spec_keywords,
            "benefits": benefit_keywords,
            "long_tail": long_tail,
            "semantic": semantic_keywords,
            "content_extracted": content_keywords,
            "all_keywords": all_keywords,
            "total_count": len(all_keywords)
        }
    
    async def _generate_semantic_keywords(self, title: str, description: str) -> List[str]:
        """Generate semantic keywords using AI"""
        
        system_prompt = """Eres un experto en SEO y marketing digital para Amazon España. 
        Genera palabras clave semánticamente relacionadas que los usuarios españoles buscarían.
        
        IMPORTANTE: Responde SOLO con un JSON array de strings. No incluyas explicaciones."""
        
        prompt = f"""
        Genera 10 palabras clave semánticamente relacionadas para este producto de Amazon:
        
        Título: {title}
        Descripción: {description}
        
        Considera:
        - Sinónimos en español
        - Términos relacionados que buscarían los compradores
        - Variaciones coloquiales
        - Keywords de compra (transaccionales)
        
        Formato: ["keyword1", "keyword2", "keyword3", ...]
        """
        
        try:
            result = await self.ollama.generate(
                model=settings.ollama_model,
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            if result["success"]:
                response_text = result["response"].strip()
                
                # Extract JSON from response
                if "[" in response_text and "]" in response_text:
                    start = response_text.find("[")
                    end = response_text.rfind("]") + 1
                    json_text = response_text[start:end]
                    
                    try:
                        keywords = json.loads(json_text)
                        return [kw.lower().strip() for kw in keywords if isinstance(kw, str) and len(kw.strip()) > 2]
                    except json.JSONDecodeError:
                        pass
            
            # Fallback keywords
            return ["producto de calidad", "envío rápido", "mejor precio", "recomendado", "popular"]
            
        except Exception:
            return ["producto de calidad", "envío rápido", "mejor precio"]
    
    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """Extract meaningful keywords from content"""
        
        # Clean and tokenize
        content = re.sub(r'[^\w\s]', ' ', content.lower())
        words = content.split()
        
        # Spanish stop words
        stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le',
            'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'las', 'los', 'una', 'del',
            'este', 'esta', 'estas', 'estos', 'muy', 'más', 'como', 'pero', 'sus', 'está',
            'han', 'fue', 'ser', 'todo', 'todos', 'todas', 'sin', 'sobre', 'hasta', 'hay'
        }
        
        # Filter meaningful words
        keywords = []
        for word in words:
            if (len(word) >= 3 and 
                word not in stop_words and 
                not word.isdigit() and
                word.isalpha()):
                keywords.append(word)
        
        # Return unique keywords
        return list(set(keywords))
    
    def _generate_long_tail_keywords(self, primary: List[str], modifiers: List[str], specs: List[str]) -> List[str]:
        """Generate long-tail keyword combinations"""
        
        long_tail = []
        
        for p in primary[:3]:  # Limit to avoid explosion
            for m in modifiers[:3]:
                long_tail.append(f"{p} {m}")
                
            for s in specs[:3]:
                long_tail.append(f"{p} {s}")
                
            for m in modifiers[:2]:
                for s in specs[:2]:
                    long_tail.append(f"{p} {m} {s}")
        
        return long_tail
    
    def _analyze_search_intent(self, title: str, description: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze search intent patterns"""
        
        content = (title + " " + description).lower()
        intent_scores = {}
        
        for intent, patterns in self.search_intents.items():
            score = 0
            matching_patterns = []
            
            for pattern in patterns:
                if pattern in content:
                    score += 1
                    matching_patterns.append(pattern)
            
            if score > 0:
                intent_scores[intent] = {
                    "score": score,
                    "patterns_found": matching_patterns,
                    "percentage": round((score / len(patterns)) * 100, 1)
                }
        
        # Determine primary intent
        primary_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x]["score"]) if intent_scores else "transactional"
        
        return {
            "primary_intent": primary_intent,
            "intent_breakdown": intent_scores,
            "recommendations": self._get_intent_recommendations(primary_intent)
        }
    
    def _get_intent_recommendations(self, primary_intent: str) -> List[str]:
        """Get recommendations based on search intent"""
        
        recommendations = {
            "informational": [
                "Incluye más detalles técnicos y especificaciones",
                "Añade información de uso y beneficios",
                "Agrega comparaciones con productos similares"
            ],
            "commercial": [
                "Incluye testimonios y reseñas simuladas",
                "Destaca ventajas competitivas",
                "Añade garantías y políticas de devolución"
            ],
            "transactional": [
                "Optimiza el precio y ofertas",
                "Incluye llamadas a la acción claras",
                "Destaca envío rápido y disponibilidad"
            ],
            "navigational": [
                "Menciona la marca claramente",
                "Incluye modelo específico",
                "Añade información oficial del fabricante"
            ]
        }
        
        return recommendations.get(primary_intent, ["Optimiza el contenido para mayor relevancia"])
    
    async def _generate_seo_recommendations(self, title: str, description: str, category: str) -> List[str]:
        """Generate SEO optimization recommendations"""
        
        recommendations = []
        
        # Title analysis
        if len(title) < 50:
            recommendations.append("Considera alargar el título para incluir más keywords relevantes")
        elif len(title) > 200:
            recommendations.append("Acorta el título para mejorar la legibilidad (máximo 200 caracteres)")
        
        # Keyword presence
        if category != "generic":
            category_keywords = self.high_value_keywords[category]["primary"]
            found_keywords = [kw for kw in category_keywords if kw.lower() in title.lower()]
            if len(found_keywords) == 0:
                recommendations.append(f"Incluye palabras clave principales: {', '.join(category_keywords[:3])}")
        
        # Description analysis
        if len(description) < 200:
            recommendations.append("Expande la descripción para incluir más detalles y keywords")
        
        # Technical specifications
        if not any(spec in description.lower() for spec in ["especificaciones", "características", "medidas", "material"]):
            recommendations.append("Incluye especificaciones técnicas detalladas")
        
        # Benefits focus
        if not any(benefit in description.lower() for benefit in ["beneficio", "ventaja", "mejor", "ideal"]):
            recommendations.append("Enfatiza más los beneficios para el usuario")
        
        # Call to action
        if not any(cta in description.lower() for cta in ["compra", "adquiere", "lleva", "obtén"]):
            recommendations.append("Incluye llamadas a la acción suaves")
        
        return recommendations
    
    def _analyze_keyword_density(self, title: str, description: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword density in content"""
        
        content = (title + " " + description).lower()
        word_count = len(content.split())
        
        keyword_analysis = {}
        
        for keyword in keywords[:10]:  # Analyze top 10 keywords
            keyword_lower = keyword.lower()
            count = content.count(keyword_lower)
            density = (count / word_count * 100) if word_count > 0 else 0
            
            keyword_analysis[keyword] = {
                "count": count,
                "density_percentage": round(density, 2),
                "recommendation": self._get_density_recommendation(density)
            }
        
        return {
            "total_words": word_count,
            "keyword_analysis": keyword_analysis,
            "overall_recommendation": self._get_overall_density_recommendation(keyword_analysis)
        }
    
    def _get_density_recommendation(self, density: float) -> str:
        """Get recommendation based on keyword density"""
        
        if density == 0:
            return "Keyword no encontrada - considera incluirla"
        elif density < 1:
            return "Densidad baja - puedes incluirla más veces"
        elif density <= 3:
            return "Densidad óptima"
        else:
            return "Densidad alta - evita sobreoptimización"
    
    def _get_overall_density_recommendation(self, analysis: Dict) -> str:
        """Get overall density recommendation"""
        
        if not analysis:
            return "Incluye más palabras clave relevantes"
        
        optimal_count = sum(1 for kw in analysis.values() if 1 <= kw["density_percentage"] <= 3)
        total_keywords = len(analysis)
        
        if optimal_count / total_keywords >= 0.7:
            return "Excelente optimización de keywords"
        elif optimal_count / total_keywords >= 0.5:
            return "Buena optimización, algunos ajustes menores"
        else:
            return "Necesita mejor distribución de keywords"
    
    def _analyze_title_optimization(self, title: str, category: str) -> Dict[str, Any]:
        """Analyze title optimization for Amazon"""
        
        analysis = {
            "length": len(title),
            "word_count": len(title.split()),
            "character_efficiency": "good" if 50 <= len(title) <= 200 else "needs_improvement",
            "structure_analysis": {},
            "recommendations": []
        }
        
        # Structure analysis
        title_lower = title.lower()
        
        # Brand presence
        has_brand = any(brand in title_lower for brand in ["marca", "brand", "®", "™"])
        analysis["structure_analysis"]["has_brand"] = has_brand
        
        # Product type
        if category != "generic":
            category_keywords = self.high_value_keywords[category]["primary"]
            has_product_type = any(kw in title_lower for kw in category_keywords)
            analysis["structure_analysis"]["has_product_type"] = has_product_type
        
        # Specifications
        has_specs = any(spec in title_lower for spec in ["gb", "pulgadas", "mm", "cm", "litros", "mah"])
        analysis["structure_analysis"]["has_specifications"] = has_specs
        
        # Benefits/features
        has_benefits = any(benefit in title_lower for benefit in ["resistente", "impermeable", "inalámbrico", "premium"])
        analysis["structure_analysis"]["has_benefits"] = has_benefits
        
        # Generate recommendations
        if not has_brand:
            analysis["recommendations"].append("Considera incluir la marca si es reconocida")
        
        if category != "generic" and not analysis["structure_analysis"].get("has_product_type", False):
            analysis["recommendations"].append("Incluye el tipo de producto claramente")
        
        if not has_specs:
            analysis["recommendations"].append("Añade especificaciones técnicas relevantes")
        
        if not has_benefits:
            analysis["recommendations"].append("Incluye características/beneficios clave")
        
        return analysis
    
    def _identify_content_gaps(self, description: str, category: str) -> Dict[str, Any]:
        """Identify content gaps in product description"""
        
        description_lower = description.lower()
        gaps = []
        
        # Essential elements for Amazon listings
        essential_elements = {
            "materials": ["material", "fabricado", "hecho de"],
            "dimensions": ["medidas", "tamaño", "dimensiones", "cm", "mm"],
            "weight": ["peso", "gramos", "kg", "liviano", "ligero"],
            "warranty": ["garantía", "warranty", "devolución"],
            "certifications": ["certificado", "ce", "fcc", "rohs"],
            "usage": ["uso", "ideal para", "perfecto para"],
            "maintenance": ["cuidado", "limpieza", "mantenimiento"],
            "compatibility": ["compatible", "compatibilidad"]
        }
        
        missing_elements = []
        for element, keywords in essential_elements.items():
            if not any(keyword in description_lower for keyword in keywords):
                missing_elements.append(element)
        
        # Category-specific gaps
        if category in self.high_value_keywords:
            category_specs = self.high_value_keywords[category].get("specs", [])
            missing_specs = [spec for spec in category_specs if spec not in description_lower]
            
            if missing_specs:
                gaps.append({
                    "type": "missing_specifications",
                    "details": f"Especificaciones faltantes: {', '.join(missing_specs[:3])}"
                })
        
        # Content length analysis
        if len(description) < 300:
            gaps.append({
                "type": "content_length",
                "details": "Descripción muy corta, expande con más detalles"
            })
        
        # Missing elements
        if missing_elements:
            gaps.append({
                "type": "missing_elements", 
                "details": f"Elementos faltantes: {', '.join(missing_elements[:3])}"
            })
        
        return {
            "gaps_found": len(gaps),
            "gaps": gaps,
            "priority_fixes": gaps[:3],  # Top 3 most important
            "completion_score": max(0, 100 - (len(missing_elements) * 10))
        }
    
    def _estimate_search_metrics(self, keywords: List[str]) -> Dict[str, Any]:
        """Estimate search metrics (in real implementation, would use SEO APIs)"""
        
        # Simulate realistic metrics based on keyword characteristics
        metrics = {}
        
        for keyword in keywords[:20]:  # Limit to top 20
            keyword_hash = hashlib.md5(keyword.encode()).hexdigest()
            
            # Simulate search volume (based on keyword length and type)
            base_volume = 1000
            if len(keyword) <= 10:  # Short keywords have higher volume
                volume_modifier = 5
            elif len(keyword) <= 20:
                volume_modifier = 3
            else:
                volume_modifier = 1
            
            # Use hash for consistent randomness
            volume = (int(keyword_hash[:4], 16) % 5000) * volume_modifier + base_volume
            
            # Simulate difficulty (0-100)
            difficulty = (int(keyword_hash[4:6], 16) % 70) + 10  # 10-80 range
            
            # Estimate CPC
            cpc = round(0.15 + (int(keyword_hash[6:8], 16) % 200) / 100, 2)
            
            metrics[keyword] = {
                "estimated_search_volume": volume,
                "estimated_difficulty": difficulty,
                "estimated_cpc_eur": cpc,
                "opportunity_score": self._calculate_opportunity_score(volume, difficulty)
            }
        
        return {
            "total_keywords_analyzed": len(metrics),
            "keyword_metrics": metrics,
            "top_opportunities": self._get_top_opportunities(metrics),
            "average_difficulty": round(sum(m["estimated_difficulty"] for m in metrics.values()) / len(metrics), 1) if metrics else 0
        }
    
    def _calculate_opportunity_score(self, volume: int, difficulty: int) -> int:
        """Calculate opportunity score (high volume, low difficulty = high opportunity)"""
        
        # Normalize values
        volume_score = min(volume / 10000 * 50, 50)  # Max 50 points for volume
        difficulty_penalty = difficulty / 100 * 30  # Max 30 point penalty for difficulty
        
        opportunity = max(0, int(volume_score - difficulty_penalty + 20))  # Base 20 points
        return min(opportunity, 100)
    
    def _get_top_opportunities(self, metrics: Dict) -> List[Dict]:
        """Get top keyword opportunities"""
        
        opportunities = []
        for keyword, data in metrics.items():
            opportunities.append({
                "keyword": keyword,
                "opportunity_score": data["opportunity_score"],
                "search_volume": data["estimated_search_volume"],
                "difficulty": data["estimated_difficulty"]
            })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return opportunities[:5]
    
    def _calculate_seo_score(self, title_analysis: Dict, density_analysis: Dict, content_gaps: Dict) -> int:
        """Calculate overall SEO score"""
        
        score = 0
        
        # Title optimization score (30 points)
        if title_analysis["character_efficiency"] == "good":
            score += 15
        
        structure_score = sum(1 for v in title_analysis["structure_analysis"].values() if v)
        score += min(structure_score * 3, 15)
        
        # Keyword density score (30 points)
        if density_analysis["keyword_analysis"]:
            optimal_keywords = sum(1 for kw in density_analysis["keyword_analysis"].values() 
                                 if 1 <= kw["density_percentage"] <= 3)
            total_keywords = len(density_analysis["keyword_analysis"])
            density_score = (optimal_keywords / total_keywords) * 30
            score += int(density_score)
        
        # Content completeness score (40 points)
        completion_score = content_gaps.get("completion_score", 50)
        score += int(completion_score * 0.4)
        
        return min(score, 100)