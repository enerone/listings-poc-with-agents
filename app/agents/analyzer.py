import json
from typing import Dict, Any, List, Optional
from app.services.ollama_client import OllamaClient
from app.agents.competitor_researcher import CompetitorResearcher
from app.services.seo_analyzer import SEOAnalyzer
from app.services.market_intelligence import MarketIntelligence
from app.core.logger import LoggerMixin
from app.core.exceptions import AIGenerationError, ValidationError
from app.core.config import settings
from app.core.cache import cache_language_detection, cache_competitor_research


class AnalyzerAgent(LoggerMixin):
    """Refactored analyzer agent with better structure and logging."""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.model = settings.ollama_model
        self.competitor_researcher = CompetitorResearcher()
        self.seo_analyzer = SEOAnalyzer()
        self.market_intelligence = MarketIntelligence()
    
    async def analyze(self, title: str, description: str) -> Dict[str, Any]:
        """
        Main analysis method - orchestrates the entire analysis process.
        
        Args:
            title: Product title to analyze
            description: Product description to analyze
            
        Returns:
            Dict containing analysis results
            
        Raises:
            AIGenerationError: If analysis fails
            ValidationError: If input validation fails
        """
        self.log_operation_start("product_analysis", title=title[:50])
        
        try:
            # Validate inputs
            self._validate_inputs(title, description)
            
            # Step 1: Detect language
            input_language = self._detect_language(title, description)
            self.logger.info("Language detected", language=input_language)
            
            # Step 2: Research competitors
            competitor_data = await self._research_competitors(title, description)
            
            # Step 3: Analyze SEO metrics
            seo_analysis = await self.seo_analyzer.analyze_seo_metrics(
                title, description, competitor_data.get("keywords", [])
            )
            
            # Step 4: Analyze market intelligence
            market_analysis = await self.market_intelligence.analyze_market_competition(
                title, description, max_competitors=8
            )
            
            # Step 5: Generate AI analysis with enhanced data
            analysis_result = await self._generate_ai_analysis(
                title, description, competitor_data, input_language, seo_analysis, market_analysis
            )
            
            # Step 6: Format and enhance response with all data
            final_result = self._format_analysis_response(
                analysis_result, competitor_data, input_language, seo_analysis, market_analysis
            )
            
            self.log_operation_success("product_analysis", 
                                     title_length=len(final_result.get("data", {}).get("title", "")))
            
            return final_result
            
        except (AIGenerationError, ValidationError):
            raise
        except Exception as e:
            self.log_operation_error("product_analysis", e, title=title[:50])
            raise AIGenerationError(f"Unexpected error during analysis: {str(e)}")
    
    def _validate_inputs(self, title: str, description: str) -> None:
        """Validate input parameters."""
        if not title or not title.strip():
            raise ValidationError("Title is required")
        
        if not description or not description.strip():
            raise ValidationError("Description is required")
        
        if len(title) > 1000:
            raise ValidationError("Title too long (max 1000 characters)")
        
        if len(description) > 10000:
            raise ValidationError("Description too long (max 10000 characters)")
    
    @cache_competitor_research(ttl=7200)  # Cache for 2 hours  
    async def _research_competitors(self, title: str, description: str) -> Dict[str, Any]:
        """Research competitors for the given product."""
        self.log_operation_start("competitor_research", title=title[:50])
        
        try:
            competitor_data = await self.competitor_researcher.research_competitors(title, description)
            
            success = competitor_data.get("success", False)
            competitors_found = competitor_data.get("data", {}).get("competitors_found", 0) if success else 0
            
            self.log_operation_success("competitor_research", 
                                     success=success, 
                                     competitors_found=competitors_found)
            
            return competitor_data
            
        except Exception as e:
            self.log_operation_error("competitor_research", e, title=title[:50])
            return {"success": False, "data": None, "error": str(e)}
    
    async def _generate_ai_analysis(self, title: str, description: str, 
                                  competitor_data: Dict[str, Any], language: str,
                                  seo_analysis: Optional[Dict[str, Any]] = None,
                                  market_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate AI analysis using Ollama."""
        self.log_operation_start("ai_generation", language=language)
        
        try:
            # Build prompts
            system_prompt = self._build_system_prompt(language)
            user_prompt = self._build_user_prompt(title, description, competitor_data, language, seo_analysis, market_analysis)
            
            # Generate response
            result = await self.ollama.generate(
                model=self.model,
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            if not result["success"]:
                raise AIGenerationError(f"Ollama generation failed: {result.get('error', 'Unknown error')}")
            
            # Parse and validate JSON response
            parsed_data = self._parse_ai_response(result["response"])
            
            self.log_operation_success("ai_generation", 
                                     title_generated=bool(parsed_data.get("title")),
                                     bullets_count=len(parsed_data.get("bullets", [])))
            
            return parsed_data
            
        except AIGenerationError:
            raise
        except Exception as e:
            self.log_operation_error("ai_generation", e)
            raise AIGenerationError(f"AI generation failed: {str(e)}")
    
    def _build_system_prompt(self, language: str) -> str:
        """Build system prompt based on detected language."""
        language_instruction = self._get_language_instruction(language)
        
        return f"""You are an Amazon listing expert with access to competitor research data. Your job is to analyze a product and create an optimized Amazon listing in SPANISH ONLY that outperforms competitors.

CRITICAL LANGUAGE RULES:
{language_instruction}

- Output ONLY valid JSON with no additional text
- ALL content must be in PERFECT SPANISH (no English, Chinese, or other languages)
- Use proper Spanish grammar and vocabulary ONLY
- Create professional e-commerce content for Spanish-speaking markets
- Do NOT mix languages, do NOT use made-up words
- If input is in other language, translate EVERYTHING to Spanish first

Generate:
1. Optimized Spanish title (max 200 characters) with relevant keywords
2. Detailed and persuasive Spanish description
3. 5 bullet points in Spanish highlighting key benefits
4. List of Spanish keywords for SEO

Response format (JSON ONLY):
{{
    "title": "Spanish optimized title here",
    "description": "Detailed Spanish description here",
    "bullets": ["Spanish benefit 1", "Spanish benefit 2", "Spanish benefit 3", "Spanish benefit 4", "Spanish benefit 5"],
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}"""
    
    def _build_user_prompt(self, title: str, description: str, 
                          competitor_data: Dict[str, Any], language: str,
                          seo_analysis: Optional[Dict[str, Any]] = None,
                          market_analysis: Optional[Dict[str, Any]] = None) -> str:
        """Build user prompt with competitor context."""
        competitor_context = self._build_competitor_context(competitor_data)
        seo_context = self._build_seo_context(seo_analysis)
        market_context = self._build_market_context(market_analysis)
        
        return f"""
Analyze this product and create a professional Amazon listing in SPANISH that beats the competition:

PRODUCT TO ANALYZE:
Title: {title}
Description: {description}

{competitor_context}

{seo_context}

{market_context}

REQUIREMENTS:
- Translate and improve content to Spanish if needed
- Create attractive, SEO-optimized Spanish title that outperforms competitors
- Write persuasive Spanish description highlighting unique benefits vs competitors
- Include 5 key selling points in Spanish that differentiate from competition
- Suggest relevant Spanish keywords based on market analysis
- Use competitor insights to identify and fill market gaps
- Position product advantageously against competition
- Output MUST be 100% in Spanish language
- NO English, Chinese, or mixed languages allowed
- Use proper Spanish grammar and vocabulary

CREATE A LISTING THAT STANDS OUT AND WINS AGAINST COMPETITORS!

Respond with JSON only.
"""
    
    def _build_competitor_context(self, competitor_data: Dict[str, Any]) -> str:
        """Build competitor context string for the prompt."""
        if not competitor_data.get("success") or not competitor_data.get("data"):
            self.logger.warning("No competitor data available for context")
            return "⚠️ No competitor data available, using basic analysis"
        
        comp_data = competitor_data["data"]
        return f"""
🏆 COMPETITOR INTELLIGENCE - USE THIS DATA TO DOMINATE THE MARKET:

MARKET ANALYSIS:
- {comp_data.get('competitors_found', 0)} competidores activos encontrados
- Características MÁS POPULARES: {', '.join(comp_data.get('common_features', [])[:5])}
- Puntos de venta EXITOSOS: {', '.join(comp_data.get('selling_points', [])[:3])}
- OPORTUNIDADES DE MERCADO: {', '.join(comp_data.get('market_gaps', [])[:3])}

ESTRATEGIA COMPETITIVA:
{chr(10).join(['- ' + rec for rec in comp_data.get('recommendations', [])[:3]])}

INSTRUCCIONES CRÍTICAS:
- INCLUYE las características populares del mercado en tu listing
- DIFERÉNCIATE destacando ventajas únicas vs competidores  
- APROVECHA las oportunidades de mercado identificadas
- USA terminología que ya funciona en el mercado
- POSICIONA el producto como SUPERIOR a la competencia

¡CREA UN LISTING QUE APLASTE A LA COMPETENCIA!
"""
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and clean AI response to extract JSON."""
        self.logger.debug("Parsing AI response", response_length=len(response_text))
        
        # Clean response text
        cleaned_text = self._clean_response_text(response_text)
        
        try:
            parsed_data = json.loads(cleaned_text)
            
            # Validate required fields
            required_fields = ["title", "description", "bullets", "keywords"]
            missing_fields = [field for field in required_fields if field not in parsed_data]
            
            if missing_fields:
                raise AIGenerationError(f"Missing required fields: {missing_fields}")
            
            # Validate data types
            if not isinstance(parsed_data.get("bullets"), list):
                raise AIGenerationError("Bullets must be a list")
            
            if not isinstance(parsed_data.get("keywords"), list):
                raise AIGenerationError("Keywords must be a list")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            self.logger.error("JSON parsing failed", error=str(e), response_preview=cleaned_text[:200])
            raise AIGenerationError(f"Invalid JSON response: {str(e)}")
    
    def _clean_response_text(self, response_text: str) -> str:
        """Clean and extract JSON from AI response."""
        cleaned = response_text.strip()
        
        # Remove thinking tags
        if "<think>" in cleaned:
            if "</think>" in cleaned:
                think_end = cleaned.find("</think>") + 8
                cleaned = cleaned[think_end:].strip()
            else:
                json_start = cleaned.find("{")
                if json_start > 0:
                    cleaned = cleaned[json_start:].strip()
        
        # Remove markdown code blocks
        if "```json" in cleaned:
            json_start = cleaned.find("```json") + 7
            json_end = cleaned.find("```", json_start)
            cleaned = cleaned[json_start:json_end].strip()
        elif "```" in cleaned:
            json_start = cleaned.find("```") + 3
            json_end = cleaned.find("```", json_start)
            cleaned = cleaned[json_start:json_end].strip()
        
        # Extract JSON object
        if "{" in cleaned:
            start_brace = cleaned.find("{")
            brace_count = 0
            end_brace = start_brace
            
            for i, char in enumerate(cleaned[start_brace:], start_brace):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_brace = i
                        break
            
            if brace_count == 0:
                cleaned = cleaned[start_brace:end_brace + 1]
        
        return cleaned
    
    def _format_analysis_response(self, parsed_data: Dict[str, Any], 
                                 competitor_data: Dict[str, Any], language: str,
                                 seo_analysis: Optional[Dict[str, Any]] = None,
                                 market_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format the final analysis response."""
        # Enhance with competitor intelligence
        competitor_info = self._extract_competitor_info(competitor_data)
        
        # Enhance keywords with competitor data
        if competitor_info and competitor_data.get("success"):
            parsed_data = self._enhance_keywords_with_competitor_data(parsed_data, competitor_data["data"])
        
        # Extract SEO and market data for response
        seo_data = seo_analysis.get("data", {}) if seo_analysis and seo_analysis.get("success") else {}
        market_data = market_analysis.get("data", {}) if market_analysis and market_analysis.get("success") else {}
        
        result_data = {
            **parsed_data,
            "competitor_intelligence": competitor_info,
            "seo_analysis": {
                "seo_score": seo_data.get("seo_score", 0),
                "enhanced_keywords": seo_data.get("enhanced_keywords", {}),
                "search_intent": seo_data.get("search_intent", {}),
                "content_gaps": seo_data.get("content_gaps", {}),
                "recommendations": seo_data.get("seo_recommendations", [])
            },
            "market_intelligence": {
                "competitors_analyzed": market_data.get("competitors_analyzed", 0),
                "pricing_analysis": market_data.get("pricing_analysis", {}),
                "market_gaps": market_data.get("market_gaps", {}),
                "competitive_insights": market_data.get("competitive_insights", []),
                "brand_landscape": market_data.get("brand_landscape", {})
            },
            "analysis_enhanced_with_market_data": competitor_data.get("success", False),
            "input_language_detected": language
        }
        
        return {
            "success": True,
            "message": "Análisis completado con SEO, inteligencia de mercado y análisis competitivo",
            "data": result_data
        }
    
    def _extract_competitor_info(self, competitor_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract competitor information for the response."""
        if not competitor_data.get("success") or not competitor_data.get("data"):
            return None
        
        comp_data = competitor_data["data"]
        return {
            "competitors_analyzed": comp_data.get("competitors_found", 0),
            "market_features": comp_data.get("common_features", []),
            "popular_selling_points": comp_data.get("selling_points", []),
            "market_gaps": comp_data.get("market_gaps", []),
            "strategic_recommendations": comp_data.get("recommendations", []),
            "keywords_from_market": comp_data.get("keywords_used", []),
            "pricing_insights": comp_data.get("pricing_insights", {}),
            "title_patterns": comp_data.get("title_patterns", [])
        }
    
    def _enhance_keywords_with_competitor_data(self, parsed_data: Dict[str, Any], 
                                             comp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance keywords with competitor data."""
        comp_features = comp_data.get("common_features", [])
        if comp_features and "keywords" in parsed_data:
            existing_keywords = parsed_data["keywords"]
            enhanced_keywords = list(set(existing_keywords + comp_features[:3]))
            parsed_data["keywords"] = enhanced_keywords[:10]
        
        return parsed_data
    
    @cache_language_detection(ttl=86400)  # Cache for 24 hours
    def _detect_language(self, title: str, description: str) -> str:
        """Detect the primary language of the input text."""
        text = f"{title} {description}".lower()
        
        # Language indicators
        spanish_words = {
            'el', 'la', 'de', 'en', 'con', 'para', 'por', 'que', 'es', 'una', 'del', 'las', 'los', 
            'se', 'su', 'al', 'más', 'como', 'pero', 'todo', 'esta', 'sus', 'le', 'ya', 'o', 
            'porque', 'cuando', 'sin', 'sobre', 'también', 'me', 'hasta', 'donde', 'ser', 'tiene'
        }
        
        english_words = {
            'the', 'and', 'for', 'are', 'with', 'his', 'they', 'this', 'have', 'from', 'or', 
            'one', 'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 
            'your', 'can', 'said', 'there', 'each', 'which', 'she', 'do', 'how', 'their'
        }
        
        words = set(text.split())
        spanish_count = len(words.intersection(spanish_words))
        english_count = len(words.intersection(english_words))
        
        # Check for Spanish characters
        if any(char in text for char in 'ñáéíóú'):
            return 'spanish'
        
        if spanish_count > english_count:
            return 'spanish'
        elif english_count > spanish_count:
            return 'english'
        else:
            return 'mixed'
    
    def _get_language_instruction(self, detected_language: str) -> str:
        """Get specific instructions based on detected input language."""
        instructions = {
            'spanish': """
- INPUT IS IN SPANISH: Perfect! Keep everything in Spanish
- DO NOT translate - just improve and optimize the Spanish content
- Use natural Spanish vocabulary and grammar
- Maintain Spanish cultural context and expressions
""",
            'english': """
- INPUT IS IN ENGLISH: Translate EVERYTHING to Spanish
- Convert all English text to natural, fluent Spanish
- Do NOT keep any English words or phrases
- Use Spanish product terminology and expressions
- Make it sound like native Spanish content, not a translation
""",
            'mixed': """
- INPUT HAS MIXED LANGUAGES: Clean up and convert ALL to Spanish
- Remove ALL non-Spanish words completely
- Translate foreign content to natural Spanish
- Create coherent Spanish content from the mixed input
- Result must be 100% Spanish with no language mixing
- Do NOT create invented words - use real Spanish vocabulary
"""
        }
        
        return instructions.get(detected_language, instructions['mixed'])
    
    def _build_seo_context(self, seo_analysis: Optional[Dict[str, Any]]) -> str:
        """Build SEO context string for the prompt."""
        if not seo_analysis or not seo_analysis.get("success"):
            return "SEO ANALYSIS: No SEO data available"
        
        seo_data = seo_analysis.get("data", {})
        enhanced_keywords = seo_data.get("enhanced_keywords", {})
        seo_recommendations = seo_data.get("seo_recommendations", [])
        search_intent = seo_data.get("search_intent", {})
        
        context = "SEO ANALYSIS:\n"
        
        # Enhanced keywords
        if enhanced_keywords.get("all_keywords"):
            context += f"- Palabras clave sugeridas: {', '.join(enhanced_keywords['all_keywords'][:10])}\n"
        
        if enhanced_keywords.get("long_tail"):
            context += f"- Keywords long-tail: {', '.join(enhanced_keywords['long_tail'][:5])}\n"
        
        # Search intent
        primary_intent = search_intent.get("primary_intent", "transactional")
        context += f"- Intención de búsqueda principal: {primary_intent}\n"
        
        # SEO recommendations
        if seo_recommendations:
            context += "- Recomendaciones SEO:\n"
            for rec in seo_recommendations[:3]:
                context += f"  * {rec}\n"
        
        # SEO score
        seo_score = seo_data.get("seo_score", 0)
        context += f"- Score SEO actual: {seo_score}/100\n"
        
        return context
    
    def _build_market_context(self, market_analysis: Optional[Dict[str, Any]]) -> str:
        """Build market context string for the prompt."""
        if not market_analysis or not market_analysis.get("success"):
            return "MARKET ANALYSIS: No market data available"
        
        market_data = market_analysis.get("data", {})
        pricing_analysis = market_data.get("pricing_analysis", {})
        competitive_insights = market_data.get("competitive_insights", [])
        market_gaps = market_data.get("market_gaps", {})
        brand_landscape = market_data.get("brand_landscape", {})
        
        context = "COMPETITIVE MARKET ANALYSIS:\n"
        
        # Competitor count
        competitors_count = market_data.get("competitors_analyzed", 0)
        context += f"- Competidores analizados: {competitors_count}\n"
        
        # Pricing insights
        if pricing_analysis.get("analysis_possible"):
            price_range = pricing_analysis.get("price_range", {})
            context += f"- Rango de precios del mercado: {price_range.get('min', 0):.2f}€ - {price_range.get('max', 0):.2f}€\n"
            context += f"- Precio promedio: {price_range.get('average', 0):.2f}€\n"
            
            recommendations = pricing_analysis.get("market_position_recommendations", [])
            if recommendations:
                context += f"- Estrategia de precio recomendada: {recommendations[0]}\n"
        
        # Market gaps
        gaps = market_gaps.get("gaps", [])
        if gaps:
            context += "- Oportunidades de mercado:\n"
            for gap in gaps[:3]:
                context += f"  * {gap.get('details', gap)}\n"
        
        # Competitive insights
        if competitive_insights:
            context += "- Insights competitivos:\n"
            for insight in competitive_insights[:3]:
                context += f"  * {insight}\n"
        
        # Brand landscape
        brand_strategy = brand_landscape.get("brand_strategy_recommendation", "")
        if brand_strategy:
            context += f"- Estrategia de marca recomendada: {brand_strategy}\n"
        
        return context