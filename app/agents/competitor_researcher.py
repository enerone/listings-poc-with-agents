import json
import asyncio
from typing import Dict, Any, List
from app.services.web_search import WebSearchService

class CompetitorResearcher:
    def __init__(self):
        self.web_search = WebSearchService()
    
    async def research_competitors(self, title: str, description: str) -> Dict[str, Any]:
        """Research competitors for the given product"""
        
        try:
            # Extract key product terms for search
            product_keywords = self._extract_keywords(title, description)
            
            # Perform competitor searches
            search_results = await self._search_competitors(product_keywords)
            
            # Analyze competitor data
            analysis = await self._analyze_competitor_data(search_results)
            
            return {
                "success": True,
                "data": {
                    "keywords_used": product_keywords,
                    "competitors_found": len(search_results),
                    "pricing_insights": analysis.get("pricing", {}),
                    "common_features": analysis.get("features", []),
                    "title_patterns": analysis.get("titles", []),
                    "selling_points": analysis.get("selling_points", []),
                    "market_gaps": analysis.get("gaps", []),
                    "recommendations": analysis.get("recommendations", [])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error in competitor research: {str(e)}",
                "data": None
            }
    
    def _extract_keywords(self, title: str, description: str) -> List[str]:
        """Extract main product keywords for search"""
        
        # Common product categories and terms
        product_terms = []
        text = f"{title} {description}".lower()
        
        # Basic product extraction (this could be enhanced with NLP)
        common_products = [
            "mochila", "auriculares", "smartphone", "laptop", "tablet", 
            "smartwatch", "cámara", "televisor", "mouse", "teclado",
            "altavoz", "cargador", "cable", "funda", "protector",
            "zapatos", "ropa", "camisa", "pantalón", "vestido",
            "libro", "juguete", "herramienta", "cocina", "hogar"
        ]
        
        # Find product category
        for product in common_products:
            if product in text:
                product_terms.append(product)
        
        # Add brand names if found
        common_brands = [
            "apple", "samsung", "sony", "nike", "adidas", "lg", "hp",
            "dell", "lenovo", "xiaomi", "huawei", "bose", "jbl"
        ]
        
        for brand in common_brands:
            if brand in text:
                product_terms.append(brand)
        
        # If no specific terms found, use first words from title
        if not product_terms:
            title_words = title.split()[:3]  # First 3 words
            product_terms.extend([word.lower() for word in title_words if len(word) > 3])
        
        return product_terms[:5]  # Limit to 5 terms
    
    async def _search_competitors(self, keywords: List[str]) -> List[Dict]:
        """Search for competitor products"""
        
        search_results = []
        
        for keyword in keywords:
            # Search Amazon specifically
            amazon_query = f"{keyword} Amazon precio características"
            amazon_results = await self.web_search.search(amazon_query, max_results=3)
            
            # Search general e-commerce
            ecommerce_query = f"{keyword} venta online precio reviews"
            ecommerce_results = await self.web_search.search(ecommerce_query, max_results=2)
            
            search_results.extend(amazon_results)
            search_results.extend(ecommerce_results)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        return search_results
    
    async def _analyze_competitor_data(self, search_results: List[Dict]) -> Dict[str, Any]:
        """Analyze competitor data to extract insights"""
        
        analysis = {
            "titles": [],
            "features": [],
            "selling_points": [],
            "pricing": {"ranges": [], "patterns": []},
            "gaps": [],
            "recommendations": []
        }
        
        # Analyze titles and descriptions
        for result in search_results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            
            if title:
                analysis["titles"].append(title)
            
            # Extract features mentioned
            text = f"{title} {snippet}".lower()
            
            # Common feature keywords
            feature_indicators = [
                "bluetooth", "inalámbrico", "resistente", "impermeable",
                "batería", "carga", "rápida", "HD", "4K", "premium",
                "ergonómico", "ligero", "compacto", "portátil",
                "garantía", "certificado", "original", "genuino"
            ]
            
            found_features = [feat for feat in feature_indicators if feat in text]
            analysis["features"].extend(found_features)
        
        # Remove duplicates and get most common
        analysis["features"] = list(set(analysis["features"]))[:10]
        
        # Generate recommendations based on analysis
        if analysis["features"]:
            analysis["recommendations"].append(
                f"Incluir características populares: {', '.join(analysis['features'][:5])}"
            )
        
        if len(analysis["titles"]) > 0:
            analysis["recommendations"].append(
                "Analizar patrones de títulos de competidores para optimización SEO"
            )
        
        # Identify potential gaps
        common_gaps = [
            "Falta información de garantía",
            "No menciona certificaciones",
            "Podría destacar más la relación calidad-precio",
            "Falta información de compatibilidad",
            "No incluye casos de uso específicos"
        ]
        analysis["gaps"] = common_gaps[:3]
        
        return analysis