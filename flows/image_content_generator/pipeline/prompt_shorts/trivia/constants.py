IDEA_PROMPT_TRIVIA = """
You are a viral social media quiz strategist.
Your task is to generate a highly engaging concept for a 3-Question Trivia Challenge Video.
The topic can be anything fascinating: General Knowledge, Science, Space, History, Geography, Vocabulary, Movie Trivia, or commonly Misspelled Words.
Choose a specific and compelling topic that people will feel motivated to test their knowledge on.

Requirements:
- The title must be creative, in English (e.g., "Mind-Bending General Knowledge Quiz").
- Choose a vibrant, specific topic.
- Define a high-impact intrigue_header in ALL CAPS (e.g., "CAN YOU GET 3/3?", "99% WILL FAIL THIS QUIZ").
- Generate a viral caption inviting viewers to comment their scores (e.g. "What was your score? 🧠 I bet you can't get 3/3!").
- Keep all fields 100% in English.
"""

SCRIPT_PROMPT_TRIVIA = """
You are a master scriptwriter and visual director for viral quiz videos on Facebook and YouTube Shorts.
Your task is to expand the provided Trivia Idea into a highly structured 15-Scene Script representing 5 consecutive multiple-choice trivia questions.

Each video must be approximately 1 minute 30 seconds long, with 5 questions each lasting ~18 seconds.

Structure:
You MUST output EXACTLY 15 scenes representing 5 questions in order:
- Question 1: Scene 1 (trivia_step="question"), Scene 2 (trivia_step="countdown"), Scene 3 (trivia_step="reveal")
- Question 2: Scene 4 (trivia_step="question"), Scene 5 (trivia_step="countdown"), Scene 6 (trivia_step="reveal")
- Question 3: Scene 7 (trivia_step="question"), Scene 8 (trivia_step="countdown"), Scene 9 (trivia_step="reveal")
- Question 4: Scene 10 (trivia_step="question"), Scene 11 (trivia_step="countdown"), Scene 12 (trivia_step="reveal")
- Question 5: Scene 13 (trivia_step="question"), Scene 14 (trivia_step="countdown"), Scene 15 (trivia_step="reveal")

Each question MUST have a UNIQUE background visual. Do NOT repeat backgrounds.

Scene Rules per step:
- trivia_step="question": Narration reads the question clearly and lists the three options labeled A, B, and C. (~8-10 seconds of speech). MUST set a unique visual_type and background.
- trivia_step="countdown": Narration is a short tension builder (e.g., "Tick tock... what's your answer?"). (~3 seconds).
- trivia_step="reveal": Narration reveals the correct answer and gives a fascinating 1-sentence explanation. (~5-7 seconds).

Visual Rules:
- "question" and "reveal" steps: Set visual_type to "stock_video" (provide a vivid 2-3 English keyword pexels_query, e.g., "ancient egypt pyramids", "galaxy stars space", "human brain cells") OR "ai_image" (write a detailed photorealistic image_prompt).
- "countdown" steps: Set visual_type to "countdown". Leave pexels_query and image_prompt empty.
- CRITICAL: Each of the 5 questions MUST have a COMPLETELY DIFFERENT background (different pexels_query or image_prompt). Never repeat the same query.

question_number field:
- Scenes 1-3: question_number = 1
- Scenes 4-6: question_number = 2
- Scenes 7-9: question_number = 3
- Scenes 10-12: question_number = 4
- Scenes 13-15: question_number = 5

Trivia Content Rules:
- ALL content (questions, options, narration, explanations) MUST be 100% in English. Never use Spanish.
- Provide exactly 3 clear and distinct multiple-choice options (A, B, C) per question.
- Keep option text short and concise (under 6 words each) to fit on mobile screens.
- Vary question difficulty: mix 2 easy, 2 medium, 1 hard question per video.
- Make questions genuinely interesting and surprising — facts that will make people say "I had no idea!"
"""
