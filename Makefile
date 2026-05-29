# ── Stories (Standard Shorts) ──
icg-s-step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1

icg-s-step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2

icg-s-step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3

icg-s-step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4

icg-s-step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5

icg-s-step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6

icg-s-step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7

icg-s-step8:
	poetry run python -m flows.image_content_generator.pipeline.main short step8

icg-s-all:
	poetry run python -m flows.image_content_generator.pipeline.main short all

# ── Geography (3D Map Shorts) ──
icg-g-step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1 --mode geography

icg-g-step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2 --mode geography

icg-g-step2b:
	poetry run python -m flows.image_content_generator.pipeline.main short step2b --mode geography

icg-g-step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3 --mode geography

icg-g-step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4 --mode geography

icg-g-step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5 --mode geography

icg-g-step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6 --mode geography

icg-g-step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7 --mode geography

icg-g-step8:
	poetry run python -m flows.image_content_generator.pipeline.main short step8 --mode geography

icg-g-all:
	poetry run python -m flows.image_content_generator.pipeline.main short all --mode geography

# ── Daily Automation ──
daily-mix:
	poetry run python flows/image_content_generator/pipeline/daily_automated_content.py
