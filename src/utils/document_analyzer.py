# src/utils/document_analyzer.py
"""
Enhanced Medical Document Analyzer
- Extracts text from PDFs, images, and text files
- Scrapes medical reference data
- Analyzes lab reports with normal ranges
- Explains in plain English
"""

import io
import re
import requests
from PIL import Image
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

class DocumentAnalyzer:
    """Analyzes medical documents and provides plain English explanations"""
    
    def __init__(self):
        self.lab_reference_ranges = self._load_lab_references()
    
    def _load_lab_references(self) -> Dict:
        """Load common lab test reference ranges"""
        return {
            # Complete Blood Count (CBC)
            'hemoglobin': {
                'name': 'Hemoglobin',
                'male': (13.5, 17.5, 'g/dL'),
                'female': (12.0, 15.5, 'g/dL'),
                'description': 'Protein in red blood cells that carries oxygen',
                'high': 'May indicate dehydration, lung disease, or living at high altitude',
                'low': 'May indicate anemia, blood loss, or nutritional deficiency'
            },
            'hematocrit': {
                'name': 'Hematocrit',
                'male': (38.8, 50.0, '%'),
                'female': (34.9, 44.5, '%'),
                'description': 'Percentage of blood volume made up of red blood cells',
                'high': 'May indicate dehydration or polycythemia',
                'low': 'May indicate anemia or blood loss'
            },
            'wbc': {
                'name': 'White Blood Cell Count',
                'normal': (4.5, 11.0, 'K/µL'),
                'description': 'Cells that fight infection',
                'high': 'May indicate infection, inflammation, or stress',
                'low': 'May indicate bone marrow problem or immune deficiency'
            },
            'platelets': {
                'name': 'Platelet Count',
                'normal': (150, 400, 'K/µL'),
                'description': 'Cell fragments that help blood clot',
                'high': 'May indicate inflammation, infection, or blood disorder',
                'low': 'May indicate bleeding risk or autoimmune condition'
            },
            
            # Comprehensive Metabolic Panel (CMP)
            'glucose': {
                'name': 'Blood Glucose (Fasting)',
                'normal': (70, 100, 'mg/dL'),
                'prediabetes': (100, 125, 'mg/dL'),
                'diabetes': (126, float('inf'), 'mg/dL'),
                'description': 'Sugar level in blood',
                'high': 'May indicate diabetes or prediabetes',
                'low': 'May indicate hypoglycemia'
            },
            'creatinine': {
                'name': 'Creatinine',
                'male': (0.7, 1.3, 'mg/dL'),
                'female': (0.6, 1.1, 'mg/dL'),
                'description': 'Waste product filtered by kidneys',
                'high': 'May indicate kidney problems',
                'low': 'Usually not concerning'
            },
            'bun': {
                'name': 'Blood Urea Nitrogen (BUN)',
                'normal': (7, 20, 'mg/dL'),
                'description': 'Waste product from protein breakdown',
                'high': 'May indicate kidney problems or dehydration',
                'low': 'May indicate liver disease or malnutrition'
            },
            'sodium': {
                'name': 'Sodium',
                'normal': (136, 145, 'mEq/L'),
                'description': 'Electrolyte that helps regulate water balance',
                'high': 'May indicate dehydration',
                'low': 'May indicate overhydration or certain medications'
            },
            'potassium': {
                'name': 'Potassium',
                'normal': (3.5, 5.0, 'mEq/L'),
                'description': 'Electrolyte important for heart and muscle function',
                'high': 'Can be dangerous - may affect heart rhythm',
                'low': 'May cause muscle weakness and heart problems'
            },
            
            # Lipid Panel
            'cholesterol': {
                'name': 'Total Cholesterol',
                'desirable': (0, 200, 'mg/dL'),
                'borderline': (200, 239, 'mg/dL'),
                'high': (240, float('inf'), 'mg/dL'),
                'description': 'Waxy substance in blood',
                'high': 'May increase risk of heart disease',
                'low': 'Usually good'
            },
            'ldl': {
                'name': 'LDL Cholesterol (Bad)',
                'optimal': (0, 100, 'mg/dL'),
                'near_optimal': (100, 129, 'mg/dL'),
                'borderline': (130, 159, 'mg/dL'),
                'high': (160, float('inf'), 'mg/dL'),
                'description': 'Low-density lipoprotein - "bad" cholesterol',
                'high': 'Increases heart disease risk',
                'low': 'Generally better'
            },
            'hdl': {
                'name': 'HDL Cholesterol (Good)',
                'low': (0, 40, 'mg/dL'),
                'normal': (40, 60, 'mg/dL'),
                'high': (60, float('inf'), 'mg/dL'),
                'description': 'High-density lipoprotein - "good" cholesterol',
                'high': 'Protective against heart disease',
                'low': 'May increase heart disease risk'
            },
            'triglycerides': {
                'name': 'Triglycerides',
                'normal': (0, 150, 'mg/dL'),
                'borderline': (150, 199, 'mg/dL'),
                'high': (200, 499, 'mg/dL'),
                'very_high': (500, float('inf'), 'mg/dL'),
                'description': 'Type of fat in blood',
                'high': 'May increase risk of heart disease and pancreatitis',
                'low': 'Usually not a concern'
            },
            
            # Thyroid
            'tsh': {
                'name': 'Thyroid Stimulating Hormone (TSH)',
                'normal': (0.4, 4.0, 'mIU/L'),
                'description': 'Hormone that regulates thyroid function',
                'high': 'May indicate underactive thyroid (hypothyroidism)',
                'low': 'May indicate overactive thyroid (hyperthyroidism)'
            },
            
            # Liver Function
            'alt': {
                'name': 'ALT (Alanine Aminotransferase)',
                'normal': (7, 56, 'U/L'),
                'description': 'Liver enzyme',
                'high': 'May indicate liver damage or inflammation',
                'low': 'Usually not concerning'
            },
            'ast': {
                'name': 'AST (Aspartate Aminotransferase)',
                'normal': (10, 40, 'U/L'),
                'description': 'Liver enzyme',
                'high': 'May indicate liver or heart damage',
                'low': 'Usually not concerning'
            }
        }
    
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
            return "ERROR: pytesseract not installed. Install with: pip install pytesseract\nAlso install Tesseract: brew install tesseract (Mac) or apt-get install tesseract-ocr (Linux)"
        except Exception as e:
            return f"Error extracting image text: {str(e)}"
    
    def extract_lab_values(self, text: str) -> List[Dict]:
        """Extract lab values and test names from document text"""
        results = []
        
        # Common patterns for lab results
        # Format: "Test Name: 12.5 mg/dL" or "Hemoglobin 14.2 g/dL"
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
        """Analyze a single lab value against reference ranges"""
        
        # Normalize test name
        test_key = test_name.lower().replace(' ', '').replace('(', '').replace(')', '')
        
        # Try to find matching reference
        ref = None
        for key, data in self.lab_reference_ranges.items():
            if key in test_key or test_key in key:
                ref = data
                break
        
        if not ref:
            return {
                'test': test_name,
                'value': value,
                'unit': unit,
                'status': 'unknown',
                'message': f"No reference range available for {test_name}"
            }
        
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
            'description': ref['description']
        }
    
    def scrape_medical_reference(self, condition: str) -> Optional[str]:
        """Scrape medical reference information from MedlinePlus"""
        try:
            # Search MedlinePlus
            search_url = f"https://medlineplus.gov/ency/article/{condition}.htm"
            response = requests.get(search_url, timeout=5)
            
            if response.status_code == 200:
                # Simple text extraction (would use BeautifulSoup in production)
                text = response.text
                # Extract relevant information
                return f"Found reference information (Status: {response.status_code})"
            else:
                return None
        except:
            return None
    
    def generate_plain_english_report(self, lab_results: List[Dict], 
                                     document_type: str = "Lab Report") -> str:
        """Generate a plain English report from lab results"""
        
        report = f"""# {document_type} Analysis

## Summary
I've analyzed your {document_type.lower()} and found {len(lab_results)} test results.

"""
        
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
This is an educational analysis only. Always discuss your results with your healthcare provider who knows your complete medical history.
"""
        
        return report
    
    def analyze_document(self, file_bytes: bytes, file_type: str, 
                        gender: Optional[str] = None) -> Dict:
        """Main analysis function - processes document and returns analysis"""
        
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
        
        # Analyze each value
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
            'total_tests': len(analyzed_results)
        }


# Example usage
if __name__ == "__main__":
    analyzer = DocumentAnalyzer()
    
    # Test with sample lab report text
    sample_text = """
    COMPLETE BLOOD COUNT
    Date: 12/13/2024
    
    Hemoglobin: 13.2 g/dL
    Hematocrit: 39.5 %
    WBC: 7.2 K/µL
    Platelets: 220 K/µL
    
    METABOLIC PANEL
    Glucose (Fasting): 95 mg/dL
    Creatinine: 1.0 mg/dL
    Sodium: 140 mEq/L
    Potassium: 4.2 mEq/L
    
    LIPID PANEL
    Total Cholesterol: 195 mg/dL
    LDL Cholesterol: 115 mg/dL
    HDL Cholesterol: 55 mg/dL
    Triglycerides: 130 mg/dL
    """
    
    # Simulate document analysis
    results = analyzer.analyze_document(
        sample_text.encode('utf-8'),
        'text/plain',
        gender='male'
    )
    
    print(results['report'])