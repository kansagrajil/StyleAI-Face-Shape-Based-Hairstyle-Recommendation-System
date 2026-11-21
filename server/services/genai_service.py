"""
Generative AI Service.
Wraps the Google Gemini API (or OpenAI as fallback) to generate:
    1. Personalized text-based hairstyle advice
    2. Virtual try-on images (via multimodal AI)
"""

import json
import base64


class GenAIService:
    """Google Gemini API wrapper for text advice and image generation."""

    def __init__(self, api_key):
        """
        Initialize the Generative AI client.
        
        Args:
            api_key: Google Gemini API key.
        """
        self.api_key = api_key
        self.model = None

        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                print("[GenAIService] Initialized with Gemini 2.0 Flash")
            except Exception as e:
                print(f"[GenAIService] Failed to initialize Gemini: {e}")

    def is_available(self):
        """Check if the GenAI service is properly configured."""
        return self.model is not None

    def generate_advice(self, face_shape, gender='unisex', hair_type='straight',
                        preferences=None):
        """
        Generate personalized hairstyle advice using Gemini.
        
        Args:
            face_shape: Detected face shape (e.g., 'oval').
            gender: User's gender.
            hair_type: User's hair type.
            preferences: Optional dict of style preferences.
        
        Returns:
            dict: {
                'explanation': str,
                'recommendations': [{'name': str, 'reason': str}, ...],
                'styles_to_avoid': [{'name': str, 'reason': str}, ...],
                'styling_tips': [str, ...]
            }
            or a fallback dict if AI is unavailable.
        """
        if not self.is_available():
            return self._fallback_advice(face_shape)

        pref_text = json.dumps(preferences) if preferences else 'No specific preferences'

        prompt = """You are an expert hairstylist and beauty consultant.

Client profile:
- Face shape: {face_shape}
- Gender: {gender}
- Hair type: {hair_type}
- Style preferences: {pref_text}

Provide hairstyle advice in the following JSON format (return ONLY valid JSON, no markdown):
{{
    "explanation": "2-3 sentence explanation of why certain styles suit this face shape",
    "recommendations": [
        {{"name": "Hairstyle Name", "reason": "Why it works for this face shape"}},
        {{"name": "Another Style", "reason": "Why it works"}}
    ],
    "styles_to_avoid": [
        {{"name": "Style Name", "reason": "Why to avoid it"}}
    ],
    "styling_tips": [
        "Tip 1 for daily styling",
        "Tip 2 for maintenance"
    ]
}}

Provide exactly 3 recommendations, 2 styles to avoid, and 3 styling tips.
Keep the tone friendly, professional, and encouraging."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Strip markdown code fences if present
            if text.startswith('```'):
                text = text.split('\n', 1)[1]
                if text.endswith('```'):
                    text = text[:-3]

            return json.loads(text)
        except (json.JSONDecodeError, Exception) as e:
            print(f"[GenAIService] Advice generation error: {e}")
            return self._fallback_advice(face_shape)

    def generate_tryon_description(self, face_shape, hairstyle_name,
                                   hairstyle_description):
        """
        Generate a detailed description for virtual try-on visualization.
        
        Args:
            face_shape: The user's face shape.
            hairstyle_name: Name of the hairstyle to try on.
            hairstyle_description: Description of the hairstyle.
        
        Returns:
            str: Detailed visualization description.
        """
        if not self.is_available():
            return f"Visualize {hairstyle_name}: {hairstyle_description}"

        prompt = f"""Describe how the hairstyle "{hairstyle_name}" would look on a person 
with a {face_shape} face shape. The hairstyle is described as: {hairstyle_description}.

