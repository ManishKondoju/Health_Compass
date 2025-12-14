# src/utils/document_analyzer_enhanced.py
"""
Enhanced Medical Document Analyzer with Web Scraping
- Uses web scraping for real-time medical data
- Queries existing vector database for medical information
- Falls back to built-in reference ranges
- Scrapes Mayo Clinic, MedlinePlus for detailed test info
"""

import io
import re
import requests
from PIL import Image
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
from bs4 import BeautifulSoup
import time

class EnhancedDocumentAnalyzer:
    """Enhanced analyzer with web scraping capabilities"""
    
    def __init__(self, rag_system=None):
        self.rag = rag_system  # Use existing RAG system for vector DB queries
        self.lab_reference_ranges = self._load_lab_references()
        self.scraping_enabled = True
        self.cache = {}  # Cache scraped data
    
    def _load_lab_references(self) -> Dict:
        """Load built-in reference ranges as fallback"""
        return {
            # Complete Blood Count (CBC)
            'hemoglobin': {
                'name': 'Hemoglobin',
                'male': (13.5, 17.5, 'g/dL'),
                'female': (12.0, 15.5, 'g/dL'),
                'description': 'Protein in red blood cells that carries oxygen',
                'high': 'May indicate dehydration, lung disease, or living at high altitude',
                'low': 'May indicate anemia, blood loss, or nutritional deficiency',
                'medlineplus_id': '003645'
            },
            'hematocrit': {
                'name': 'Hematocrit',
                'male': (38.8, 50.0, '%'),
                'female': (34.9, 44.5, '%'),
                'description': 'Percentage of blood volume made up of red blood cells',
                'high': 'May indicate dehydration or polycythemia',
                'low': 'May indicate anemia or blood loss',
                'medlineplus_id': '003646'
            },
            'wbc': {
                'name': 'White Blood Cell Count',
                'normal': (4.5, 11.0, 'K/µL'),
                'description': 'Cells that fight infection',
                'high': 'May indicate infection, inflammation, or stress',
                'low': 'May indicate bone marrow problem or immune deficiency',
                'medlineplus_id': '003643'
            },
            'platelets': {
                'name': 'Platelet Count',
                'normal': (150, 400, 'K/µL'),
                'description': 'Cell fragments that help blood clot',
                'high': 'May indicate inflammation, infection, or blood disorder',
                'low': 'May indicate bleeding risk or autoimmune condition',
                'medlineplus_id': '003647'
            },
            'glucose': {
                'name': 'Blood Glucose (Fasting)',
                'normal': (70, 100, 'mg/dL'),
                'prediabetes': (100, 125, 'mg/dL'),
                'diabetes': (126, float('inf'), 'mg/dL'),
                'description': 'Sugar level in blood',
                'high': 'May indicate diabetes or prediabetes',
                'low': 'May indicate hypoglycemia',
                'medlineplus_id': '003482'
            },
            'cholesterol': {
                'name': 'Total Cholesterol',
                'desirable': (0, 200, 'mg/dL'),
                'borderline': (200, 239, 'mg/dL'),
                'high': (240, float('inf'), 'mg/dL'),
                'description': 'Waxy substance in blood',
                'high': 'May increase risk of heart disease',
                'low': 'Usually good',
                'medlineplus_id': '003491'
            },
            'ldl': {
                'name': 'LDL Cholesterol (Bad)',
                'optimal': (0, 100, 'mg/dL'),
                'near_optimal': (100, 129, 'mg/dL'),
                'borderline': (130, 159, 'mg/dL'),
                'high': (160, float('inf'), 'mg/dL'),
                'description': 'Low-density lipoprotein - "bad" cholesterol',
                'high': 'Increases heart disease risk',
                'low': 'Generally better',
                'medlineplus_id': '003495'
            },
            'hdl': {
                'name': 'HDL Cholesterol (Good)',
                'low': (0, 40, 'mg/dL'),
                'normal': (40, 60, 'mg/dL'),
                'high': (60, float('inf'), 'mg/dL'),
                'description': 'High-density lipoprotein - "good" cholesterol',
                'high': 'Protective against heart disease',
                'low': 'May increase heart disease risk',
                'medlineplus_id': '003493'
            },
            'triglycerides': {
                'name': 'Triglycerides',
                'normal': (0, 150, 'mg/dL'),
                'borderline': (150, 199, 'mg/dL'),
                'high': (200, 499, 'mg/dL'),
                'very_high': (500, float('inf'), 'mg/dL'),
                'description': 'Type of fat in blood',
                'high': 'May increase risk of heart disease and pancreatitis',
                'low': 'Usually not a concern',
                'medlineplus_id': '003493'
            },
            'tsh': {
                'name': 'Thyroid Stimulating Hormone (TSH)',
                'normal': (0.4, 4.0, 'mIU/L'),
                'description': 'Hormone that regulates thyroid function',
                'high': 'May indicate underactive thyroid (hypothyroidism)',
                'low': 'May indicate overactive thyroid (hyperthyroidism)',
                'medlineplus_id': '003684'
            },
            'alt': {
                'name': 'ALT (Alanine Aminotransferase)',
                'normal': (7, 56, 'U/L'),
                'description': 'Liver enzyme',
                'high': 'May indicate liver damage or inflammation',
                'low': 'Usually not concerning',
                'medlineplus_id': '003473'
            },
            'creatinine': {
                'name': 'Creatinine',
                'male': (0.7, 1.3, 'mg/dL'),
                'female': (0.6, 1.1, 'mg/dL'),
                'description': 'Waste product filtered by kidneys',
                'high': 'May indicate kidney problems',
                'low': 'Usually not concerning',
                'medlineplus_id': '003475'
            }
        }
    
    def scrape_medlineplus_test_info(self, test_id: str) -> Optional[Dict]:
        """Scrape detailed test information from MedlinePlus"""
        if test_id in self.cache:
            return self.cache[test_id]
        
        try:
            url = f"https://medlineplus.gov/lab-tests/{test_id}.htm"
            response = requests.get(url, timeout=5, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; HealthCompass/1.0)'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract key information
                info = {
                    'url': url,
                    'description': '',
                    'why_needed': '',
                    'what_results_mean': '',
                    'scraped': True
                }
                
                # Try to extract description
                desc_section = soup.find('div', {'id': 'topic-summary'})
                if desc_section:
                    info['description'] = desc_section.get_text().strip()
                
                # Cache the result
                self.cache[test_id] = info
                return info
            
            return None
        except Exception as e:
            print(f"Scraping failed: {e}")
            return None
    
    def scrape_mayo_clinic_reference(self, test_name: str) -> Optional[Dict]:
        """Scrape Mayo Clinic for reference ranges"""
        try:
            # Mayo Clinic test catalog search
            search_url = "https://www.mayocliniclabs.com/test-catalog/search"
            params = {'q': test_name}
            
            response = requests.get(search_url, params=params, timeout=5, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; HealthCompass/1.0)'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract reference range if found
                # This is simplified - real implementation would parse specific elements
                reference_section = soup.find('div', class_='reference-values')
                if reference_section:
                    return {
                        'source': 'Mayo Clinic',
                        'reference_range': reference_section.get_text().strip(),
                        'scraped': True
                    }
            
            return None
        except:
            return None
    
    def query_vector_db_for_test(self, test_name: str) -> Optional[str]:
        """Query existing vector database for test information"""
        if not self.rag:
            return None
        
        try:
            # Query the vector DB
            query = f"What is {test_name}? What does it measure? What are normal ranges?"
            result = self.rag.query(query, n_results=2)
            
            if result and result.get('answer'):
                return result['answer']
            
            return None
        except:
            return None
    
    def get_enhanced_test_info(self, test_name: str, test_key: str) -> Dict:
        """Get comprehensive test information using multiple sources"""
        
        # Start with built-in data
        builtin_info = self.lab_reference_ranges.get(test_key, {})
        
        enhanced_info = {
            'name': builtin_info.get('name', test_name),
            'description': builtin_info.get('description', ''),
            'sources': ['Built-in Reference'],
            'additional_info': []
        }
        
        # Try web scraping if enabled
        if self.scraping_enabled:
            
            # 1. Try MedlinePlus
            medlineplus_id = builtin_info.get('medlineplus_id')
            if medlineplus_id:
                medlineplus_info = self.scrape_medlineplus_test_info(medlineplus_id)
                if medlineplus_info:
                    enhanced_info['additional_info'].append({
                        'source': 'MedlinePlus',
                        'description': medlineplus_info.get('description', '')[:500]
                    })
                    enhanced_info['sources'].append('MedlinePlus')
            
            # 2. Try Mayo Clinic
            mayo_info = self.scrape_mayo_clinic_reference(test_name)
            if mayo_info:
                enhanced_info['additional_info'].append({
                    'source': 'Mayo Clinic',
                    'info': mayo_info.get('reference_range', '')
                })
                enhanced_info['sources'].append('Mayo Clinic')
            
            # Small delay to be respectful to servers
            time.sleep(0.5)
        
        # 3. Query existing vector database
        if self.rag:
            vector_info = self.query_vector_db_for_test(test_name)
            if vector_info:
                enhanced_info['additional_info'].append({
                    'source': 'Health Compass Database',
                    'info': vector_info[:500]
                })
                enhanced_info['sources'].append('Vector Database')
        
        return enhanced_info
    
    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            pdf_file = io.BytesIO(file_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"
    
    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except ImportError:
            return "ERROR: pytesseract not installed. Install with: pip install pytesseract"
        except Exception as e:
            return f"Error extracting image text: {str(e)}"
    
    def extract_lab_values(self, text: str) -> List[Dict]:
        """Extract lab values and test names from document text"""
        results = []
        
        # Common patterns for lab results
        patterns = [
            r'([A-Za-z\s\(\)]+)[\s:]+(\d+\.?\d*)\s*([a-zA-Z/%µ]+)',
            r'([A-Za-z\s]+)\s+(\d+\.?\d*)\s+([a-zA-Z/%µ]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                test_name = match.group(1).strip()
                value = float(match.group(2))
                unit = match.group(3).strip()
                
                results.append({
                    'test': test_name,
                    'value': value,
                    'unit': unit
                })
        
        return results
    
    def analyze_lab_value(self, test_name: str, value: float, unit: str, 
                         gender: Optional[str] = None) -> Dict:
        """Analyze a single lab value with enhanced information"""
        
        # Normalize test name
        test_key = test_name.lower().replace(' ', '').replace('(', '').replace(')', '')
        
        # Try to find matching reference
        ref = None
        matched_key = None
        for key, data in self.lab_reference_ranges.items():
            if key in test_key or test_key in key:
                ref = data
                matched_key = key
                break
        
        if not ref:
            return {
                'test': test_name,
                'value': value,
                'unit': unit,
                'status': 'unknown',
                'message': f"No reference range available for {test_name}",
                'sources': ['Built-in']
            }
        
        # Get enhanced information
        enhanced_info = self.get_enhanced_test_info(test_name, matched_key)
        
        # Determine if value is normal, high, or low
        status = 'normal'
        message = f"{ref['name']}: {value} {unit}"
        details = ref['description']
        
        # Check gender-specific ranges
        if gender and gender.lower() in ['male', 'female']:
            if gender.lower() in ref:
                low, high, ref_unit = ref[gender.lower()]
                if value < low:
                    status = 'low'
                    message = f"⚠️ LOW: {ref['name']} is {value} {unit} (normal: {low}-{high} {ref_unit})"
                    details = ref['low']
                elif value > high:
                    status = 'high'
                    message = f"⚠️ HIGH: {ref['name']} is {value} {unit} (normal: {low}-{high} {ref_unit})"
                    details = ref['high']
                else:
                    message = f"✅ NORMAL: {ref['name']} is {value} {unit} (normal: {low}-{high} {ref_unit})"
        
        # Check general normal ranges
        elif 'normal' in ref:
            low, high, ref_unit = ref['normal']
            if value < low:
                status = 'low'
                message = f"⚠️ LOW: {ref['name']} is {value} {unit} (normal: {low}-{high} {ref_unit})"
                details = ref.get('low', 'Below normal range')
            elif value > high:
                status = 'high'
                message = f"⚠️ HIGH: {ref['name']} is {value} {unit} (normal: {low}-{high} {ref_unit})"
                details = ref.get('high', 'Above normal range')
            else:
                message = f"✅ NORMAL: {ref['name']} is {value} {unit} (normal: {low}-{high} {ref_unit})"
        
        return {
            'test': ref['name'],
            'value': value,
            'unit': unit,
            'status': status,
            'message': message,
            'details': details,
            'description': enhanced_info['description'],
            'sources': enhanced_info['sources'],
            'additional_info': enhanced_info.get('additional_info', [])
        }
    
    def generate_plain_english_report(self, lab_results: List[Dict], 
                                     document_type: str = "Lab Report") -> str:
        """Generate a plain English report from lab results"""
        
        report = f"""# {document_type} Analysis

## Summary
I've analyzed your {document_type.lower()} and found {len(lab_results)} test results.

"""
        
        # Show data sources used
        all_sources = set()
        for result in lab_results:
            all_sources.update(result.get('sources', []))
        
        if len(all_sources) > 1:
            report += f"**Data Sources Used:** {', '.join(all_sources)}\n\n"
        
        # Categorize results
        normal = [r for r in lab_results if r['status'] == 'normal']
        abnormal = [r for r in lab_results if r['status'] in ['high', 'low']]
        unknown = [r for r in lab_results if r['status'] == 'unknown']
        
        if abnormal:
            report += "## ⚠️ Results Needing Attention\n\n"
            for result in abnormal:
                report += f"### {result['test']}\n"
                report += f"**Your Value:** {result['value']} {result['unit']}\n"
                report += f"**Status:** {result['status'].upper()}\n\n"
                report += f"**What this means:** {result['details']}\n\n"
                report += f"**About this test:** {result['description']}\n\n"
                
                # Add additional scraped information
                if result.get('additional_info'):
                    report += "**Additional Information:**\n"
                    for info in result['additional_info'][:2]:  # Limit to 2 sources
                        report += f"- *Source: {info['source']}*\n"
                        content = info.get('description') or info.get('info', '')
                        if content:
                            report += f"  {content[:200]}...\n\n"
                
                report += "---\n\n"
        
        if normal:
            report += f"## ✅ Normal Results ({len(normal)})\n\n"
            for result in normal:
                report += f"- **{result['test']}:** {result['value']} {result['unit']} (Normal)\n"
            report += "\n"
        
        if unknown:
            report += "## ❓ Other Tests Found\n\n"
            for result in unknown:
                report += f"- {result['test']}: {result['value']} {result['unit']}\n"
            report += "\n"
        
        report += """## 📋 What To Do Next

"""
        
        if abnormal:
            report += """### Talk to Your Doctor About:
1. What these abnormal values mean for your specific situation
2. Whether any treatment or lifestyle changes are needed
3. If follow-up testing is recommended
4. Any medications that might affect these values

"""
        
        report += """### Questions to Ask:
- What caused these results?
- Do I need any treatment?
- Should I make any lifestyle changes?
- When should I retest?
- Are there any immediate concerns?

## ⚠️ Important Reminder
This analysis uses multiple trusted medical sources but is for educational purposes only. Always discuss your results with your healthcare provider who knows your complete medical history.
"""
        
        return report
    
    def analyze_document(self, file_bytes: bytes, file_type: str, 
                        gender: Optional[str] = None) -> Dict:
        """Main analysis function with web scraping enhancement"""
        
        # Extract text based on file type
        if file_type == 'application/pdf':
            text = self.extract_text_from_pdf(file_bytes)
        elif file_type.startswith('image/'):
            text = self.extract_text_from_image(file_bytes)
        elif file_type == 'text/plain':
            text = file_bytes.decode('utf-8')
        else:
            return {'error': f'Unsupported file type: {file_type}'}
        
        # Extract lab values
        lab_values = self.extract_lab_values(text)
        
        # Analyze each value (with web scraping)
        analyzed_results = []
        for lab in lab_values:
            analysis = self.analyze_lab_value(
                lab['test'], 
                lab['value'], 
                lab['unit'],
                gender
            )
            analyzed_results.append(analysis)
        
        # Generate report
        report = self.generate_plain_english_report(analyzed_results)
        
        return {
            'extracted_text': text,
            'lab_results': analyzed_results,
            'report': report,
            'abnormal_count': len([r for r in analyzed_results if r['status'] != 'normal']),
            'total_tests': len(analyzed_results),
            'web_scraping_used': self.scraping_enabled
        }


# Usage in app.py - replace DocumentAnalyzer with this
if __name__ == "__main__":
    # Test with sample
    analyzer = EnhancedDocumentAnalyzer()
    
    sample_text = """
    COMPLETE BLOOD COUNT
    Hemoglobin: 10.5 g/dL
    WBC: 12.2 K/µL
    Glucose: 145 mg/dL
    LDL Cholesterol: 175 mg/dL
    """
    
    result = analyzer.analyze_document(
        sample_text.encode('utf-8'),
        'text/plain',
        gender='male'
    )
    
    print(result['report'])