"""
Market Intelligence Service - Advanced competitor analysis and market insights
"""

import json
import re
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
from app.services.ollama_client import OllamaClient
from app.services.web_search import WebSearchService
from app.core.config import settings

class MarketIntelligence:
    """Advanced market analysis and competitive intelligence"""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.web_search = WebSearchService()
        
        # Price extraction patterns
        self.price_patterns = {
            'eur': [
                r'(\d+[,.]?\d*)\s*€',
                r'€\s*(\d+[,.]?\d*)',
                r'(\d+[,.]?\d*)\s*euros?',
                r'precio[:\s]*(\d+[,.]?\d*)',
            ],
            'usd': [
                r'\$\s*(\d+[,.]?\d*)',
                r'(\d+[,.]?\d*)\s*\$',
                r'(\d+[,.]?\d*)\s*dólares?'
            ]
        }
        
        # Feature extraction patterns
        self.feature_patterns = {
            'connectivity': ['wifi', 'bluetooth', 'usb', '5g', '4g', 'wireless', 'inalámbrico'],
            'materials': ['aluminio', 'acero', 'plástico', 'cuero', 'tela', 'metal', 'silicona'],
            'certifications': ['ip67', 'ip68', 'ce', 'fcc', 'rohs', 'waterproof', 'impermeable'],
            'battery': ['mah', 'batería', 'battery', 'recargable', 'duración', 'autonomía'],
            'display': ['pantalla', 'lcd', 'oled', 'retina', 'hd', '4k', 'pulgadas'],
            'storage': ['gb', 'tb', 'ssd', 'hdd', 'almacenamiento', 'memoria'],
            'performance': ['procesador', 'cpu', 'gpu', 'ram', 'ghz', 'cores']
        }
    
    async def analyze_market_competition(self, title: str, description: str, max_competitors: int = 10) -> Dict[str, Any]:
        """Comprehensive competitive analysis"""
        
        try:
            # Search for competitors
            competitors = await self._find_competitors(title, description, max_competitors)
            
            # Analyze pricing strategies
            pricing_analysis = self._analyze_pricing_strategies(competitors)
            
            # Extract common features
            feature_analysis = self._analyze_competitor_features(competitors)
            
            # Market positioning analysis
            positioning = await self._analyze_market_positioning(title, description, competitors)
            
            # Identify market gaps
            market_gaps = self._identify_market_gaps(competitors, feature_analysis)
            
            # Generate competitive insights
            insights = await self._generate_competitive_insights(title, description, competitors, feature_analysis)
            
            # Brand analysis
            brand_analysis = self._analyze_brand_landscape(competitors)
            
            return {
                "success": True,
                "data": {
                    "competitors_analyzed": len(competitors),
                    "competitors": competitors,
                    "pricing_analysis": pricing_analysis,
                    "feature_analysis": feature_analysis,
                    "market_positioning": positioning,
                    "market_gaps": market_gaps,
                    "competitive_insights": insights,
                    "brand_landscape": brand_analysis,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en análisis competitivo: {str(e)}",
                "data": None
            }
    
    async def _find_competitors(self, title: str, description: str, max_competitors: int) -> List[Dict[str, Any]]:
        """Find competitor products using web search"""
        
        # Extract key search terms
        search_terms = self._extract_search_terms(title, description)
        
        competitors = []
        
        for search_term in search_terms[:3]:  # Search with top 3 terms
            try:
                # Search for competitors
                search_query = f"{search_term} amazon precio"
                results = await self.web_search.search(search_query, max_results=max_competitors)
                
                for result in results:
                    competitor = self._process_competitor_result(result, search_term)
                    if competitor and len(competitors) < max_competitors:
                        competitors.append(competitor)
                
                # Add simulated competitors for demo purposes
                if len(competitors) < 5:
                    simulated = self._generate_simulated_competitors(search_term, 5 - len(competitors))
                    competitors.extend(simulated)
                
            except Exception as e:
                print(f"Error searching for term '{search_term}': {e}")
        
        return competitors[:max_competitors]
    
    def _extract_search_terms(self, title: str, description: str) -> List[str]:
        """Extract relevant search terms for competitor research"""
        
        content = f"{title} {description}".lower()
        
        # Common Spanish stop words
        stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le',
            'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'las', 'los', 'una',
            'este', 'esta', 'muy', 'más', 'como', 'pero', 'sus', 'está', 'todo', 'sin'
        }
        
        # Extract meaningful terms
        words = re.findall(r'\b\w+\b', content)
        meaningful_words = [w for w in words if len(w) >= 3 and w not in stop_words and not w.isdigit()]
        
        # Generate search terms (combinations of 1-3 words)
        search_terms = []
        
        # Single words
        search_terms.extend(meaningful_words[:10])
        
        # Two-word combinations
        for i in range(min(5, len(meaningful_words) - 1)):
            search_terms.append(f"{meaningful_words[i]} {meaningful_words[i+1]}")
        
        return search_terms[:15]
    
    def _process_competitor_result(self, result: Dict, search_term: str) -> Optional[Dict[str, Any]]:
        """Process a search result into competitor data"""
        
        try:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            url = result.get("url", "")
            
            if not title or len(title) < 10:
                return None
            
            # Extract price if available
            price = self._extract_price_from_text(f"{title} {snippet}")
            
            # Extract features
            features = self._extract_features_from_text(f"{title} {snippet}")
            
            # Estimate relevance
            relevance = self._calculate_relevance(title + " " + snippet, search_term)
            
            return {
                "title": title,
                "snippet": snippet,
                "url": url,
                "extracted_price": price,
                "features": features,
                "relevance_score": relevance,
                "source": "web_search",
                "search_term": search_term
            }
            
        except Exception:
            return None
    
    def _extract_price_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract price information from text"""
        
        text = text.lower()
        
        for currency, patterns in self.price_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    price_str = match.group(1).replace(',', '.')
                    try:
                        price_value = float(price_str)
                        return {
                            "value": price_value,
                            "currency": currency,
                            "raw_text": match.group(0)
                        }
                    except ValueError:
                        continue
        
        return None
    
    def _extract_features_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract product features from text"""
        
        text = text.lower()
        extracted_features = {}
        
        for category, keywords in self.feature_patterns.items():
            found_features = []
            for keyword in keywords:
                if keyword in text:
                    found_features.append(keyword)
            
            if found_features:
                extracted_features[category] = found_features
        
        return extracted_features
    
    def _calculate_relevance(self, text: str, search_term: str) -> float:
        """Calculate relevance score between text and search term"""
        
        text = text.lower()
        search_term = search_term.lower()
        
        # Basic keyword matching
        search_words = search_term.split()
        text_words = text.split()
        
        matches = sum(1 for word in search_words if word in text_words)
        relevance = matches / len(search_words) if search_words else 0
        
        return round(relevance, 2)
    
    def _generate_simulated_competitors(self, search_term: str, count: int) -> List[Dict[str, Any]]:
        """Generate simulated competitor data for demo purposes"""
        
        competitors = []
        
        for i in range(count):
            # Generate consistent data based on search term
            term_hash = hashlib.md5(f"{search_term}{i}".encode()).hexdigest()
            
            # Simulate price
            base_price = 20 + (int(term_hash[:4], 16) % 300)
            price = {
                "value": base_price,
                "currency": "eur",
                "raw_text": f"{base_price}€"
            }
            
            # Simulate features
            simulated_features = self._generate_simulated_features(search_term, term_hash)
            
            competitors.append({
                "title": f"Producto Similar {i+1} - {search_term.title()}",
                "snippet": f"Excelente {search_term} con características premium y garantía...",
                "url": f"https://example-marketplace.com/product-{term_hash[:8]}",
                "extracted_price": price,
                "features": simulated_features,
                "relevance_score": 0.8 - (i * 0.1),
                "source": "simulated",
                "search_term": search_term
            })
        
        return competitors
    
    def _generate_simulated_features(self, search_term: str, term_hash: str) -> Dict[str, List[str]]:
        """Generate simulated features based on search term"""
        
        features = {}
        
        # Common features based on product type
        if any(word in search_term.lower() for word in ['mochila', 'bolso', 'bag']):
            features['materials'] = ['tela', 'aluminio']
            features['certifications'] = ['impermeable']
            features['storage'] = ['compartimentos']
        
        elif any(word in search_term.lower() for word in ['auriculares', 'headphones']):
            features['connectivity'] = ['bluetooth', 'wireless']
            features['battery'] = ['batería']
            features['performance'] = ['drivers']
        
        elif any(word in search_term.lower() for word in ['smartphone', 'teléfono']):
            features['display'] = ['pantalla', 'hd']
            features['storage'] = ['gb']
            features['connectivity'] = ['5g', 'wifi']
        
        return features
    
    def _analyze_pricing_strategies(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze competitor pricing strategies"""
        
        prices = []
        for comp in competitors:
            if comp.get("extracted_price") and comp["extracted_price"].get("value"):
                prices.append(comp["extracted_price"]["value"])
        
        if not prices:
            return {
                "analysis_possible": False,
                "message": "No se encontraron precios suficientes para análisis"
            }
        
        # Calculate statistics
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        median_price = sorted(prices)[len(prices) // 2]
        
        # Pricing segments
        segments = self._categorize_pricing_segments(prices)
        
        # Pricing recommendations
        recommendations = self._generate_pricing_recommendations(avg_price, min_price, max_price)
        
        return {
            "analysis_possible": True,
            "price_range": {
                "min": min_price,
                "max": max_price,
                "average": round(avg_price, 2),
                "median": median_price
            },
            "pricing_segments": segments,
            "market_position_recommendations": recommendations,
            "total_prices_analyzed": len(prices)
        }
    
    def _categorize_pricing_segments(self, prices: List[float]) -> Dict[str, Any]:
        """Categorize pricing into market segments"""
        
        if not prices:
            return {}
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        # Define segments
        budget_threshold = min_price + (price_range * 0.33)
        premium_threshold = min_price + (price_range * 0.67)
        
        segments = {
            "budget": {"min": min_price, "max": budget_threshold, "count": 0},
            "mid_range": {"min": budget_threshold, "max": premium_threshold, "count": 0},
            "premium": {"min": premium_threshold, "max": max_price, "count": 0}
        }
        
        # Count products in each segment
        for price in prices:
            if price <= budget_threshold:
                segments["budget"]["count"] += 1
            elif price <= premium_threshold:
                segments["mid_range"]["count"] += 1
            else:
                segments["premium"]["count"] += 1
        
        return segments
    
    def _generate_pricing_recommendations(self, avg_price: float, min_price: float, max_price: float) -> List[str]:
        """Generate pricing strategy recommendations"""
        
        recommendations = []
        
        price_range = max_price - min_price
        
        # Competitive pricing
        competitive_price = avg_price * 0.95  # 5% below average
        recommendations.append(f"Precio competitivo sugerido: {competitive_price:.2f}€ (5% por debajo del promedio)")
        
        # Value positioning
        value_price = min_price + (price_range * 0.4)
        recommendations.append(f"Posicionamiento de valor: {value_price:.2f}€ (balance precio-calidad)")
        
        # Premium positioning
        if max_price > avg_price * 1.5:
            premium_price = avg_price * 1.2
            recommendations.append(f"Posicionamiento premium: {premium_price:.2f}€ (diferenciación por calidad)")
        
        return recommendations
    
    def _analyze_competitor_features(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze common features across competitors"""
        
        all_features = {}
        feature_frequency = {}
        
        for comp in competitors:
            features = comp.get("features", {})
            for category, feature_list in features.items():
                if category not in all_features:
                    all_features[category] = set()
                    feature_frequency[category] = {}
                
                for feature in feature_list:
                    all_features[category].add(feature)
                    feature_frequency[category][feature] = feature_frequency[category].get(feature, 0) + 1
        
        # Find most common features
        common_features = {}
        for category, features in feature_frequency.items():
            sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
            common_features[category] = sorted_features[:5]  # Top 5 per category
        
        # Calculate market standards
        market_standards = self._identify_market_standards(feature_frequency, len(competitors))
        
        return {
            "total_feature_categories": len(all_features),
            "common_features": common_features,
            "market_standards": market_standards,
            "feature_coverage": {cat: len(features) for cat, features in all_features.items()}
        }
    
    def _identify_market_standards(self, feature_frequency: Dict, total_competitors: int) -> List[str]:
        """Identify features that are market standards (appear in >50% of products)"""
        
        standards = []
        threshold = total_competitors * 0.5
        
        for category, features in feature_frequency.items():
            for feature, count in features.items():
                if count >= threshold:
                    standards.append(f"{feature} ({category})")
        
        return standards
    
    async def _analyze_market_positioning(self, title: str, description: str, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze market positioning opportunities"""
        
        # Extract our product features
        our_features = self._extract_features_from_text(f"{title} {description}")
        
        # Competitor feature analysis
        competitor_features = {}
        for comp in competitors:
            comp_features = comp.get("features", {})
            for category, features in comp_features.items():
                if category not in competitor_features:
                    competitor_features[category] = set()
                competitor_features[category].update(features)
        
        # Find unique advantages
        unique_advantages = []
        common_weaknesses = []
        
        for category, our_feature_list in our_features.items():
            competitor_feature_set = competitor_features.get(category, set())
            
            for feature in our_feature_list:
                if feature not in competitor_feature_set:
                    unique_advantages.append(f"{feature} ({category})")
        
        # Find common market weaknesses (missing features)
        market_gaps = self._find_positioning_gaps(competitor_features)
        
        return {
            "unique_advantages": unique_advantages,
            "market_gaps": market_gaps,
            "positioning_recommendations": self._generate_positioning_recommendations(unique_advantages, market_gaps)
        }
    
    def _find_positioning_gaps(self, competitor_features: Dict) -> List[str]:
        """Find gaps in competitor feature coverage"""
        
        # Features that should be common but aren't
        expected_features = {
            'certifications': ['ce', 'rohs', 'impermeable'],
            'connectivity': ['bluetooth', 'usb', 'wifi'],
            'materials': ['aluminio', 'acero'],
            'battery': ['recargable', 'duración']
        }
        
        gaps = []
        for category, expected in expected_features.items():
            competitor_set = competitor_features.get(category, set())
            for expected_feature in expected:
                if expected_feature not in competitor_set:
                    gaps.append(f"{expected_feature} ({category})")
        
        return gaps
    
    def _generate_positioning_recommendations(self, advantages: List[str], gaps: List[str]) -> List[str]:
        """Generate market positioning recommendations"""
        
        recommendations = []
        
        if advantages:
            recommendations.append(f"Destacar ventajas únicas: {', '.join(advantages[:3])}")
        
        if gaps:
            recommendations.append(f"Aprovechar vacíos del mercado: {', '.join(gaps[:3])}")
        
        if not advantages and not gaps:
            recommendations.append("Considerar diferenciación en precio o servicio")
        
        recommendations.append("Enfocarse en beneficios que la competencia no comunica claramente")
        
        return recommendations
    
    def _identify_market_gaps(self, competitors: List[Dict], feature_analysis: Dict) -> Dict[str, Any]:
        """Identify market gaps and opportunities"""
        
        gaps = {
            "feature_gaps": [],
            "pricing_gaps": [],
            "positioning_gaps": [],
            "content_gaps": []
        }
        
        # Feature gaps - missing common features
        market_standards = feature_analysis.get("market_standards", [])
        if len(market_standards) < 5:
            gaps["feature_gaps"].append("Mercado carece de estándares claros de características")
        
        # Content gaps - analyze competitor descriptions
        content_quality = self._analyze_competitor_content_quality(competitors)
        if content_quality["average_quality"] < 0.6:
            gaps["content_gaps"].append("Oportunidad de diferenciación con contenido de mayor calidad")
        
        # Pricing gaps
        pricing_analysis = self._analyze_pricing_strategies(competitors)
        if pricing_analysis.get("analysis_possible"):
            segments = pricing_analysis["pricing_segments"]
            if segments.get("mid_range", {}).get("count", 0) < 2:
                gaps["pricing_gaps"].append("Poca competencia en segmento de precio medio")
        
        return gaps
    
    def _analyze_competitor_content_quality(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze quality of competitor content"""
        
        if not competitors:
            return {"average_quality": 0, "analysis": "No hay competidores para analizar"}
        
        quality_scores = []
        
        for comp in competitors:
            title = comp.get("title", "")
            snippet = comp.get("snippet", "")
            
            # Simple quality metrics
            score = 0
            
            # Title length
            if 30 <= len(title) <= 200:
                score += 0.3
            
            # Description length
            if len(snippet) >= 100:
                score += 0.3
            
            # Feature mentions
            if comp.get("features"):
                score += 0.2
            
            # Price information
            if comp.get("extracted_price"):
                score += 0.2
            
            quality_scores.append(score)
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "average_quality": round(avg_quality, 2),
            "competitor_count": len(competitors),
            "quality_distribution": {
                "high_quality": sum(1 for s in quality_scores if s >= 0.8),
                "medium_quality": sum(1 for s in quality_scores if 0.5 <= s < 0.8),
                "low_quality": sum(1 for s in quality_scores if s < 0.5)
            }
        }
    
    async def _generate_competitive_insights(self, title: str, description: str, competitors: List[Dict], feature_analysis: Dict) -> List[str]:
        """Generate actionable competitive insights using AI"""
        
        system_prompt = """Eres un experto en análisis competitivo y marketing para Amazon España.
        Genera insights accionables basados en el análisis de la competencia.
        
        IMPORTANTE: Responde SOLO con un JSON array de strings con insights específicos."""
        
        competitor_summary = {
            "competitor_count": len(competitors),
            "common_features": feature_analysis.get("market_standards", []),
            "our_product": {"title": title, "description": description[:200]}
        }
        
        prompt = f"""
        Basándote en este análisis competitivo, genera 5 insights accionables:
        
        {json.dumps(competitor_summary, indent=2)}
        
        Enfócate en:
        1. Oportunidades de diferenciación
        2. Estrategias de posicionamiento
        3. Mejoras de contenido
        4. Ventajas competitivas
        5. Recomendaciones de marketing
        
        Formato: ["insight 1", "insight 2", "insight 3", "insight 4", "insight 5"]
        """
        
        try:
            result = await self.ollama.generate(
                model=settings.ollama_model,
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            if result["success"]:
                response_text = result["response"].strip()
                
                if "[" in response_text and "]" in response_text:
                    start = response_text.find("[")
                    end = response_text.rfind("]") + 1
                    json_text = response_text[start:end]
                    
                    try:
                        insights = json.loads(json_text)
                        return [insight for insight in insights if isinstance(insight, str) and len(insight.strip()) > 10]
                    except json.JSONDecodeError:
                        pass
            
            # Fallback insights
            return [
                "Diferenciarse con características únicas no presentes en la competencia",
                "Optimizar el precio para el segmento de mercado objetivo",
                "Mejorar la descripción del producto con más detalles técnicos",
                "Destacar beneficios que la competencia no comunica claramente",
                "Aprovechar vacíos en las características estándar del mercado"
            ]
            
        except Exception:
            return [
                "Analizar fortalezas y debilidades vs competencia",
                "Optimizar estrategia de posicionamiento",
                "Mejorar propuesta de valor diferencial"
            ]
    
    def _analyze_brand_landscape(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze brand landscape and positioning"""
        
        # Extract brand mentions from titles
        brands = {}
        for comp in competitors:
            title = comp.get("title", "").lower()
            
            # Common brand indicators
            brand_indicators = ['marca', 'brand', '®', '™', 'original', 'oficial']
            
            for indicator in brand_indicators:
                if indicator in title:
                    # Extract potential brand name (word before/after indicator)
                    words = title.split()
                    for i, word in enumerate(words):
                        if indicator in word:
                            if i > 0:
                                brand_name = words[i-1].capitalize()
                                brands[brand_name] = brands.get(brand_name, 0) + 1
                            if i < len(words) - 1:
                                brand_name = words[i+1].capitalize()
                                brands[brand_name] = brands.get(brand_name, 0) + 1
        
        # Sort brands by frequency
        sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "detected_brands": sorted_brands[:10],
            "brand_diversity": len(brands),
            "market_concentration": {
                "top_brand_share": (sorted_brands[0][1] / len(competitors) * 100) if sorted_brands else 0,
                "top_3_share": (sum(b[1] for b in sorted_brands[:3]) / len(competitors) * 100) if len(sorted_brands) >= 3 else 0
            },
            "brand_strategy_recommendation": self._get_brand_strategy_recommendation(sorted_brands, len(competitors))
        }
    
    def _get_brand_strategy_recommendation(self, sorted_brands: List, total_competitors: int) -> str:
        """Get brand strategy recommendation based on market analysis"""
        
        if not sorted_brands:
            return "Mercado fragmentado - oportunidad para establecer marca fuerte"
        
        top_brand_share = (sorted_brands[0][1] / total_competitors * 100) if sorted_brands else 0
        
        if top_brand_share > 50:
            return "Mercado dominado por una marca - considerar estrategia de nicho"
        elif top_brand_share > 30:
            return "Mercado con líder claro - diferenciarse o competir en precio"
        else:
            return "Mercado fragmentado - oportunidad para posicionamiento de marca"