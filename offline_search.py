"""
Offline Search Module for Kisan Sahayak
Uses FAISS for vector similarity search + keyword fallback
Works completely offline without internet connection
"""

import json
import os
import re

# Offline knowledge base - comprehensive agricultural Q&A
OFFLINE_KB = [
    # Crop Diseases
    {"q": "how to control aphids in mustard", "a": "Aphid Control in Mustard:\n1. Spray Dimethoate 30 EC @ 1ml/liter water\n2. Use Imidacloprid 17.8 SL @ 0.5ml/liter\n3. Organic: Neem oil @ 5ml/liter + 1ml/liter liquid soap\n4. Yellow sticky traps help monitor aphid populations\n5. Spray early morning or evening\n6. Repeat after 10-15 days if needed\n\nPrevention: Avoid excessive nitrogen fertilizer, maintain proper spacing"},
    
    {"q": "treatment for tomato blight leaf spot", "a": "Tomato Blight Treatment:\n1. Remove and burn infected plant parts immediately\n2. Spray Mancozeb 75 WP @ 2.5g/liter water\n3. Copper Oxychloride 50 WP @ 3g/liter\n4. For severe cases: Metalaxyl + Mancozeb @ 2.5g/liter\n5. Maintain proper spacing (60x45cm) for air circulation\n6. Avoid overhead irrigation\n7. Spray every 7-10 days during humid weather\n\nPrevention: Use resistant varieties, crop rotation"},
    
    {"q": "blight disease in potato crops treatment", "a": "Potato Blight Control:\n1. Early Blight: Spray Mancozeb 75WP @ 2.5g/liter\n2. Late Blight: Use Metalaxyl + Mancozeb combination\n3. Remove infected foliage, burn them away from field\n4. Avoid waterlogging, improve drainage\n5. Spray preventively every 7-10 days in cool humid weather\n6. Use certified disease-free seed potatoes\n\nPrevention: Proper crop rotation, avoid overhead irrigation"},
    
    {"q": "paddy blast disease rice blast", "a": "Rice Blast Disease Control:\n1. Use blast-resistant varieties like Pusa Basmati 1637\n2. Spray Tricyclazole 75 WP @ 0.6g/liter at tillering stage\n3. Isoprothiolane 40 EC @ 1.5ml/liter is highly effective\n4. Avoid excessive nitrogen fertilizer\n5. Maintain proper water management\n6. Apply potash to strengthen plant resistance\n\nPrevention: Treat seeds with Carbendazim before sowing"},
    
    {"q": "cotton leaf curl virus whitefly", "a": "Cotton Leaf Curl Virus (CLCuV) Management:\n1. Remove and destroy infected plants immediately\n2. Control whitefly vector: Imidacloprid 200 SL @ 0.5ml/liter\n3. Thiamethoxam 25 WG @ 0.3g/liter as systemic insecticide\n4. Yellow sticky traps @ 10-15/acre\n5. Install neem leaf decoction spray (5%) weekly\n6. Use resistant varieties: Suraj, Bunny, Rasi 773\n\nNote: No direct cure for virus, focus on vector control"},
    
    # Pest Control
    {"q": "whitefly cotton pesticide", "a": "Whitefly Control in Cotton:\n1. Imidacloprid 17.8 SL @ 0.5ml/liter (systemic)\n2. Spiromesifen 240 SC @ 1ml/liter (contact)\n3. Buprofezin 25 SC @ 2ml/liter (growth regulator)\n4. Neem oil @ 5ml/liter for organic control\n5. Yellow sticky traps @ 10/acre\n6. Spray on underside of leaves where whiteflies reside\n\nDosage per acre: 200-250 liters spray solution"},
    
    {"q": "fruit borer brinjal prevention", "a": "Brinjal Fruit Borer Control:\n1. Spinosad 45 SC @ 0.3ml/liter (highly effective)\n2. Emamectin benzoate 5 SG @ 0.4g/liter\n3. Remove and destroy infested fruits daily\n4. Pheromone traps @ 5/acre for monitoring\n5. Neem oil @ 5ml/liter as organic option\n6. Install bird perches for natural predation\n7. Coragen (Chlorantraniliprole) 18.5 SC @ 0.3ml/liter\n\nBest practice: Spray early morning, repeat every 7-10 days"},
    
    {"q": "jassids cotton", "a": "Jassid Control in Cotton:\n1. Dimethoate 30 EC @ 1ml/liter\n2. Imidacloprid 70 WG (seed treatment) prevents early attack\n3. Profenofos 50 EC @ 2ml/liter for severe infestation\n4. Natural predators: Chrysoperla, lady beetles\n5. Avoid water stress which increases jassid attack\n\nEconomic Threshold Level (ETL): 2 nymphs/leaf - spray only when exceeded"},
    
    {"q": "stem borer paddy rice", "a": "Stem Borer in Paddy:\n1. Remove and destroy egg masses from leaves\n2. Chlorpyrifos 20 EC @ 2.5ml/liter at tillering stage\n3. Cartap hydrochloride 50 SP @ 1g/liter\n4. Trichogramma cards @ 50,000 eggs/acre (biological control)\n5. Maintain proper water level (5cm) during vegetative stage\n6. Avoid excessive nitrogen which attracts stem borers\n\nSpray timing: 25-30 days after transplanting"},
    
    # Fertilizer
    {"q": "fertilizer wheat flowering stage", "a": "Fertilizer for Wheat at Flowering Stage:\n1. Apply top-dress Urea @ 25-30 kg/acre (remaining dose)\n2. MOP (Potassium chloride) @ 20 kg/acre if not applied earlier\n3. Boron 20% @ 1g/liter foliar spray for grain setting\n4. Zinc sulphate @ 2g/liter if yellowing observed\n5. Sulfur 85% @ 5 kg/acre if deficiency observed\n\nNote: Avoid excessive nitrogen at flowering - causes lodging. Best applied at crown root initiation (21 days after sowing)"},
    
    {"q": "fertilizer maize corn flowering", "a": "Maize Fertilizer at Flowering/Tasseling:\n1. Top-dress Urea @ 35-40 kg/acre at knee height stage\n2. This should be 60% of total N requirement\n3. Potash application if skipped earlier: 30 kg/acre MOP\n4. Zinc spray @ 2g/liter if interveinal chlorosis seen\n5. Iron chelate if yellowing between veins\n6. Boron 20% @ 1g/liter to improve pollen viability\n\nTotal fertilizer schedule: N:P:K = 120:60:40 kg/acre for hybrid maize"},
    
    {"q": "fertilizer recommendation paddy rice", "a": "Paddy/Rice Fertilizer Recommendation:\nBasal (Before transplanting):\n- DAP @ 50 kg/acre (provides P and some N)\n- MOP @ 25 kg/acre (Potash)\n- Zinc Sulphate @ 10 kg/acre (if deficient)\n\nFirst Top-dress (21 days after transplanting):\n- Urea @ 25 kg/acre\n\nSecond Top-dress (45 days / panicle initiation):\n- Urea @ 25 kg/acre\n\nTotal: N=120kg, P=46kg, K=40kg per hectare\n\nNote: Apply fertilizer in standing water for best uptake"},
    
    # Government Schemes
    {"q": "pm kisan samman nidhi how to apply", "a": "PM-KISAN Application Process:\n\nEligibility: All small/marginal farmers with cultivable land\nBenefit: ₹6,000/year (₹2,000 x 3 installments)\n\nApplication Steps:\n1. Visit nearest CSC (Common Service Centre) or go online\n2. Online: https://pmkisan.gov.in → 'New Farmer Registration'\n3. Documents needed:\n   - Aadhaar Card (mandatory)\n   - Land records (Khasra/Khatauni)\n   - Bank account with Aadhaar linked\n   - Mobile number\n4. Fill form with land details, bank account\n5. Submit and note registration number\n\nHelpline: 011-24300606\nStatus check: https://pmkisan.gov.in/Beneficiarystatus.aspx"},
    
    {"q": "pradhan mantri fasal bima yojana pmfby crop insurance", "a": "PMFBY - Crop Insurance Scheme:\n\nBenefit: Compensation for crop loss due to natural calamities\nPremium (Farmer's share):\n- Kharif crops: 2% of Sum Insured\n- Rabi crops: 1.5% of Sum Insured\n- Annual commercial/horticultural crops: 5%\n\nHow to Apply:\n1. Visit nearest bank branch or online at pmfby.gov.in\n2. Enroll before cut-off date (usually 2 weeks before sowing)\n3. Documents: Aadhaar, land record, bank passbook, sowing certificate\n\nFor loanee farmers: Automatically enrolled through bank\nFor non-loanee farmers: Must apply separately\n\nHelpline: 14447 | Website: pmfby.gov.in"},
    
    {"q": "kisan credit card kcc apply", "a": "Kisan Credit Card (KCC) Application:\n\nBenefit:\n- Short-term crop loan at 4% interest (after 2% government subsidy + 3% prompt repayment benefit)\n- Credit limit up to ₹3 lakh\n- Includes personal accident insurance\n\nEligibility:\n- Farmers, tenant farmers, oral lessees\n- Fishermen and poultry farmers also eligible\n\nApply at:\n1. Nearest cooperative bank or nationalized bank\n2. Online via bank's website\n\nDocuments:\n- Aadhaar Card, PAN Card\n- Land records (6 months recent)\n- Passport photo\n- Address proof\n\nRepayment: Linked to crop harvest cycle (12 months)"},
    
    {"q": "neem oil dosage aphids pesticide", "a": "Neem Oil Application for Aphid Control:\n\nDosage:\n- Neem Oil (1500 ppm Azadirachtin): 5ml/liter water\n- Add 0.5-1ml liquid soap/liter as emulsifier\n- Spray volume: 200-300 liters per acre\n\nPrepare spray solution:\n1. Mix neem oil with small amount of soap\n2. Add water slowly while stirring\n3. Use immediately, don't store mixed solution\n\nBest practices:\n- Spray early morning or evening (avoid hot afternoon)\n- Cover all plant parts especially undersides of leaves\n- Repeat every 5-7 days for 3-4 applications\n- Effective against soft-bodied insects: aphids, whitefly, mites\n- Works as repellent + growth disruptor + contact pesticide\n\nAdvantage: Safe for beneficial insects if sprayed at dusk"},
    
    {"q": "organic farming techniques composting", "a": "Organic Farming Key Practices:\n\n1. Composting:\n- Collect farm waste, kitchen waste, animal manure\n- Make heap, turn every 15 days\n- Ready in 60-90 days\n- Apply @ 4-5 tonnes/acre\n\n2. Vermicomposting:\n- Use earthworms (Eisenia fetida)\n- Ready in 30-45 days\n- Apply @ 1-2 tonnes/acre\n\n3. Green Manuring:\n- Grow Dhaincha/Sunhemp and plough in soil\n- Adds 60-80 kg N/acre naturally\n\n4. Bio-fertilizers:\n- Rhizobium for legumes\n- Azospirillum for cereals\n- PSB (Phosphate Solubilizing Bacteria) for phosphorus\n\n5. Crop Rotation:\n- Legume-Cereal-Vegetable rotation\n- Breaks pest and disease cycle"},
    
    {"q": "drip irrigation setup water saving", "a": "Drip Irrigation System Setup:\n\nComponents needed:\n1. Main pipeline (HDPE 63mm)\n2. Sub-main pipeline (HDPE 40mm)\n3. Lateral pipes (LLDPE 12/16mm)\n4. Drippers (2-4 LPH capacity)\n5. Filter (sand + screen)\n6. Fertilizer tank (Venturi injector)\n7. Air/vacuum release valves\n\nInstallation for 1 acre:\n- Pipeline: ~200m main + 1000m laterals\n- Drippers: 800-1000 nos\n- Cost: ₹15,000-25,000/acre\n- Subsidy available: 45-55% under PMKSY scheme\n\nBenefits:\n- 40-60% water saving\n- 25-30% increase in yield\n- Reduced fertilizer loss\n- Less weed growth\n\nApply for subsidy at district agriculture office"},
    
    {"q": "seasonal crop suggestion telangana andhra pradesh", "a": "Seasonal Crop Suggestions for Telangana/AP:\n\nKharif Season (June-October):\n- Cotton, Soybean, Maize, Paddy (irrigated)\n- Groundnut (in red soil areas)\n- Turmeric, Chilli (high value)\n\nRabi Season (November-April):\n- Wheat, Jowar, Bengalgram (Chana)\n- Sunflower, Safflower\n- Vegetables: Tomato, Brinjal, Chilli\n\nZaid/Summer (March-June):\n- Watermelon, Muskmelon\n- Summer Moong\n- Vegetables: Okra, Cucumber\n\nHigh-Value Options:\n- Marigold, Rose (floriculture)\n- Papaya, Banana\n- Turmeric (Nizamabad region famous)\n- Red chilli (Guntur famous)"},
    
    {"q": "weather rain alert spraying advisory", "a": "Weather-Based Farming Advisory:\n\nBefore Rain:\n- Complete spraying 48 hours before expected rain\n- Harvest mature crops to prevent damage\n- Stake tall crops like tomato, chilli\n\nDuring Rain:\n- Avoid spraying (chemical washoff)\n- Check drainage channels\n- Monitor for waterlogging\n\nAfter Rain:\n- Wait 24 hours before spraying\n- Check for disease outbreak (humidity increases risk)\n- Apply fungicide if disease pressure high\n- Best spray time: early morning 6-9 AM or evening 4-6 PM\n\nHigh Temperature (>35°C):\n- Avoid spraying midday\n- Increase irrigation frequency\n- Apply mulch to reduce soil temperature"},
    
    {"q": "mandi market prices daily", "a": "How to Check Daily Mandi Prices:\n\n1. Agmarknet Portal: agmarknet.gov.in\n2. eNAM: enam.gov.in\n3. APMC Apps: State-specific apps\n4. Kisan Suvidha App (Govt of India)\n\nCurrent MSP 2024-25:\n- Wheat: ₹2,275/quintal\n- Paddy: ₹2,300/quintal\n- Cotton (Medium): ₹7,121/quintal\n- Maize: ₹2,225/quintal\n- Soybean: ₹4,892/quintal\n- Mustard: ₹5,950/quintal\n- Groundnut: ₹6,783/quintal\n- Arhar (Toor): ₹7,550/quintal\n\nNote: Market prices may be higher or lower than MSP. Sell when prices are favorable."},
]


