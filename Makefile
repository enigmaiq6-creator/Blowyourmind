# ── Pipeline Steps ──
step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1

step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2

step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3

step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4

step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5

step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6

step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7

step8:
	poetry run python -m flows.image_content_generator.pipeline.main short step8

all:
	poetry run python -m flows.image_content_generator.pipeline.main short all

# ── Daily Automation ──
daily-mix:
	poetry run python flows/image_content_generator/pipeline/daily_automated_content.py