Provide a vivid, encouraging 2-3 sentence description of how this would look, 
mentioning specific facial features it would complement. Keep it professional and positive."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[GenAIService] Try-on description error: {e}")
            return f"Visualize {hairstyle_name}: {hairstyle_description}"

    def _fallback_advice(self, face_shape):
        """
        Provide static fallback advice when the AI service is unavailable.
        
        Args:
            face_shape: Detected face shape.
        
        Returns:
            dict: Static advice for the given face shape.
        """
        advice_db = {
            'oval': {
                'explanation': 'The oval face shape is considered the most versatile and balanced. '
                               'Your face length is about 1.5 times the width, with a gently '
                               'rounded jawline. Most hairstyles complement this shape beautifully.',
                'recommendations': [
                    {'name': 'Long Layered Waves', 'reason': 'Enhances your balanced proportions with soft movement'},
                    {'name': 'Bob with Side Part', 'reason': 'Highlights your symmetrical features'},
                    {'name': 'Textured Pixie', 'reason': 'Shows off your well-proportioned face shape'}
                ],
                'styles_to_avoid': [
                    {'name': 'Heavy Bangs', 'reason': 'Can make the face appear shorter than it is'},
                    {'name': 'Overly Voluminous Top', 'reason': 'May elongate the face too much'}
                ],
                'styling_tips': [
                    'Experiment freely — oval faces suit nearly every style',
                    'Keep layers around the cheekbones for a flattering frame',
                    'Try pulling hair back to show off your balanced features'
                ]
            },
            'round': {
                'explanation': 'Round faces have soft curves with similar width and length. '
                               'The key is to create the illusion of length and angles to '
                               'balance the natural softness of your features.',
                'recommendations': [
                    {'name': 'Long Layers', 'reason': 'Adds vertical lines to elongate the face'},
                    {'name': 'Side-Swept Bangs', 'reason': 'Creates asymmetry and angles'},
                    {'name': 'Lob with Face Framing', 'reason': 'Lengthens while keeping fullness'}
                ],
                'styles_to_avoid': [
                    {'name': 'Chin-Length Bob', 'reason': 'Emphasizes the width of the face'},
                    {'name': 'Center-Parted Blunt Cut', 'reason': 'Can make the face appear wider'}
                ],
                'styling_tips': [
                    'Add volume at the crown to create height',
                    'Use a deep side part for slimming effect',
                    'Avoid tightly pulled-back styles that expose roundness'
                ]
            },
            'square': {
                'explanation': 'Square face shapes feature a prominent, angular jawline with proportional forehead and cheekbone width. '
                               'Soften angular lines with texture, waves, and face-framing layers.',
                'recommendations': [
                    {'name': 'Soft Layered Shag', 'reason': 'Softens strong jawline angles with texture'},
                    {'name': 'Side-Swept Waves', 'reason': 'Diverts focus from sharp jaw angles'},
                    {'name': 'Long Textured Quiff', 'reason': 'Adds height and softens square dimensions'}
                ],
                'styles_to_avoid': [
                    {'name': 'Blunt Straight Bob', 'reason': 'Accentuates jawline boxiness'},
                    {'name': 'Flat Straight Bangs', 'reason': 'Draws attention across the wide forehead'}
                ],
                'styling_tips': [
                    'Incorporate soft, wispy layers around the jaw',
                    'Opt for off-center or side parts to disrupt symmetry',
                    'Use texturizing spray for effortless movement'
                ]
            },
            'heart': {
                'explanation': 'Heart-shaped faces feature a wider forehead tapering to a delicate, pointed chin. '
                               'Balance the narrow jaw by creating width and volume around the neck and chin area.',
                'recommendations': [
                    {'name': 'Chin-Length Textured Bob', 'reason': 'Fills out space around the narrow chin'},
                    {'name': 'Curtain Bangs with Layers', 'reason': 'Softens forehead width while framing the face'},
                    {'name': 'Mid-Length Waves', 'reason': 'Distributes volume evenly across jawline'}
                ],
                'styles_to_avoid': [
                    {'name': 'Top-Heavy Voluminous Crown', 'reason': 'Makes forehead look wider'},
                    {'name': 'Slicked-Back Ponytail', 'reason': 'Exposes forehead and emphasizes chin sharpness'}
                ],
                'styling_tips': [
                    'Keep volume around chin level',
                    'Curtain bangs are exceptionally flattering for heart shapes',
                    'Soft waves help balance proportions'
                ]
            },
            'oblong': {
                'explanation': 'Oblong face shapes are longer than they are wide, with a straight cheekline and long chin. '
                               'Add width and fullness at the sides to balance face length.',
                'recommendations': [
                    {'name': 'Medium Waves with Fringe', 'reason': 'Shortens face visually and adds side volume'},
                    {'name': 'Voluminous Bob', 'reason': 'Creates horizontal width across cheekbones'},
                    {'name': 'Side-Parted Layers', 'reason': 'Breaks vertical lines'}
                ],
                'styles_to_avoid': [
                    {'name': 'Super Long Straight Hair', 'reason': 'Elongates the face further'},
                    {'name': 'High Pompadour', 'reason': 'Adds unnecessary vertical height'}
                ],
                'styling_tips': [
                    'Bangs effectively shorten face length',
                    'Focus volume on sides rather than crown',
                    'Waves and curls build flattering horizontal balance'
                ]
            },
            'diamond': {
                'explanation': 'Diamond face shapes feature high, dramatic cheekbones with a narrow forehead and pointed chin. '
                               'Frame the cheekbones and add fullness at forehead and jaw.',
                'recommendations': [
                    {'name': 'Textured Side-Swept Bob', 'reason': 'Accentuates cheekbones while softening chin'},
                    {'name': 'Full Fringe with Soft Layers', 'reason': 'Widens narrow forehead'},
                    {'name': 'Chin-Length Layers', 'reason': 'Fills out narrow jawline'}
                ],
                'styles_to_avoid': [
                    {'name': 'Severe Flat Center Part', 'reason': 'Draws focus to narrow forehead'},
                    {'name': 'Slick Back Without Volume', 'reason': 'Highlights narrow chin line'}
                ],
                'styling_tips': [
                    'Showcase your high cheekbones with layered frames',
                    'Side parts and fringe balance narrow forehead',
                    'Keep chin-level layers soft and flowing'
                ]
            },
            'triangle': {
                'explanation': 'Triangle face shapes have a wider jawline tapering up to a narrow forehead. '
                               'Add volume at the crown and forehead to create balance.',
                'recommendations': [
                    {'name': 'Voluminous Crop with Layers', 'reason': 'Widens the forehead area'},
                    {'name': 'Full Side Fringe', 'reason': 'Creates width across temple and forehead'},
                    {'name': 'Shaggy Layered Lob', 'reason': 'Draws attention upward from jaw'}
                ],
                'styles_to_avoid': [
                    {'name': 'Chin-Length Heavy Bob', 'reason': 'Adds bulk to wide jawline'},
                    {'name': 'Flat Top Styles', 'reason': 'Exaggerates wide lower face'}
                ],
                'styling_tips': [
                    'Build height and fullness at top and temples',
                    'Layering above chin draws focus upward',
                    'Soft texturizing helps soften jawline boundaries'
                ]
            }
        }

        # Return matching advice or generic
        return advice_db.get(face_shape, {
            'explanation': f'Your {face_shape} face shape has unique characteristics that '
                           f'pair well with specific hairstyles.',
            'recommendations': [
                {'name': 'Consult a Professional', 'reason': 'A stylist can provide personalized advice'}
            ],
            'styles_to_avoid': [
                {'name': 'Extremes', 'reason': 'Very severe or dramatic styles may not flatter'}
            ],
            'styling_tips': [
                'Consider your hair texture and lifestyle when choosing a style',
                'Bring reference photos to your stylist',
                'Start with subtle changes and build from there'
            ]
        })