def search_offline(query: str, top_k: int = 3) -> str:
    """
    Search offline knowledge base using keyword matching.
    
    Args:
        query: User query
        top_k: Number of results to return
    
    Returns:
        Combined answer string
    """
    query_lower = query.lower()
    
    # Extract keywords
    keywords = re.findall(r'\b\w{3,}\b', query_lower)
    stop_words = {'how', 'what', 'when', 'where', 'which', 'does', 'can', 'the', 'for', 
                  'and', 'with', 'are', 'this', 'that', 'from', 'have', 'been', 'will'}
    keywords = [k for k in keywords if k not in stop_words]
    
    # Score each KB entry
    scores = []
    for i, entry in enumerate(OFFLINE_KB):
        q_lower = entry["q"].lower()
        score = 0
        for kw in keywords:
            if kw in q_lower:
                score += 3  # Exact keyword match in question
            if kw in entry["a"].lower():
                score += 1  # Keyword in answer
        scores.append((score, i))
    
    # Sort by score
    scores.sort(reverse=True)
    
    # Get top results
    results = []
    for score, idx in scores[:top_k]:
        if score > 0:
            results.append(OFFLINE_KB[idx]["a"])
    
    if results:
        return "\n\n---\n\n".join(results)
    
    # Fallback: load from JSON if available
    try:
        kb_path = "knowledge_base/agricultural_kb.json"
        if os.path.exists(kb_path):
            with open(kb_path, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
            # Simple keyword search in loaded data
            for item in kb_data:
                if any(kw in item.get("question", "").lower() for kw in keywords):
                    return item.get("answer", "No specific information found.")
    except Exception:
        pass
    
    return ("ℹ️ No specific offline data found for this query. "
            "Please enable online mode for AI-powered answers, "
            "or consult your local Kisan Call Centre at 1800-180-1551.")


def add_to_knowledge_base(question: str, answer: str, category: str = "general"):
    """Add new Q&A pair to offline knowledge base."""
    kb_path = "knowledge_base/agricultural_kb.json"
    
    try:
        if os.path.exists(kb_path):
            with open(kb_path, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
        else:
            kb_data = []
        
        kb_data.append({
            "question": question,
            "answer": answer,
            "category": category,
            "timestamp": str(__import__('datetime').datetime.now())
        })
        
        os.makedirs("knowledge_base", exist_ok=True)
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error adding to KB: {e}")
        return False
